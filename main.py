import sys

from schema_formatter.schema_management import (
    backup_postgresql_schema,
    convert_schema_from_pg_to_sqlite,
    create_database,
)

from config_management import load_config_as_class, first_run_setup
from command_line_args import handle_arguments


def main() -> None:
    args = handle_arguments()
    config = load_config_as_class()

    if args.config:
        print("Re-running first time configuration.")
        first_run_setup()

    if config is None:
        print("No configuration file found. Running first time setup.")
        first_run_setup()
        config = load_config_as_class()

    # TODO: Alter database query: this goes to the cloud db.

    exit_code = backup_postgresql_schema(config)
    if not exit_code:
        exit_code = convert_schema_from_pg_to_sqlite(config)
    if not exit_code:
        exit_code = create_database(config)
    # TODO: Upload to S3 bucket (New sqlite db).
    # TODO: Notify dev of change. (Email, Teams.)
    if exit_code:
        sys.exit(exit_code)

    # TODO: write base64 query to the ref_local_db_updates table.
    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
