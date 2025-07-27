# app/services/batch_service.py
import asyncio
from asyncio import Semaphore
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.batch_job import BatchJob
from app.models.campaign_post import CampaignPost
from app.services.openai_service import openai_service

class BatchGenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.max_concurrent = 5  # Sesuaikan berdasarkan limit API OpenAI

    async def process_batch(self, batch_job_id: str, posts_data: List[Dict]) -> Dict[str, Any]:
        """Main batch processing function - CORE CHALLENGE"""
        # Ambil batch_job dari database
        batch_job = self.db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
        if not batch_job:
             raise Exception("Batch job not found")

        batch_job.status = "processing"
        batch_job.started_at = datetime.utcnow()
        batch_job.total_posts = len(posts_data)
        self.db.commit()

        # Create semaphore for rate limiting
        semaphore = Semaphore(self.max_concurrent)

        # Definisikan process_single_post di dalam method ini
        async def process_single_post(post_data: Dict, index: int) -> Dict:
            """Process individual post with rate limiting"""
            async with semaphore: # Gunakan semaphore untuk rate limiting
                post = None # Inisialisasi post untuk error handling
                try:
                    print(f"Processing post {index + 1}/{len(posts_data)}: {post_data.get('title', 'Untitled')}")
                    # Create database record
                    post = CampaignPost(
                        campaign_id=batch_job.campaign_id,
                        batch_job_id=batch_job_id,
                        title=post_data.get('title'),
                        topic=post_data.get('topic'),
                        brief=post_data.get('brief'),
                        generation_status='generating_caption'
                    )
                    self.db.add(post)
                    self.db.commit() # Commit setelah add
                    self.db.refresh(post) # Refresh untuk mendapatkan ID

                    # Generate caption
                    if post_data.get('generate_caption', True):
                        caption = await openai_service.generate_caption(post_data)
                        post.caption = caption

                    # Update status for image generation
                    post.generation_status = 'generating_image'
                    self.db.commit()

                    # Generate image
                    if post_data.get('generate_image', True):
                        image_url = await openai_service.generate_image(post_data)
                        post.image_url = image_url

                    # Mark as completed
                    post.generation_status = 'completed'
                    self.db.commit()

                    # Update batch progress (sukses)
                    # Ambil ulang batch_job untuk memastikan state terbaru
                    current_batch_job = self.db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
                    if current_batch_job:
                        current_batch_job.completed_posts += 1
                        self.db.commit()
                    
                    return {
                        'success': True,
                        'post_id': str(post.id),
                        'title': post.title,
                        'caption': post.caption,
                        'image_url': post.image_url
                    }
                except Exception as e:
                    error_msg = str(e)
                    print(f"Error processing post {index + 1}: {error_msg}")
                    # Rollback jika error pada post ini dan post sudah dibuat
                    self.db.rollback()
                    
                    # Perbarui job batch untuk failure
                    # Ambil ulang batch_job dari database untuk menghindari masalah detached instance
                    current_batch_job = self.db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
                    if current_batch_job:
                        current_batch_job.failed_posts += 1
                        self.db.commit()
                    
                    # Jika post sudah dibuat sebagian, pastikan statusnya diperbarui
                    if post and post.id:
                         try:
                            post.generation_status = 'failed'
                            self.db.commit()
                         except:
                            self.db.rollback() # Rollback jika gagal update post

                    return {
                        'success': False,
                        'error': error_msg,
                        'title': post_data.get('title', 'Unknown') if post_data else 'Unknown'
                    }

        # Execute all posts concurrently with rate limiting
        print(f"Starting batch generation for {len(posts_data)} posts...")
        start_time = datetime.utcnow()
        # Gunakan return_exceptions=True agar error di satu task tidak menghentikan yang lain
        results = await asyncio.gather(
            *[process_single_post(post_data, i) for i, post_data in enumerate(posts_data)],
            return_exceptions=True # Ini penting!
        )
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        # Filter hasil untuk mendapatkan yang sukses dan yang gagal
        successful_results = [r for r in results if isinstance(r, dict) and r.get('success')]
        failed_results = [r for r in results if not (isinstance(r, dict) and r.get('success'))]
        
        # Ambil ulang batch_job untuk update status akhir
        batch_job = self.db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
        if batch_job:
            # Pastikan jumlah completed dan failed sesuai dengan hasil
            # Karena update dilakukan secara individual, kita bisa gunakan hasil akhir
            batch_job.completed_posts = len(successful_results)
            batch_job.failed_posts = len(failed_results) # Hitung ulang berdasarkan hasil
            batch_job.status = "completed" if batch_job.failed_posts == 0 else "completed_with_errors"
            batch_job.completed_at = end_time
            self.db.commit()

        print(f"Batch completed in {processing_time:.2f} seconds")
        print(f"Success: {len(successful_results)}/{len(posts_data)} posts")
        return {
            'batch_id': batch_job_id,
            'total_posts': len(posts_data),
            'completed_posts': len(successful_results),
            'failed_posts': len(failed_results),
            'processing_time_seconds': processing_time,
            'results': [str(r) if isinstance(r, Exception) else r for r in results] # Konversi exception untuk respons JSON
        }
