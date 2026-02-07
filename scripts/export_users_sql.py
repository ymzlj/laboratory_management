import os
import sys
from pathlib import Path
from datetime import datetime, date
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "laboratory_management.settings")
from django import setup
setup()

from apps.users.models import User

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
  parser.add_argument("--data-only", action="store_true")
  parser.add_argument("--upsert", action="store_true")
  parser.add_argument("--output", default=None)
  parser.add_argument("--no_fk", action="store_true")
  args = parser.parse_args()

  out_dir = BASE_DIR / "database" / "exports"
  out_dir.mkdir(parents=True, exist_ok=True)
  default_name = "user_data.sql" if not args.data_only else ("user_data_data_only.sql" if not args.upsert else "user_data_upsert.sql")
  out_path = Path(args.output) if args.output else (out_dir / default_name)

  header_sql = "SET NAMES utf8mb4;\n"
  if not args.no_fk:
    header_sql += "SET FOREIGN_KEY_CHECKS=0;\n"

  create_sql = ""
  if not args.data_only:
    create_sql = """
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `password` VARCHAR(128) NOT NULL,
  `last_login` DATETIME NULL,
  `is_superuser` TINYINT(1) NOT NULL DEFAULT 0,
  `username` VARCHAR(150) NOT NULL,
  `email` VARCHAR(254) NOT NULL,
  `is_staff` TINYINT(1) NOT NULL DEFAULT 0,
  `date_joined` DATETIME NOT NULL,
  `employee_id` VARCHAR(20) NOT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `position` VARCHAR(100) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  `department_id` BIGINT NULL,
  `role` VARCHAR(20) NOT NULL,
  `account_status` TINYINT(1) NOT NULL DEFAULT 1,
  `first_name` VARCHAR(150) NOT NULL,
  `last_name` VARCHAR(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_users_username_unique` (`username`),
  UNIQUE KEY `idx_users_employee_id_unique` (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""".strip() + "\n"

  rows = []
  for u in User.objects.all():
    row = "(" + ",".join([
      esc(u.id),
      esc(u.password),
      esc(u.last_login),
      "1" if u.is_superuser else "0",
      esc(u.username),
      esc(u.email),
      "1" if u.is_staff else "0",
      esc(u.date_joined),
      esc(u.employee_id),
      esc(u.phone),
      esc(u.position),
      esc(u.created_at),
      esc(u.updated_at),
      esc(getattr(u, "department_id", None)),
      esc(getattr(u, "role", "")),
      "1" if getattr(u, "account_status", True) else "0",
      esc(getattr(u, "first_name", "")),
      esc(getattr(u, "last_name", "")),
    ]) + ")"
    rows.append(row)

  cols = "(`id`,`password`,`last_login`,`is_superuser`,`username`,`email`,`is_staff`,`date_joined`,`employee_id`,`phone`,`position`,`created_at`,`updated_at`,`department_id`,`role`,`account_status`,`first_name`,`last_name`)"
  insert_header = f"INSERT INTO `users` {cols} VALUES\n"
  insert_sql = ""
  if rows:
    insert_sql = insert_header + ",\n".join(rows) + ";\n"
    if args.upsert:
      insert_sql = insert_header + ",\n".join(rows) + "\nON DUPLICATE KEY UPDATE " + ",".join([
        "`password`=VALUES(`password`)",
        "`last_login`=VALUES(`last_login`)",
        "`is_superuser`=VALUES(`is_superuser`)",
        "`email`=VALUES(`email`)",
        "`is_staff`=VALUES(`is_staff`)",
        "`date_joined`=VALUES(`date_joined`)",
        "`phone`=VALUES(`phone`)",
        "`position`=VALUES(`position`)",
        "`updated_at`=VALUES(`updated_at`)",
        "`department_id`=VALUES(`department_id`)",
        "`role`=VALUES(`role`)",
        "`account_status`=VALUES(`account_status`)",
        "`first_name`=VALUES(`first_name`)",
        "`last_name`=VALUES(`last_name`)"
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

  print(str(out_path))

if __name__ == "__main__":
  main()
