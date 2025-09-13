from pydantic import BaseModel, Field
from datetime import datetime


class BalancerConfigBase(BaseModel):
    cdn_host: str = Field(..., description="CDN host URL")
    cdn_ratio: int = Field(..., ge=1, le=100, description="CDN ratio (1-100)")
    origin_ratio: int = Field(..., ge=1, le=100, description="Origin ratio (1-100)")
    is_active: bool = Field(True, description="Whether this config is active")


class BalancerConfigCreate(BalancerConfigBase):
    pass


class BalancerConfigUpdate(BaseModel):
    cdn_host: str | None = Field(None, description="CDN host URL")
    cdn_ratio: int | None = Field(None, ge=1, le=100, description="CDN ratio (1-100)")
    origin_ratio: int | None = Field(
        None, ge=1, le=100, description="Origin ratio (1-100)"
    )
    is_active: bool | None = Field(None, description="Whether this config is active")


class BalancerConfigResponse(BalancerConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class BalancerRequest(BaseModel):
    video: str = Field(..., description="Video URL to balance")


class DelMessageResponse(BaseModel):
    message: str


class BalancerResponse(BaseModel):
    redirect_url: str = Field(..., description="URL to redirect to")
    target: str = Field(..., description="Target type: 'cdn' or 'origin'")
