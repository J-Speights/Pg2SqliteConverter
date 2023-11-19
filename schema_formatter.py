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


def backup_postgresql_schema():
    """
    Creates a schema only backup of the Nimble Database.
    Deletes the old copy if one exists.
    """
    if os.path.exists(POSTGRESQL_BACKUP_FILE):
        os.remove(POSTGRESQL_BACKUP_FILE)
        print(f"Deleted {POSTGRESQL_BACKUP_FILE}")

    try:
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASS")
        database = os.getenv("DB_NAME")
        output_file = POSTGRESQL_BACKUP_FILE

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

    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}")

    return


def string_replacement(line: str):
    """
    Handles various string replacements during conversion.
    """
    replacements = {
        "DEFAULT public.uuid_generate_v4()": "",
        "DEFAULT 0": "",
        "uuid[]": "text",
        "text[]": "text",
        "jsonb[]": "text",
        "public.": "",
        "uuid": " text",
        "timestamp without time zone": "text",
        "numeric": "text",
        "boolean": "text",
        "integer": "text",
        "jsonb": "text",
    }
    for old, new in replacements.items():
        line = line.replace(old, new)

    return line


def fix_primary_key(line: str):
    """
    We need to define our PRIMARY KEYs in line.
    """
    old_and_busted = "id  text NOT NULL"
    new_hotness = "id text PRIMARY KEY"
    if line.lstrip().startswith(old_and_busted):
        line = line.replace(old_and_busted, new_hotness)
    return line


def convert_schema_from_pg_to_sqlite():
    """
    Reads a schema backup from Postgres and drops anything sqlite does not or cannot use.
    Converts all fields to text fields for simplicity, and writes to FINAL_FILE.
    Deletes the old FINAL_FILE if one exists.
    """
    # Toss the old file to start
    if os.path.exists(FINAL_FILE):
        os.remove(FINAL_FILE)
        print(f"Deleted {FINAL_FILE}")

    with open(POSTGRESQL_BACKUP_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Finds the first CREATE TABLE
    try:
        index = next(
            i
            for i, line in enumerate(lines)
            if line.lstrip().startswith("CREATE TABLE")
        )
    except StopIteration:  # No Creates for some reason
        index = None

    # Throws out everything before the first CREATE TABLE, SQLite can't use it.
    if index is not None:
        lines = lines[index:]

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

    with open(FINAL_FILE, "w", encoding="utf-8") as new_file:
        new_file.writelines(lines)

    return


def create_database():
    """
    Create a new SQLite Database and apply schema.
    Deletes the existing file if one exists.
    """
    if os.path.exists(SQLITE_DB_FILENAME):
        os.remove(SQLITE_DB_FILENAME)
        print(f"Dropped old sqlite db {SQLITE_DB_FILENAME}")

    conn = sqlite3.connect(SQLITE_DB_FILENAME)
    with open(FINAL_FILE, "r", encoding="utf-8") as file:
        schema_sql = file.read()
        print(f"Success creating sqlite db: {SQLITE_DB_FILENAME}")

    try:
        conn.executescript(schema_sql)
        print(f"Created schema to sqlite db: {SQLITE_DB_FILENAME}")
    except sqlite3.Error as e:
        print(f"Unable to apply new schema: {e}")
    finally:
        conn.close()

    return


def main():
    backup_postgresql_schema()
    convert_schema_from_pg_to_sqlite()
    create_database()


if __name__ == "__main__":
    main()
