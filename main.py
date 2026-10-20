"""
Create a SQLite database from a PostgreSQL schema-only backup.

The main workflow backs up the configured PostgreSQL schema, converts it to
SQLite-compatible SQL, and applies that schema to the configured SQLite database.
Use --config to rerun the interactive configuration setup.
"""

import sys

from schema_formatter.schema_management import (
    backup_postgresql_schema,
    convert_schema_from_pg_to_sqlite,
    create_sqlite_database,
)

from config_management import load_config_as_class, first_run_setup
from command_line_args import handle_arguments
from upload import upload_to_s3

from notify import notify_teams


def main() -> int:
    args = handle_arguments()

    if args.config:
        print("Re-running first time configuration.")
        first_run_setup()

    config = load_config_as_class()

    # TODO: Alter database query: this goes to the cloud db.
    # TODO: We'll basically be doing our database edit from here, instead of from pgadmin.
    # TODO: After the commit, we'll continue, and that should give us an up-to-the-minute db.

    exit_code = backup_postgresql_schema(config)
    if not exit_code:
        exit_code = convert_schema_from_pg_to_sqlite(config)
    if not exit_code:
        exit_code = create_sqlite_database(config)

    # if not exit_code:
    #     exit_code, s3_url = upload_to_s3(config)

    # if not exit_code and s3_url:
    #     webhook_url = config.teams_config.webhook_url
    #     exit_code = notify_teams(webhook_url, s3_url)

    if exit_code:
        return exit_code

    return 0


if __name__ == "__main__":
    sys.exit(main())
