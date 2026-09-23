from pydantic import BaseModel, Field


class ExternalPdfUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str
    size: int = Field(gt=0, le=10 * 1024 * 1024)


class SignedUploadResponse(BaseModel):
    object_key: str
    upload_url: str
