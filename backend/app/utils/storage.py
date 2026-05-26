import os
import uuid
import boto3
from botocore.exceptions import ClientError

class StorageService:
    def __init__(self):
        # We default to False if we don't have the MINIO configuration set 
        # yet in the .env, but for now we can enable it by default.
        self.use_s3 = os.getenv("USE_S3", "True").lower() in ("true", "1", "yes")
        
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "agridesk-uploads")
        # In a real environment, this should point to actual AWS S3 URL
        # For local development, it points to the MinIO container
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
        self.aws_access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
        self.aws_secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
        self.region = os.getenv("S3_REGION", "us-east-1")
        
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region,
            )
        else:
            self.local_upload_dir = "uploads"
            os.makedirs(self.local_upload_dir, exist_ok=True)

    def upload_file(self, file_content: bytes, original_filename: str) -> str:
        """Uploads a file to S3 (or local fallback) and returns the key/path."""
        ext = original_filename.split('.')[-1] if '.' in original_filename else 'pdf'
        filename = f"{uuid.uuid4().hex}.{ext}"

        if self.use_s3:
            try:
                content_type = "application/pdf"
                if ext.lower() in ["png", "jpg", "jpeg"]:
                    content_type = f"image/{ext.lower().replace('jpg', 'jpeg')}"

                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=file_content,
                    ContentType=content_type,
                )
                return filename
            except ClientError as e:
                print(f"S3 Upload failed: {e}")
                # Fallback
                return self._upload_local(file_content, filename)
            except Exception as e:
                print(f"Unknown upload exception: {e}")
                return self._upload_local(file_content, filename)
        else:
            return self._upload_local(file_content, filename)
            
    def _upload_local(self, file_content: bytes, filename: str) -> str:
        self.local_upload_dir = "uploads"
        os.makedirs(self.local_upload_dir, exist_ok=True)
        filepath = os.path.join(self.local_upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(file_content)
        return filepath
        
    def get_file_content(self, path_or_key: str) -> bytes:
        """Retrieves file content from S3 or local."""
        # If it has a slash and not from uploads, check if it's a legacy local file
        if self.use_s3 and not path_or_key.startswith("uploads/") and "/" not in path_or_key:
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=path_or_key)
                return response['Body'].read()
            except ClientError as e:
                print(f"S3 Download failed: {e}")
                
        # Local fallback
        filepath = path_or_key if path_or_key.startswith("uploads") else os.path.join("uploads", path_or_key)
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return f.read()
        
        raise FileNotFoundError(f"File not found in storage: {path_or_key}")

storage_service = StorageService()
