import boto3
from botocore.config import Config

from backend.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket_exists():
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.S3_BUCKET)
    except Exception:
        client.create_bucket(Bucket=settings.S3_BUCKET)


def upload_file(key: str, data: bytes, content_type: str) -> str:
    client = get_s3_client()
    client.put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{key}"
