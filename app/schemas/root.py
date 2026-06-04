from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    app: str
    version: str
    docs_url: str = Field(default="/docs")
    health_url: str = Field(default="/health")
