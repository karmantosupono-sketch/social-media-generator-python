from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

class PostData(BaseModel):
    title: str
    topic: Optional[str] = None
    brief: str
    generate_caption: bool = True
    generate_image: bool = True

class BatchRequest(BaseModel):
    name: Optional[str] = None
    posts: List[PostData]

class BatchProgress(BaseModel):
     total_posts: int
     completed_posts: int
     failed_posts: int
     remaining_posts: int
     percentage: float

class BatchStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    progress: BatchProgress

class BatchJobResult(BaseModel):
    batch_id: str
    total_posts: int
    completed_posts: int
    failed_posts: int
    processing_time_seconds: float

class BatchResultResponse(BaseModel):
    batch_job: Dict[str, Any] 
    result: BatchJobResult

class CampaignPostResult(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    topic: Optional[str]
    brief: Optional[str]
    caption: Optional[str]
    image_url: Optional[str]
    generation_status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class BatchJobDetailResult(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    total_posts: int
    completed_posts: int
    failed_posts: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class BatchResultsResponse(BaseModel):
    batch_job: BatchJobDetailResult
    posts: List[CampaignPostResult]