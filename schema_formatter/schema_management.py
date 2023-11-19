import os
import sqlite3
import subprocess
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

OUTPUT_DIR = Path("db_files")
POSTGRESQL_BACKUP_FILE = OUTPUT_DIR / "export_schema.sql"
FINAL_FILE = OUTPUT_DIR / "sqlite_ready_schema.sql"
SQLITE_DB_FILENAME = OUTPUT_DIR / "nimble.db3"


def delete_file(file_name: str) -> int:
    """Deletes file_name using os.remove."""
    try:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Deleted {file_name}")
            return 0

    except OSError as e:
        print(f"Error deleting file: {e}")
        return 1

    return 0


def backup_postgresql_schema() -> int:
    """
    Creates a schema only backup of the Nimble Database.
    Deletes the old copy if one exists.
    """
    exit_code = delete_file(POSTGRESQL_BACKUP_FILE)
    if exit_code:
        return 1

    try:
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASS")
        database = os.getenv("DB_NAME")
        output_file = POSTGRESQL_BACKUP_FILE

        if not all([host, port, user, password, database]):
            raise EnvironmentError(
                "Missing environment variable(s). "
                "Make sure your .env file is set up correctly."
            )

        command = [
            "pg_dump",
            "-h",
            host,
            "-p",
            str(port),
            "-U",
            user,
            "-d",
            database,
            "--schema-only",
            "-f",
            output_file,
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = password

        subprocess.run(command, env=env, check=True)
        print(f"Schema backup of {database} success. Created {output_file}")

        return 0

    except OSError as e:
        print(f"Error handling file: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return 1


def string_replacement(line: str) -> str:
    """
    Replaces Postgresql only strings with Sqlite friendly strings.
    Generally replaces Postgresql types with text.
    Replaces most other special cases with ""
    Add any other cases to the replacements dict.

    NOTE: The order of the replacements dict is very important!
    It replaces top to bottom, in order. So uuid[] has to be above uuid, etc.
    """
    replacements = {
        "DEFAULT public.uuid_generate_v4()": "",
        "DEFAULT 0": "",
        "uuid[]": "text",
        "text[]": "text",
        "jsonb[]": "text",
        "public.": "",
        "uuid": "text",
        "timestamp without time zone": "text",
        "numeric": "text",
        "boolean": "text",
        "integer": "text",
        "jsonb": "text",
    }
    for old, new in replacements.items():
        line = line.replace(old, new)

    return line


def fix_primary_key(line: str) -> str:
    """
    We need to define our PRIMARY KEYs in line.
    Every table in my database has an id primary key, so we're going to count on that.
    """
    old_and_busted = "id text NOT NULL"
    old_and_really_busted = "id text  NOT NULL"
    new_hotness = "id text PRIMARY KEY"

    if line.lstrip().startswith(old_and_busted):
        line = line.replace(old_and_busted, new_hotness)
    if line.lstrip().startswith(old_and_really_busted):
        line = line.replace(old_and_really_busted, new_hotness)
    return line


def convert_schema_from_pg_to_sqlite() -> int:
    """
    Reads a schema backup from Postgres and drops anything sqlite does not or cannot use.
    Converts all fields to text fields for simplicity, and writes to FINAL_FILE.
    Deletes the old FINAL_FILE if one exists.
    """
    # Toss the old file to start
    exit_code = delete_file(FINAL_FILE)
    if exit_code:
        return 1

    if (
        not POSTGRESQL_BACKUP_FILE.exists()
        or POSTGRESQL_BACKUP_FILE.stat().st_size == 0
    ):
        print(f"Backup file {POSTGRESQL_BACKUP_FILE} missing or empty.")
        return 1

    with open(POSTGRESQL_BACKUP_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Finds the first CREATE TABLE
    try:
        first_create_index = next(
            i
            for i, line in enumerate(lines)
            if line.lstrip().startswith("CREATE TABLE")
        )
    except StopIteration:  # No Creates for some reason
        first_create_index = None

    # Throws out everything before the first CREATE TABLE, Sqlite can't use it.
    if first_create_index is not None:
        lines = lines[first_create_index:]

    # Strip out all comments
    lines = [line for line in lines if not line.lstrip().startswith("--")]

    # Strip out all ALTER TABLEs, This gets rid of change OWNER lines.
    lines = [line for line in lines if not line.lstrip().startswith("ALTER TABLE")]

    # Find the start of the last CREATE statement
    last_create_index = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("CREATE TABLE") or line.lstrip().startswith(
            "CREATE VIEW"
        ):
            last_create_index = i

    # Find the end of the last CREATE statement
    end_of_last_create_index = None
    if last_create_index is not None:
        for i in range(last_create_index, len(lines)):
            if ";" in lines[i]:
                end_of_last_create_index = i
                break

    # Throw away all of the lines after CREATE statements, SQLite doesn't use them.
    if end_of_last_create_index is not None:
        lines = lines[: end_of_last_create_index + 1]

    # Handle all additional string replacement work, defined in string_replacement
    lines = [string_replacement(line) for line in lines]

    lines = [fix_primary_key(line) for line in lines]
    try:
        with open(FINAL_FILE, "w", encoding="utf-8") as new_file:
            new_file.writelines(lines)
    except OSError as e:
        print(f"Could not write to file {FINAL_FILE}: {e}")

    return 0


def create_database() -> int:
    """
    Create a new Sqlite database and apply schema.
    Deletes the existing file if one exists.
    """
    try:
        exit_code = delete_file(SQLITE_DB_FILENAME)
        if exit_code:
            return 1

        conn = sqlite3.connect(SQLITE_DB_FILENAME)
        with open(FINAL_FILE, "r", encoding="utf-8") as file:
            schema_sql = file.read()
            print(f"Success creating new sqlite db: {SQLITE_DB_FILENAME}")

            conn.executescript(schema_sql)
            print(f"Created schema to sqlite db: {SQLITE_DB_FILENAME}")

            return 0

    except sqlite3.Error as e:
        print(f"Unable to apply new schema: {e}")
        return 1

    finally:
        conn.close()
