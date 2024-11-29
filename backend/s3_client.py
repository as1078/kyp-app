from config import settings
import boto3


class S3Client:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        self.S3_BUCKET_NAME='current-events-tracker'
    def __getattr__(self, name):
        return getattr(self.client, name)