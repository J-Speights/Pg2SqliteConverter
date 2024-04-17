import os
import sqlite3
import subprocess
from config_management import AppConfig

# Define any custom replacements here.
# You may also update the string_replacement function.
CUSTOM_REPLACEMENTS = {
    "inserted_at text NOT NULL": "inserted_at text",
    "updated_at text NOT NULL": "updated_at text",
    "::text": "",
}


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


def backup_postgresql_schema(config: AppConfig) -> int:
    """
    Creates a schema only backup of the Nimble Database.
    Deletes the old copy if one exists.
    """
    host = config.database.host
    port = config.database.port
    user = config.database.user
    password = config.database.password
    database = config.database.name

    output_file = config.file_paths.postgres_backup_file

    exit_code = delete_file(output_file)
    if exit_code:
        return 1

    pg_dump = config.file_paths.pg_dump_path

    if not all([host, port, user, password, database]):
        raise EnvironmentError(
            "Missing environment variable(s). "
            "Make sure your .env file is set up correctly."
        )

    command = [
        pg_dump,
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

    try:
        subprocess.run(command, env=env, check=True)
        print(f"Schema backup of {database} success. Created {output_file}")

        return 0

    except OSError as e:
        print(f"Error handling file: {e}. Is your PG_DUMP_PATH variable set in .env?")
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
    if CUSTOM_REPLACEMENTS:
        custom_replacements = CUSTOM_REPLACEMENTS
        replacements.update(custom_replacements)

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


def convert_schema_from_pg_to_sqlite(config: AppConfig) -> int:
    """
    Reads a schema backup from Postgres and drops anything sqlite does not or cannot use.
    Converts all fields to text fields for simplicity, and writes to FINAL_FILE.
    Deletes the old FINAL_FILE if one exists.
    """
    sqlite_import_file = config.file_paths.sqlite_import_file
    postgres_backup_file = config.file_paths.postgres_backup_file

    # Toss the old file to start
    exit_code = delete_file(sqlite_import_file)
    if exit_code:
        return 1

    if not postgres_backup_file.exists() or postgres_backup_file.stat().st_size == 0:
        print(f"Backup file {postgres_backup_file} missing or empty.")
        return 1

    with open(postgres_backup_file, "r", encoding="utf-8") as file:
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
        with open(sqlite_import_file, "w", encoding="utf-8") as new_file:
            new_file.writelines(lines)
    except OSError as e:
        print(f"Could not write to file {sqlite_import_file}: {e}")

    return 0


def create_database(config: AppConfig) -> int:
    """
    Create a new Sqlite database and apply schema.
    Deletes the existing file if one exists.
    """

    sqlite_db = config.file_paths.sqlite_db
    sqlite_import_file = config.file_paths.sqlite_import_file

    try:
        exit_code = delete_file(sqlite_db)
        if exit_code:
            return 1

        conn = sqlite3.connect(sqlite_db)
        with open(sqlite_import_file, "r", encoding="utf-8") as file:
            schema_sql = file.read()
            print(f"Success creating new sqlite db: {sqlite_db}")

            conn.executescript(schema_sql)
            print(f"Created schema to sqlite db: {sqlite_db}")

            return 0

    except sqlite3.Error as e:
        print(f"Unable to apply new schema: {e}")
        return 1

    finally:
        conn.close()
