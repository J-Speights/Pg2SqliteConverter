"""
This creates the Assets db file used for nimble.
Unnecessary for full project.  Should be removed from main branch of repo.
"""

import sqlite3

from schema_formatter.schema_management import delete_file
from pathlib import Path

OUTPUT_DIR = Path("db_files")
ASSET_DB_FILENAME = OUTPUT_DIR / "assets_database.db3"
ASSET_DB_FILE = OUTPUT_DIR / "assets_database.sql"


def create_assets_db():
    """
    Create a new Sqlite database and apply schema.
    Deletes the existing file if one exists.
    """
    try:
        exit_code = delete_file(ASSET_DB_FILENAME)
        if exit_code:
            return 1

        conn = sqlite3.connect(ASSET_DB_FILENAME)
        with open(ASSET_DB_FILE, "r", encoding="utf-8") as file:
            schema_sql = file.read()
            print(f"Success creating new sqlite db: {ASSET_DB_FILENAME}")

            conn.executescript(schema_sql)
            print(f"Created schema to sqlite db: {ASSET_DB_FILENAME}")

            return 0

    except sqlite3.Error as e:
        print(f"Unable to apply new schema: {e}")
        return 1

    finally:
        conn.close()


if __name__ == "__main__":
    create_assets_db()
