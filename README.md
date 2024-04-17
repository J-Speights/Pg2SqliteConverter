# Pg2SqliteConverter

Description
This repository contains a Python script designed to back up a PostgreSQL database schema, convert it to an SQLite-compatible format, and then create an SQLite database using the converted schema. It is ideal for transitioning data between PostgreSQL and SQLite environments.

## Description

This repository contains a Python script designed to back up a PostgreSQL database schema, convert it to an SQLite-compatible format, and then create an SQLite database using the converted schema. It is ideal for transitioning data between PostgreSQL and SQLite environments.

## System Requirements

- Python 3.x (Built on 3.10.6)
- PostgreSQL (including `pg_dump` utility)
- SQLite

## Setup

1. **Clone the Repository**: Clone this repository to your local machine.
2. **Install Python**: Ensure you have Python 3.x installed.
3. **Install PostgreSQL**: Ensure PostgreSQL is installed and `pg_dump` is available in your system's PATH.
4. **Install SQLite**: Make sure SQLite is installed on your system.
   - The SQLite folder should also be on PATH to be recognized.
5. **Create a Virtual Environment** (Optional but recommended):
   - Run `python -m venv venv` to create a virtual environment.
   - Activate the virtual environment:
     - On Windows: `venv\Scripts\activate`
     - On macOS and Linux: `source venv/bin/activate`
6. **Install Dependencies**: Install the required Python packages using `pip install -r requirements.txt`.

## Usage

1. Ensure all prerequisites are met and the environment variables are set in the `.env` file.
2. Run the script using `python {path_to_file}\main.py`.
3. Run first time config. This will create a TOML file for future runs.
4. The script will perform the following actions:
   - Back up the PostgreSQL schema.
   - Convert the schema to an SQLite-friendly format.
   - Create a new SQLite database using the converted schema.

## Notes

You can re-run the configuration at any time by running the file with the -c or --config arguments.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License

[Specify the license or state if it's open for public use]
