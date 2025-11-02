# aws_client.py
import os
from dotenv import load_dotenv
import boto3
from botocore.config import Config

load_dotenv()

DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# A small centralized function to create boto3 clients with sensible defaults
def get_client(service: str, region: str = None, **kwargs):
    region = region or DEFAULT_REGION
    config = Config(
        retries={"max_attempts": 5, "mode": "standard"},
        connect_timeout=10,
        read_timeout=60,
    )

    return boto3.client(
        service,
        region_name=region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        config=config,
        **kwargs,
    )
