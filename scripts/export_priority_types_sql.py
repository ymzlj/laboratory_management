import os
import sys
from pathlib import Path
from datetime import datetime, date
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "laboratory_management.settings")
from django import setup
setup()

from apps.tasks.models import PriorityType

BASE_DIR = Path(__file__).resolve().parents[1]

def esc(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (datetime, date)):
        return "'" + v.strftime("%Y-%m-%d %H:%M:%S") + "'"
    s = str(v)
    s = s.replace("\\", "\\\\").replace("'", "\\'")
    return "'" + s + "'"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-only", action="store_true", help="Only export data, skip CREATE TABLE")
    parser.add_argument("--upsert", action="store_true", help="Use INSERT ... ON DUPLICATE KEY UPDATE")
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument("--no_fk", action="store_true", help="Do not include FOREIGN_KEY_CHECKS statements")
    args = parser.parse_args()

    out_dir = BASE_DIR / "database" / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    default_name = "priority_types_data.sql"
    if args.upsert:
        default_name = "priority_types_upsert.sql"
    
    out_path = Path(args.output) if args.output else (out_dir / default_name)

    header_sql = "SET NAMES utf8mb4;\n"
    if not args.no_fk:
        header_sql += "SET FOREIGN_KEY_CHECKS=0;\n"

    create_sql = ""
    if not args.data_only:
        create_sql = """
DROP TABLE IF EXISTS `priority_types`;
CREATE TABLE `priority_types` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `level` INT NOT NULL,
  `description` LONGTEXT NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `level` (`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""".strip() + "\n"

    rows = []
    for obj in PriorityType.objects.all().order_by('level'):
        row = "(" + ",".join([
            esc(obj.id),
            esc(obj.name),
            esc(obj.level),
            esc(obj.description),
            esc(obj.created_at),
            esc(obj.updated_at),
        ]) + ")"
        rows.append(row)

    cols = "(`id`, `name`, `level`, `description`, `created_at`, `updated_at`)"
    insert_header = f"INSERT INTO `priority_types` {cols} VALUES\n"
    insert_sql = ""
    
    if rows:
        insert_sql = insert_header + ",\n".join(rows) + ";\n"
        if args.upsert:
            # ON DUPLICATE KEY UPDATE
            # If ID or LEVEL matches, we update the other fields.
            # We want to sync the data from this source to target.
            insert_sql = insert_header + ",\n".join(rows) + "\nON DUPLICATE KEY UPDATE " + ",".join([
                "`name`=VALUES(`name`)",
                "`level`=VALUES(`level`)",
                "`description`=VALUES(`description`)",
                "`updated_at`=VALUES(`updated_at`)",
                # We can optionally update created_at or id, but usually id is the key.
                # If 'level' caused the conflict, we might want to update that row.
                # But 'level' is also being set by VALUES(`level`).
            ]) + ";\n"

    footer_sql = ""
    if not args.no_fk:
        footer_sql = "SET FOREIGN_KEY_CHECKS=1;\n"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header_sql)
        if create_sql:
            f.write(create_sql)
        if insert_sql:
            f.write(insert_sql)
        f.write(footer_sql)

    print(f"Exported to {out_path}")

if __name__ == "__main__":
    main()
