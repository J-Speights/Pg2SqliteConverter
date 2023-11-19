import sys

from schema_formatter.worker_functions import (
    backup_postgresql_schema,
    convert_schema_from_pg_to_sqlite,
    create_database,
)


def main() -> None:
    exit_code = backup_postgresql_schema()
    if not exit_code:
        exit_code = convert_schema_from_pg_to_sqlite()
    if not exit_code:
        exit_code = create_database()
    if exit_code:
        sys.exit(exit_code)

    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
