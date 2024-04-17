import argparse


def handle_arguments():
    """
    Handles command line arguments.
    Possible Args:
        -c, --config: Re-run first time configuration.
    """
    parser = argparse.ArgumentParser(description="Sync database schema.")
    parser.add_argument(
        "-c", "--config", action="store_true", help="Re-run first time configuration."
    )
    args = parser.parse_args()

    return args
