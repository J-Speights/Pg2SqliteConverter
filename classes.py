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
    output_dir: str
    pg_dump_path: str
    postgres_backup_file: str
    sqlite_import_file: str
    sqlite_db: str

    def __post_init__(self):
        if not isinstance(self.output_dir, Path):
            self.output_dir: Path = Path(self.output_dir)

        self.postgres_backup_file: Path = self.output_dir / self.postgres_backup_file
        self.sqlite_import_file: Path = self.output_dir / self.sqlite_import_file
        self.sqlite_db: Path = self.output_dir / self.sqlite_db


@dataclass
class AppConfig:
    database: DatabaseConfig
    file_paths: FilePathConfig
