"""
NOTE: Custom replacements are currently defined in the schema_management file.
Edit the CUSTOM_REPLACEMENTS dictionary to add or remove custom replacements.

The TODOs in the main function are largely Nimble project specific. 
They sync the cloud database, the local api database, and the station DBs automatically.
TODO: clean this up in the main branch.
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
        exit_code = create_sqlite_database(config)

    if not exit_code:
        exit_code, s3_url = upload_to_s3(config)

    if not exit_code and s3_url:
        webhook_url = config.teams_config.webhook_url
        exit_code = notify_teams(webhook_url, s3_url)

    if exit_code:
        sys.exit(exit_code)

    # TODO: write base64 query to the ref_local_db_updates table.
    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
