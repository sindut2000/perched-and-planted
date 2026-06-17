from datetime import datetime

from pydantic import BaseModel


class MetadataEntry(BaseModel):
    key: str
    value: str
    updated_at: datetime


class MetadataSearchResponse(BaseModel):
    prefix: str
    results: list[MetadataEntry]
