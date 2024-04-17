import os
import toml

from classes import AppConfig, DatabaseConfig, FilePathConfig


def load_config_as_class():
    DATABASE = "database"
    FILEPATH_CONFIG = "file_paths"

    config_dict = load_config()
    if not config_dict:
        return None
    database_config = DatabaseConfig(**config_dict[DATABASE])
    filepath_config = FilePathConfig(**config_dict[FILEPATH_CONFIG])
    return AppConfig(database=database_config, file_paths=filepath_config)


def load_config():
    if not os.path.exists("config.toml"):
        return None
    with open("config.toml") as file:
        config = toml.load(file)
        return config


def save_config(config):
    with open("config.toml", "w") as file:
        toml.dump(config, file)
    return


def first_run_setup():
    config = {"database": {}, "file_paths": {}}
    config["database"]["name"] = input("Enter the database name: \n")
    config["database"]["host"] = input("Enter the database host: \n")
    config["database"]["port"] = input("Enter the database port: \n")
    config["database"]["user"] = input("Enter the database user: \n")
    config["database"]["password"] = input("Enter the database password: \n")
    config["file_paths"]["pg_dump_path"] = input(
        "Enter the path to pg_dump (e.g. /usr/bin/pg_dump or C:/Program Files/PostgreSQL/13/bin/pg_dump.exe): \n"
    )
    config["file_paths"]["output_dir"] = input(
        "Enter the path to the output directory: (e.g. db_files or C:/Users/username/Documents/db_files/) \n"
    )
    config["file_paths"]["sqlite_import_file"] = "sqlite_ready_schema.sql"
    config["file_paths"]["postgres_backup_file"] = "postgres_backup.sql"
    config["file_paths"]["sqlite_db"] = "nimble.db3"
    save_config(config)
    return
