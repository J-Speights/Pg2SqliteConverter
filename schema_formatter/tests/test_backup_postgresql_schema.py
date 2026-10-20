from pathlib import Path

import pytest
from classes import AppConfig, DatabaseConfig, FilePathConfig, S3Config, TeamsConfig
from schema_formatter.schema_management import backup_postgresql_schema


def test_missing_database_config_raises_error(tmp_path: Path):
    config = AppConfig(
        database=DatabaseConfig(name="", host="", port=0, user="", password=""),
        file_paths=FilePathConfig(
            output_dir=tmp_path,
            pg_dump_path=Path("pg_dump"),
            postgres_backup_file=Path("postgres_backup.sql"),
            sqlite_import_file=Path("sqlite_ready_schema.sql"),
            sqlite_db=Path("database.db"),
        ),
        s3_config=S3Config(
            bucket_name="",
            s3_key="",
            aws_access_key_id="",
            aws_secret_access_key="",
            region_name="",
        ),
        teams_config=TeamsConfig(webhook_url=""),
    )

    with pytest.raises(EnvironmentError, match="Missing configuration"):
        backup_postgresql_schema(config)


def test_subprocess():  # Not sure how to test this yet.
    pass
