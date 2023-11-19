# Pg2SqliteConverter

Description
This repository contains a Python script designed to back up a PostgreSQL database schema, convert it to an SQLite-compatible format, and then create an SQLite database using the converted schema. It is ideal for transitioning data between PostgreSQL and SQLite environments.

## Description

This repository contains a Python script designed to back up a PostgreSQL database schema, convert it to an SQLite-compatible format, and then create an SQLite database using the converted schema. It is ideal for transitioning data between PostgreSQL and SQLite environments.

## System Requirements

- Python 3.x
- PostgreSQL (including `pg_dump` utility)
- SQLite

## Setup

1. **Clone the Repository**: Clone this repository to your local machine.
2. **Install Python**: Ensure you have Python 3.x installed.
3. **Install PostgreSQL**: Ensure PostgreSQL is installed and `pg_dump` is available in your system's PATH.
4. **Install SQLite**: Make sure SQLite is installed on your system.
5. **Create a Virtual Environment** (Optional but recommended):
   - Run `python -m venv venv` to create a virtual environment.
   - Activate the virtual environment:
     - On Windows: `venv\Scripts\activate`
     - On macOS and Linux: `source venv/bin/activate`
6. **Install Dependencies**: Install the required Python packages using `pip install -r requirements.txt`.

## Environment Setup

Create a `.env` file in the root directory with the following variables:

- `DB_HOST`: Your PostgreSQL database host.
- `DB_PORT`: Your PostgreSQL database port.
- `DB_USER`: Your PostgreSQL database user.
- `DB_PASS`: Your PostgreSQL database password.
- `DB_NAME`: Your PostgreSQL database name.

## Usage

1. Ensure all prerequisites are met and the environment variables are set in the `.env` file.
2. Run the script using `python <script_name>.py`.
3. The script will perform the following actions:
   - Back up the PostgreSQL schema.
   - Convert the schema to an SQLite-friendly format.
   - Create a new SQLite database using the converted schema.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License

[Specify the license or state if it's open for public use]
