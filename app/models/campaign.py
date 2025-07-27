from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    brand_name = Column(String(255), nullable=False)
    target_audience = Column(Text)
    tone_id = Column(String(20), ForeignKey('content_tones.id'), nullable=False)
    status = Column(String(20), default='draft')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="campaigns")
    tone = relationship("ContentTone") 
    posts = relationship("CampaignPost", back_populates="campaign", cascade="all, delete-orphan")
    batch_jobs = relationship("BatchJob", back_populates="campaign", cascade="all, delete-orphan")