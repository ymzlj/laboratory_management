import argparse
import subprocess
import sys
from pathlib import Path
from getpass import getpass
import tempfile

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", default=None)
    parser.add_argument("--database", required=True)
    parser.add_argument("--sql", required=True)
    parser.add_argument("--client", choices=["mysql", "mariadb"], default="mysql")
    parser.add_argument("--secure-auth", action="store_true", help="Use defaults-extra-file to avoid CLI password warning")
    args = parser.parse_args()

    sql_path = Path(args.sql)
    if not sql_path.exists():
        print(f"SQL file not found: {sql_path}")
        sys.exit(1)

    password = args.password or getpass("Password: ")
    with sql_path.open("r", encoding="utf-8") as f:
        sql_text = f.read()

    bin_name = "mysql" if args.client == "mysql" else "mariadb"
    cmd = [bin_name]
    tf = None
    if args.secure_auth:
        tf = tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8")
        tf.write("[client]\n")
        tf.write(f"host={args.host}\n")
        tf.write(f"port={args.port}\n")
        tf.write(f"user={args.user}\n")
        tf.write(f"password={password}\n")
        tf.flush()
        tf.close()
        help_out = subprocess.run([bin_name, "--help"], capture_output=True, text=True)
        supports_extra = "--defaults-extra-file" in (help_out.stdout or "") or "--defaults-extra-file" in (help_out.stderr or "")
        supports_file = "--defaults-file" in (help_out.stdout or "") or "--defaults-file" in (help_out.stderr or "")
        if supports_extra:
            cmd.extend(["--defaults-extra-file", tf.name])
        elif supports_file:
            cmd.extend(["--defaults-file", tf.name])
        else:
            cmd.extend(["-h", args.host, "-P", str(args.port), "-u", args.user, f"-p{password}"])
    else:
        cmd.extend(["-h", args.host, "-P", str(args.port), "-u", args.user, f"-p{password}"])
    cmd.append(args.database)
    proc = subprocess.run(cmd, input=sql_text, text=True, capture_output=True)
    if tf:
        try:
            Path(tf.name).unlink(missing_ok=True)
        except Exception:
            pass
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
