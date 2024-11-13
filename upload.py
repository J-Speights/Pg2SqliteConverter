import boto3
from classes import AppConfig
from typing import Optional
from datetime import datetime


def upload_to_s3(config: AppConfig) -> tuple[int, Optional[str]]:
    """
    Uploads a file to an S3 bucket.

    Args:
        config (AppConfig): The configuration object.

    Returns:
        int: exit code. 0 if successful, 1 if not.
        str: The URL of the uploaded file.
    """
    file_path = config.file_paths.sqlite_db
    bucket_name = config.s3_config.bucket_name
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    s3_key = f"{config.s3_config.s3_key}_{timestamp}.db3"

    aws_access_key_id = config.s3_config.aws_access_key_id
    aws_secret_access_key = config.s3_config.aws_secret_access_key
    region_name = config.s3_config.region_name

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )
    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"File uploaded successful: {file_path} to {bucket_name}/{s3_key}")
        return 0, f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return 1, None
