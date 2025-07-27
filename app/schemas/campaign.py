from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    brand_name: str
    target_audience: Optional[str] = None
    tone_id: str

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(CampaignBase):
    name: Optional[str] = None
    brand_name: Optional[str] = None
    tone_id: Optional[str] = None

class CampaignResponse(CampaignBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 