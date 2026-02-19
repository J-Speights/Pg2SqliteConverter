from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatabaseConfig:
    name: str
    host: str
    port: int
    user: str
    password: str


@dataclass
class FilePathConfig:
    output_dir: Path
    pg_dump_path: Path
    postgres_backup_file: Path
    sqlite_import_file: Path
    sqlite_db: Path

    def __post_init__(self):
        if not isinstance(self.output_dir, Path):
            self.output_dir: Path = Path(self.output_dir)

        self.postgres_backup_file = self.output_dir / self.postgres_backup_file
        self.sqlite_import_file = self.output_dir / self.sqlite_import_file
        self.sqlite_db = self.output_dir / self.sqlite_db


@dataclass
class S3Config:
    bucket_name: str
    s3_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str


@dataclass
class TeamsConfig:
    webhook_url: str


@dataclass
class AppConfig:
    database: DatabaseConfig
    file_paths: FilePathConfig
    s3_config: S3Config
    teams_config: TeamsConfig
