from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid 
from app.services.batch_service import BatchGenerationService
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.batch_job import BatchJob
from app.models.campaign import Campaign 
from app.schemas import batch_job as batch_schemas 

router = APIRouter(prefix="/batch-jobs", tags=["batch_jobs"])

@router.post("/campaigns/{campaign_id}/generate-batch", response_model=batch_schemas.BatchResultResponse) 
async def start_batch_generation(
    campaign_id: str, 
    batch_request: batch_schemas.BatchRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID format")

    campaign = db.query(Campaign).filter(Campaign.id == campaign_uuid, Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")

    try:
        enriched_posts_data = []
        for post_data in batch_request.posts:
            enriched_data = post_data.model_dump() 
            if 'brand_name' not in enriched_data or not enriched_data['brand_name']:
                enriched_data['brand_name'] = campaign.brand_name
            if 'tone' not in enriched_data or not enriched_data['tone']:
                 enriched_data['tone'] = campaign.tone.name if campaign.tone else campaign.tone_id 
            if 'target_audience' not in enriched_data or not enriched_data['target_audience']:
                 enriched_data['target_audience'] = campaign.target_audience
            if not enriched_data.get('topic'):
                 enriched_data['topic'] = enriched_data.get('title') 
            enriched_posts_data.append(enriched_data)

        batch_job = BatchJob(
            campaign_id=campaign_id, 
            user_id=current_user.id, 
            name=batch_request.name or f'Batch {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            total_posts=len(enriched_posts_data), 
            status='pending'
        )
        db.add(batch_job)
        db.commit()
        db.refresh(batch_job) 

        batch_service = BatchGenerationService(db)
        result = await batch_service.process_batch(
            str(batch_job.id),
            enriched_posts_data 
        )

        return {
            'batch_job': {
                'id': str(batch_job.id),
                'status': batch_job.status,
                'total_posts': batch_job.total_posts,
                'completed_posts': batch_job.completed_posts,
                'failed_posts': batch_job.failed_posts
            },
            'result': result 
        }

    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/status", response_model=batch_schemas.BatchStatusResponse) 
async def get_batch_status(
    job_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    batch_job = db.query(BatchJob).join(BatchJob.campaign).filter(BatchJob.id == job_uuid, BatchJob.user_id == current_user.id).first()
    if not batch_job:
        raise HTTPException(status_code=404, detail="Batch job not found or not owned by user")

    percentage = 0
    if batch_job.total_posts > 0:
        percentage = (batch_job.completed_posts / batch_job.total_posts) * 100
    return batch_schemas.BatchStatusResponse(
        id=batch_job.id,
        status=batch_job.status,
        progress=batch_schemas.BatchProgress(
            total_posts=batch_job.total_posts,
            completed_posts=batch_job.completed_posts,
            failed_posts=batch_job.failed_posts,
            remaining_posts=batch_job.total_posts - batch_job.completed_posts - batch_job.failed_posts,
            percentage=round(percentage, 1)
        )
    )

@router.get("/{job_id}/results", response_model=batch_schemas.BatchResultsResponse) 
async def get_batch_results(
    job_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    batch_job = db.query(BatchJob).join(BatchJob.campaign).filter(BatchJob.id == job_uuid, BatchJob.user_id == current_user.id).first()
    if not batch_job:
        raise HTTPException(status_code=404, detail="Batch job not found or not owned by user")

    from app.models.campaign_post import CampaignPost
    posts = db.query(CampaignPost).filter(CampaignPost.batch_job_id == job_uuid).all()

    posts_data = [
         batch_schemas.CampaignPostResult(
            id=post.id,
            title=post.title,
            topic=post.topic,
            brief=post.brief,
            caption=post.caption,
            image_url=post.image_url,
            generation_status=post.generation_status,
            created_at=post.created_at
         ) for post in posts
    ]

    batch_job_detail = batch_schemas.BatchJobDetailResult(
        id=batch_job.id,
        name=batch_job.name,
        status=batch_job.status,
        total_posts=batch_job.total_posts,
        completed_posts=batch_job.completed_posts,
        failed_posts=batch_job.failed_posts,
        started_at=batch_job.started_at,
        completed_at=batch_job.completed_at,
        created_at=batch_job.created_at,
    )

    return batch_schemas.BatchResultsResponse(
        batch_job=batch_job_detail,
        posts=posts_data
    )
