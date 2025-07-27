from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class CampaignPost(Base):
    __tablename__ = "campaign_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    batch_job_id = Column(UUID(as_uuid=True), ForeignKey('batch_jobs.id', ondelete='SET NULL'), nullable=True) 
    title = Column(String(255))
    topic = Column(String(255))
    brief = Column(Text)
    caption = Column(Text)
    image_url = Column(String(500))
    generation_status = Column(String(20), default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign", back_populates="posts")
    batch_job = relationship("BatchJob", back_populates="posts")