import sys

from schema_formatter.schema_management import (
    backup_postgresql_schema,
    convert_schema_from_pg_to_sqlite,
    create_database,
)


def main() -> None:
    # TODO: Alter database query: this goes to the cloud db.
    exit_code = backup_postgresql_schema()
    if not exit_code:
        exit_code = convert_schema_from_pg_to_sqlite()
    if not exit_code:
        exit_code = create_database()
    # TODO: Upload to S3 bucket (New sqlite db).
    # TODO: Notify dev of change. (Email, Teams.)
    if exit_code:
        sys.exit(exit_code)

    # TODO: write base64 query to the ref_local_db_updates table.
    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
