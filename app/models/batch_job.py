from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=True)
    name = Column(String(255), nullable=False)
    total_posts = Column(Integer, default=0, nullable=False)
    completed_posts = Column(Integer, default=0, nullable=False)
    failed_posts = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default='pending')
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="batch_jobs")
    campaign = relationship("Campaign", back_populates="batch_jobs") 
    posts = relationship("CampaignPost", back_populates="batch_job", cascade="all, delete-orphan")