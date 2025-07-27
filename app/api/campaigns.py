from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models 
from app.schemas import campaign as campaign_schemas 
from app.schemas import user as user_schemas 
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User 

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("/", response_model=campaign_schemas.CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    campaign: campaign_schemas.CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    db_tone = db.query(models.ContentTone).filter(models.ContentTone.id == campaign.tone_id).first()
    if not db_tone:
         raise HTTPException(status_code=400, detail="Invalid tone_id")

    db_campaign = models.Campaign(
        name=campaign.name,
        description=campaign.description,
        brand_name=campaign.brand_name,
        target_audience=campaign.target_audience,
        tone_id=campaign.tone_id,
        user_id=current_user.id 
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.get("/", response_model=List[campaign_schemas.CampaignResponse])
def read_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaigns = db.query(models.Campaign).filter(models.Campaign.user_id == current_user.id).offset(skip).limit(limit).all()
    return campaigns

@router.get("/{campaign_id}", response_model=campaign_schemas.CampaignResponse)
def read_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id, models.Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")
    return campaign
