import os
import toml

from classes import AppConfig, DatabaseConfig, FilePathConfig, S3Config, TeamsConfig


def load_str_replacements() -> dict:
    """
    Loads string replacements from a config file.
    """
    replacements = toml.load("replacements.toml")
    standard_replacements = replacements.get("standard_replacements", {})
    custom_replacements = replacements.get("custom_replacements", {})
    return {**standard_replacements, **custom_replacements}


def load_config() -> dict[str, dict]:
    """
    Retrieves data from the config.toml file.
    """
    if not os.path.exists("config.toml"):
        return {}
    with open("config.toml") as file:
        config = toml.load(file)
        return config


def load_config_as_class() -> AppConfig:
    """
    Loads the config file into AppConfig class.
    """
    DATABASE = "database"
    FILEPATH_CONFIG = "file_paths"
    AWS_CONFIG = "s3_config"
    TEAMS_CONFIG = "teams_config"

    def has_required_keys(config: dict) -> bool:
        return all(
            key in config
            for key in [DATABASE, FILEPATH_CONFIG, AWS_CONFIG, TEAMS_CONFIG]
        )

    config_dict = load_config()
    if not has_required_keys(config_dict):
        print("No configuration file found. Running first time setup.")
        first_run_setup()
        config_dict = load_config()

        if not has_required_keys(config_dict):
            raise RuntimeError(
                "First time setup failed. Please check your configuration."
            )

    database_config = DatabaseConfig(**config_dict[DATABASE])
    filepath_config = FilePathConfig(**config_dict[FILEPATH_CONFIG])
    aws_config = S3Config(**config_dict[AWS_CONFIG])
    teams_config = TeamsConfig(**config_dict[TEAMS_CONFIG])
    return AppConfig(
        database=database_config,
        file_paths=filepath_config,
        s3_config=aws_config,
        teams_config=teams_config,
    )


def save_config(config) -> None:
    """
    Saves the configuration to the config.toml file.
    """
    with open("config.toml", "w") as file:
        toml.dump(config, file)
    return


def first_run_setup() -> None:
    """
    Walks the user through first time setup.
    Saves the configuration to the config.toml file.
    """
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

    config["s3_config"]["bucket_name"] = input("Enter the S3 bucket name: \n")
    config["s3_config"]["s3_key"] = input(
        "Enter the S3 key (This is the base filename for your uploaded file.): \n"
    )
    config["s3_config"]["aws_access_key_id"] = input("Enter the AWS Access Key ID: \n")

    config["s3_config"]["aws_secret_access_key"] = input(
        "Enter the AWS Secret Access Key: \n"
    )
    config["s3_config"]["region_name"] = input("Enter the AWS region name: \n")

    config["teams_config"]["webhook_url"] = input("Enter the Teams webhook URL: \n")
    save_config(config)
    return
