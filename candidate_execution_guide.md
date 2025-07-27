# 16-Hour Sprint Success Manual
## Social Media Content Generator - Candidate Guidelines

### 🎯 **Your Mission**

Build a system that can **generate 10-100 Instagram posts simultaneously** using AI without timeout issues in just **16 hours**.

**Success Metrics:**
- 10 posts: < 90 seconds ⚡ (CRITICAL)
- 50 posts: < 5 minutes ⭐ (TARGET)
- 100 posts: < 10 minutes 💎 (BONUS)

---

## ⏰ **16-Hour Battle Plan**

### **Day 1: Backend Power (8 hours)**
```
Hour 1-2: Setup & Foundation
Hour 3-4: Authentication & Database  
Hour 5-6: OpenAI Integration
Hour 7-8: Batch Processing (CORE)
```

### **Day 2: Frontend & Integration (8 hours)**
```
Hour 1-2: Next.js + shadcn/ui Setup
Hour 3-4: Campaign Management UI
Hour 5-6: Batch Generator Interface (CORE)
Hour 7-8: Progress Tracking & Results
```

---

## 🛠 **Required Tech Stack**

### **Backend (MANDATORY)**
- ✅ Python FastAPI
- ✅ PostgreSQL  
- ✅ SQLAlchemy + Alembic
- ✅ OpenAI API integration

### **Frontend (MANDATORY)**
- ✅ Next.js 14 + TypeScript
- ✅ shadcn/ui (ALL UI components)
- ✅ Tailwind CSS

### **AI Tools (ENCOURAGED)**
- 🤖 GitHub Copilot, Cursor, Claude, ChatGPT
- 📝 **REQUIREMENT**: Understand every line of AI code

---

## 🗄️ **Ready-to-Use Database Schema**

**Copy-paste this complete PostgreSQL schema:**

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users (simple auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content tones lookup
CREATE TABLE content_tones (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    prompt_modifier TEXT
);

-- Insert default tones
INSERT INTO content_tones (id, name, description, prompt_modifier) VALUES
('friendly', 'Friendly', 'Warm and approachable', 'Use warm, welcoming language'),
('casual', 'Casual', 'Relaxed and informal', 'Keep it conversational'),
('modern', 'Modern', 'Contemporary and innovative', 'Use trendy language'),
('professional', 'Professional', 'Formal and business-like', 'Maintain professional tone'),
('humorous', 'Humorous', 'Funny and entertaining', 'Add humor and playfulness');

-- Campaigns (organizing content)
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    brand_name VARCHAR(255) NOT NULL,
    target_audience TEXT,
    tone_id VARCHAR(20) NOT NULL REFERENCES content_tones(id),
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Batch jobs (track bulk operations) 
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    total_posts INTEGER NOT NULL DEFAULT 0,
    completed_posts INTEGER NOT NULL DEFAULT 0,
    failed_posts INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaign posts (individual content)
CREATE TABLE campaign_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    batch_job_id UUID REFERENCES batch_jobs(id) ON DELETE SET NULL,
    title VARCHAR(255),
    topic VARCHAR(255),
    brief TEXT,
    caption TEXT,
    image_url VARCHAR(500),
    generation_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_batch_jobs_status ON batch_jobs(status);
CREATE INDEX idx_campaign_posts_batch_job_id ON campaign_posts(batch_job_id);
```

---

## 🚀 **Hour-by-Hour Execution Guide**

### **HOUR 1-2: Project Foundation**

#### **Backend Setup (45 min)**
```bash
# Create project structure
mkdir social-media-generator
cd social-media-generator

# Backend setup
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic python-jose[cryptography] passlib[bcrypt] openai python-multipart

# Create environment file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost/social_media_db
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=your_jwt_secret_key_here
EOF
```

#### **FastAPI Starter Template (30 min)**
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Social Media Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### **Database Connection (15 min)**
```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **HOUR 3-4: Authentication & Models**

#### **User Model & Auth (60 min)**
```python
# models/user.py
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, server_default="NOW()")
```

#### **JWT Authentication (60 min)**
```python
# auth.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### **HOUR 5-6: OpenAI Integration** 

#### **OpenAI Service (90 min)**
```python
# services/openai_service.py
import openai
import asyncio
import os
from typing import Dict, List

class OpenAIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def generate_caption(self, campaign_data: Dict) -> str:
        prompt = f"""
        Create an engaging Instagram caption for:
        Brand: {campaign_data['brand_name']}
        Topic: {campaign_data.get('topic', 'General')}
        Tone: {campaign_data['tone']}
        Target Audience: {campaign_data.get('target_audience', 'General audience')}
        Brief: {campaign_data.get('brief', '')}
        
        Requirements:
        - Match the {campaign_data['tone']} tone
        - Include 5-8 relevant hashtags
        - Add appropriate emojis
        - Keep under 2000 characters
        - Include call-to-action
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Caption generation failed: {str(e)}")
    
    async def generate_image(self, campaign_data: Dict) -> str:
        image_prompt = f"""
        Professional Instagram post image for {campaign_data['brand_name']}.
        Topic: {campaign_data.get('topic', 'Brand content')}
        Style: {campaign_data['tone']} and appealing
        Brief: {campaign_data.get('brief', '')}
        High quality, 1:1 aspect ratio, vibrant colors, no text overlay.
        """
        
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

# Global instance
openai_service = OpenAIService()
```

#### **Test OpenAI Integration (30 min)**
```python
# Test your OpenAI service with a simple script
async def test_openai():
    test_data = {
        'brand_name': 'Test Brand',
        'topic': 'Product Launch',
        'tone': 'friendly',
        'brief': 'Testing our new product'
    }
    
    caption = await openai_service.generate_caption(test_data)
    print("Generated Caption:", caption)
    
    image_url = await openai_service.generate_image(test_data)
    print("Generated Image URL:", image_url)

# Run: python -c "import asyncio; asyncio.run(test_openai())"
```

### **HOUR 7-8: Batch Processing (MOST CRITICAL)**

#### **Core Batch Processing Engine (120 min)**
```python
# services/batch_service.py
import asyncio
from asyncio import Semaphore
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.batch_job import BatchJob
from models.campaign_post import CampaignPost
from services.openai_service import openai_service

class BatchGenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.max_concurrent = 5  # Adjust based on OpenAI rate limits
        
    async def process_batch(self, batch_job_id: str, posts_data: List[Dict]) -> Dict[str, Any]:
        """Main batch processing function - THIS IS YOUR CORE CHALLENGE"""
        
        # Update batch job status
        batch_job = self.db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
        batch_job.status = "processing"
        batch_job.started_at = datetime.utcnow()
        batch_job.total_posts = len(posts_data)
        self.db.commit()
        
        # Create semaphore for rate limiting
        semaphore = Semaphore(self.max_concurrent)
        
        async def process_single_post(post_data: Dict, index: int) -> Dict:
            """Process individual post with rate limiting"""
            async with semaphore:
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
                    self.db.commit()
                    
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
                    
                    # Update batch progress
                    batch_job.completed_posts += 1
                    self.db.commit()
                    
                    return {
                        'success': True,
                        'post_id': str(post.id),
                        'title': post.title,
                        'caption': post.caption,
                        'image_url': post.image_url
                    }
                    
                except Exception as e:
                    print(f"Error processing post {index + 1}: {str(e)}")
                    
                    # Update failure count
                    batch_job.failed_posts += 1
                    self.db.commit()
                    
                    return {
                        'success': False,
                        'error': str(e),
                        'title': post_data.get('title', 'Unknown')
                    }
        
        # Execute all posts concurrently with rate limiting
        print(f"Starting batch generation for {len(posts_data)} posts...")
        start_time = datetime.utcnow()
        
        results = await asyncio.gather(
            *[process_single_post(post_data, i) for i, post_data in enumerate(posts_data)],
            return_exceptions=True
        )
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Update final batch status
        successful_results = [r for r in results if isinstance(r, dict) and r.get('success')]
        batch_job.completed_posts = len(successful_results)
        batch_job.failed_posts = len(posts_data) - len(successful_results)
        batch_job.status = "completed" if batch_job.failed_posts == 0 else "completed_with_errors"
        batch_job.completed_at = end_time
        self.db.commit()
        
        print(f"Batch completed in {processing_time:.2f} seconds")
        print(f"Success: {len(successful_results)}/{len(posts_data)} posts")
        
        return {
            'batch_id': batch_job_id,
            'total_posts': len(posts_data),
            'completed_posts': len(successful_results),
            'failed_posts': batch_job.failed_posts,
            'processing_time_seconds': processing_time,
            'results': results
        }
```

#### **Batch API Endpoint**
```python
# api/batch.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.batch_service import BatchGenerationService
from database import get_db
import asyncio

router = APIRouter()

@router.post("/campaigns/{campaign_id}/generate-batch")
async def start_batch_generation(
    campaign_id: str,
    batch_request: Dict,  # Define proper schema
    db: Session = Depends(get_db)
):
    try:
        # Create batch job record
        batch_job = BatchJob(
            campaign_id=campaign_id,
            name=batch_request.get('name', f'Batch {datetime.now().strftime("%Y%m%d_%H%M%S")}'),
            total_posts=len(batch_request['posts']),
            status='pending'
        )
        db.add(batch_job)
        db.commit()
        
        # Start background processing
        batch_service = BatchGenerationService(db)
        
        # For simplicity, we'll process synchronously
        # In production, use Celery or similar for background processing
        result = await batch_service.process_batch(
            str(batch_job.id), 
            batch_request['posts']
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch-jobs/{job_id}/status")
async def get_batch_status(job_id: str, db: Session = Depends(get_db)):
    batch_job = db.query(BatchJob).filter(BatchJob.id == job_id).first()
    if not batch_job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    percentage = 0
    if batch_job.total_posts > 0:
        percentage = (batch_job.completed_posts / batch_job.total_posts) * 100
    
    return {
        'id': str(batch_job.id),
        'status': batch_job.status,
        'progress': {
            'total_posts': batch_job.total_posts,
            'completed_posts': batch_job.completed_posts,
            'failed_posts': batch_job.failed_posts,
            'remaining_posts': batch_job.total_posts - batch_job.completed_posts - batch_job.failed_posts,
            'percentage': round(percentage, 1)
        }
    }
```

---

## 🎨 **Day 2: Frontend Implementation**

### **HOUR 1-2: Next.js Setup**

#### **Frontend Foundation (60 min)**
```bash
# Frontend setup
cd ../frontend
npx create-next-app@latest . --typescript --tailwind --app

# Install shadcn/ui (MANDATORY)
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input textarea card progress table dialog toast form badge select

# Install additional dependencies
npm install axios zustand react-hook-form @hookform/resolvers zod lucide-react
```

#### **API Client Setup (30 min)**
```typescript
// lib/api.ts
import axios, { AxiosInstance } from 'axios'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
      timeout: 120000, // 2 minutes for batch operations
    })

    // Auth interceptor
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Authentication
  async login(username: string, password: string) {
    return this.client.post('/auth/login', { username, password })
  }

  // Campaigns
  async getCampaigns() {
    return this.client.get('/campaigns')
  }

  async createCampaign(data: any) {
    return this.client.post('/campaigns', data)
  }

  // CORE: Batch Generation
  async startBatchGeneration(campaignId: string, data: any) {
    return this.client.post(`/campaigns/${campaignId}/generate-batch`, data)
  }

  async getBatchStatus(jobId: string) {
    return this.client.get(`/batch-jobs/${jobId}/status`)
  }

  async getBatchResults(jobId: string) {
    return this.client.get(`/batch-jobs/${jobId}/results`)
  }
}

export const apiClient = new ApiClient()
```

#### **Basic Auth Setup (30 min)**
```typescript
// app/login/page.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { apiClient } from '@/lib/api'

export default function LoginPage() {
  const router = useRouter()
  const [credentials, setCredentials] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await apiClient.login(credentials.username, credentials.password)
      localStorage.setItem('access_token', response.data.access_token)
      router.push('/dashboard')
    } catch (error) {
      alert('Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Login</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <Input
              placeholder="Username"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
            />
            <Input
              type="password"
              placeholder="Password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
            />
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
```

### **HOUR 3-4: Campaign Management**

#### **Campaign Form (60 min)**
```typescript
// components/campaign-form.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { apiClient } from '@/lib/api'

export function CampaignForm({ onSuccess }: { onSuccess?: () => void }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    brand_name: '',
    target_audience: '',
    tone_id: 'friendly'
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await apiClient.createCampaign(formData)
      alert('Campaign created successfully!')
      onSuccess?.()
    } catch (error) {
      alert('Failed to create campaign')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create New Campaign</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            placeholder="Campaign Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
          
          <Input
            placeholder="Brand Name"
            value={formData.brand_name}
            onChange={(e) => setFormData({...formData, brand_name: e.target.value})}
            required
          />
          
          <Textarea
            placeholder="Campaign Description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            rows={3}
          />
          
          <Textarea
            placeholder="Target Audience"
            value={formData.target_audience}
            onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
            rows={2}
          />
          
          <Select value={formData.tone_id} onValueChange={(value) => setFormData({...formData, tone_id: value})}>
            <SelectTrigger>
              <SelectValue placeholder="Select tone" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="friendly">Friendly</SelectItem>
              <SelectItem value="casual">Casual</SelectItem>
              <SelectItem value="modern">Modern</SelectItem>
              <SelectItem value="professional">Professional</SelectItem>
              <SelectItem value="humorous">Humorous</SelectItem>
            </SelectContent>
          </Select>
          
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Creating...' : 'Create Campaign'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
```

#### **Campaign List (60 min)**
```typescript
// components/campaign-list.tsx
'use client'

import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api'

interface Campaign {
  id: string
  name: string
  brand_name: string
  tone_id: string
  status: string
  created_at: string
}

export function CampaignList({ onSelectCampaign }: { onSelectCampaign: (campaign: Campaign) => void }) {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCampaigns()
  }, [])

  const loadCampaigns = async () => {
    try {
      const response = await apiClient.getCampaigns()
      setCampaigns(response.data.campaigns || [])
    } catch (error) {
      console.error('Failed to load campaigns:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading campaigns...</div>

  return (
    <div className="space-y-4">
      {campaigns.map((campaign) => (
        <Card key={campaign.id} className="cursor-pointer hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-lg">{campaign.name}</CardTitle>
                <p className="text-sm text-gray-600">{campaign.brand_name}</p>
              </div>
              <Badge variant="outline" className="capitalize">
                {campaign.tone_id}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">
                Created: {new Date(campaign.created_at).toLocaleDateString()}
              </span>
              <Button 
                onClick={() => onSelectCampaign(campaign)}
                size="sm"
              >
                Generate Content
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
```

### **HOUR 5-6: Batch Generator (MOST CRITICAL)**

#### **Batch Generator Interface (120 min)**
```typescript
// components/batch-generator.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Plus, Trash2, Wand2, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface PostInput {
  id: string
  title: string
  topic: string
  brief: string
  generate_image: boolean
  generate_caption: boolean
}

interface Campaign {
  id: string
  name: string
  brand_name: string
  tone_id: string
}

export function BatchGenerator({ campaign }: { campaign: Campaign }) {
  const [posts, setPosts] = useState<PostInput[]>([
    {
      id: '1',
      title: '',
      topic: '',
      brief: '',
      generate_image: true,
      generate_caption: true
    }
  ])
  const [isGenerating, setIsGenerating] = useState(false)
  const [batchResult, setBatchResult] = useState<any>(null)

  const addPost = () => {
    setPosts([...posts, {
      id: Date.now().toString(),
      title: '',
      topic: '',
      brief: '',
      generate_image: true,
      generate_caption: true
    }])
  }

  const removePost = (id: string) => {
    if (posts.length > 1) {
      setPosts(posts.filter(p => p.id !== id))
    }
  }

  const updatePost = (id: string, field: keyof PostInput, value: any) => {
    setPosts(posts.map(p => p.id === id ? { ...p, [field]: value } : p))
  }

  const startGeneration = async () => {
    // Validation
    const invalidPosts = posts.filter(p => !p.title.trim() || !p.brief.trim())
    if (invalidPosts.length > 0) {
      alert(`${invalidPosts.length} posts are missing title or brief`)
      return
    }

    setIsGenerating(true)
    setBatchResult(null)

    try {
      const batchData = {
        name: `Batch ${new Date().toLocaleString()}`,
        posts: posts.map(p => ({
          title: p.title,
          topic: p.topic || p.title,
          brief: p.brief,
          brand_name: campaign.brand_name,
          tone: campaign.tone_id,
          generate_image: p.generate_image,
          generate_caption: p.generate_caption
        })),
        generation_options: {
          max_caption_words: 150,
          include_hashtags: true,
          include_emojis: true,
          use_cache: true
        }
      }

      console.log('Starting batch generation for', posts.length, 'posts...')
      const startTime = Date.now()

      const response = await apiClient.startBatchGeneration(campaign.id, batchData)
      
      const endTime = Date.now()
      const duration = (endTime - startTime) / 1000

      setBatchResult({
        ...response.data,
        duration: duration
      })

      alert(`Batch generation completed in ${duration.toFixed(1)} seconds!`)

    } catch (error: any) {
      console.error('Batch generation failed:', error)
      alert('Batch generation failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsGenerating(false)
    }
  }

  const addMultiplePosts = (count: number) => {
    const newPosts = Array.from({ length: count }, (_, i) => ({
      id: `${Date.now()}_${i}`,
      title: `Post ${posts.length + i + 1}`,
      topic: 'Sample Topic',
      brief: 'Sample brief for quick testing',
      generate_image: true,
      generate_caption: true
    }))
    setPosts([...posts, ...newPosts])
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Wand2 className="h-5 w-5" />
                Batch Content Generator
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Campaign: {campaign.name} | Brand: {campaign.brand_name}
              </p>
            </div>
            <Badge variant="outline">
              {posts.length} {posts.length === 1 ? 'Post' : 'Posts'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 flex-wrap">
            <Button onClick={addPost} variant="outline" size="sm">
              <Plus className="h-4 w-4 mr-1" />
              Add Post
            </Button>
            <Button onClick={() => addMultiplePosts(10)} variant="outline" size="sm">
              Add 10 Posts
            </Button>
            <Button onClick={() => addMultiplePosts(50)} variant="outline" size="sm">
              Add 50 Posts
            </Button>
            <Button onClick={() => addMultiplePosts(100)} variant="outline" size="sm">
              Add 100 Posts
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Posts Input */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {posts.map((post, index) => (
          <Card key={post.id}>
            <CardHeader>
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium">Post #{index + 1}</h3>
                {posts.length > 1 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removePost(post.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Input
                  placeholder="Post title"
                  value={post.title}
                  onChange={(e) => updatePost(post.id, 'title', e.target.value)}
                />
                <Input
                  placeholder="Topic (optional)"
                  value={post.topic}
                  onChange={(e) => updatePost(post.id, 'topic', e.target.value)}
                />
              </div>
              
              <Textarea
                placeholder="Brief description of this post..."
                value={post.brief}
                onChange={(e) => updatePost(post.id, 'brief', e.target.value)}
                rows={2}
              />

              <div className="flex gap-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={post.generate_caption}
                    onChange={(e) => updatePost(post.id, 'generate_caption', e.target.checked)}
                  />
                  <span className="text-sm">Generate Caption</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={post.generate_image}
                    onChange={(e) => updatePost(post.id, 'generate_image', e.target.checked)}
                  />
                  <span className="text-sm">Generate Image</span>
                </label>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Generate Button */}
      <div className="text-center">
        <Button
          onClick={startGeneration}
          disabled={isGenerating || posts.length === 0}
          size="lg"
          className="min-w-[200px]"
        >
          {isGenerating ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Generating {posts.length} Posts...
            </>
          ) : (
            <>
              <Wand2 className="mr-2 h-4 w-4" />
              Generate {posts.length} {posts.length === 1 ? 'Post' : 'Posts'}
            </>
          )}
        </Button>
      </div>

      {/* Results */}
      {batchResult && (
        <Card>
          <CardHeader>
            <CardTitle>Generation Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {batchResult.result?.completed_posts || 0}
                </div>
                <div className="text-sm text-gray-600">Completed</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">
                  {batchResult.result?.failed_posts || 0}
                </div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {batchResult.duration?.toFixed(1)}s
                </div>
                <div className="text-sm text-gray-600">Duration</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">
                  {((batchResult.result?.completed_posts || 0) / (batchResult.duration || 1) * 60).toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Posts/min</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
```

### **HOUR 7-8: Progress & Results**

#### **Progress Tracker (60 min)**
```typescript
// components/progress-tracker.tsx
'use client'

import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle, Clock, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface ProgressTrackerProps {
  jobId: string
  onComplete?: () => void
}

export function ProgressTracker({ jobId, onComplete }: ProgressTrackerProps) {
  const [progress, setProgress] = useState<any>(null)
  const [isPolling, setIsPolling] = useState(true)

  useEffect(() => {
    if (!isPolling) return

    const interval = setInterval(async () => {
      try {
        const response = await apiClient.getBatchStatus(jobId)
        setProgress(response.data.progress)

        if (response.data.status === 'completed' || response.data.status === 'failed') {
          setIsPolling(false)
          onComplete?.()
        }
      } catch (error) {
        console.error('Failed to fetch progress:', error)
      }
    }, 2000) // Poll every 2 seconds

    return () => clearInterval(interval)
  }, [jobId, isPolling, onComplete])

  if (!progress) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin mr-2" />
          <span>Loading progress...</span>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Batch Progress
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span>Progress</span>
            <span>{progress.completed_posts} of {progress.total_posts} completed</span>
          </div>
          <Progress value={progress.percentage} className="h-3" />
        </div>

        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="p-3 bg-green-50 rounded-lg">
            <div className="flex items-center justify-center gap-1 mb-1">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-lg font-bold text-green-600">{progress.completed_posts}</span>
            </div>
            <div className="text-sm text-green-700">Completed</div>
          </div>
          
          <div className="p-3 bg-red-50 rounded-lg">
            <div className="flex items-center justify-center gap-1 mb-1">
              <XCircle className="h-4 w-4 text-red-600" />
              <span className="text-lg font-bold text-red-600">{progress.failed_posts}</span>
            </div>
            <div className="text-sm text-red-700">Failed</div>
          </div>
          
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Clock className="h-4 w-4 text-blue-600" />
              <span className="text-lg font-bold text-blue-600">{progress.remaining_posts}</span>
            </div>
            <div className="text-sm text-blue-700">Remaining</div>
          </div>
        </div>

        <div className="text-center">
          <Badge variant={progress.percentage === 100 ? "default" : "secondary"}>
            {Math.round(progress.percentage)}% Complete
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}
```

#### **Main Dashboard (60 min)**
```typescript
// app/dashboard/page.tsx
'use client'

import { useState } from 'react'
import { CampaignForm } from '@/components/campaign-form'
import { CampaignList } from '@/components/campaign-list'
import { BatchGenerator } from '@/components/batch-generator'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function DashboardPage() {
  const [selectedCampaign, setSelectedCampaign] = useState<any>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Social Media Content Generator</h1>
      
      {!selectedCampaign ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Campaign List */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Your Campaigns</h2>
              <Button onClick={() => setShowCreateForm(!showCreateForm)}>
                {showCreateForm ? 'Cancel' : 'New Campaign'}
              </Button>
            </div>
            
            {showCreateForm && (
              <div className="mb-6">
                <CampaignForm onSuccess={() => {
                  setShowCreateForm(false)
                  window.location.reload()
                }} />
              </div>
            )}
            
            <CampaignList onSelectCampaign={setSelectedCampaign} />
          </div>

          {/* Instructions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Start Guide</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold">1. Create a Campaign</h3>
                <p className="text-sm text-gray-600">Set up your brand, tone, and target audience</p>
              </div>
              <div>
                <h3 className="font-semibold">2. Generate Content</h3>
                <p className="text-sm text-gray-600">Create 10-100 Instagram posts simultaneously</p>
              </div>
              <div>
                <h3 className="font-semibold">3. Review & Export</h3>
                <p className="text-sm text-gray-600">Preview and download your generated content</p>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div>
          <div className="flex items-center gap-4 mb-6">
            <Button 
              variant="outline" 
              onClick={() => setSelectedCampaign(null)}
            >
              ← Back to Campaigns
            </Button>
            <h2 className="text-xl font-semibold">Generate Content</h2>
          </div>
          
          <BatchGenerator campaign={selectedCampaign} />
        </div>
      )}
    </div>
  )
}
```

---

## ⚡ **Performance Testing Script**

Create this test to verify your performance:

```python
# test_performance.py
import asyncio
import time
from services.batch_service import BatchGenerationService

async def test_batch_performance():
    """Test batch generation performance"""
    
    # Test data
    test_posts = []
    for i in range(10):  # Start with 10 posts
        test_posts.append({
            'title': f'Test Post {i+1}',
            'topic': 'Performance Test',
            'brief': f'This is test post number {i+1} for performance testing',
            'brand_name': 'Test Brand',
            'tone': 'friendly',
            'generate_caption': True,
            'generate_image': True
        })
    
    print(f"Starting performance test with {len(test_posts)} posts...")
    start_time = time.time()
    
    # Your batch processing code here
    # results = await batch_service.process_batch(test_posts)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Generated {len(test_posts)} posts in {duration:.2f} seconds")
    print(f"⚡ Rate: {len(test_posts)/duration:.2f} posts per second")
    
    # Check if meets requirements
    if duration < 90:  # 90 seconds for 10 posts
        print("🎉 PASSED: Performance requirement met!")
        return True
    else:
        print("❌ FAILED: Performance requirement not met")
        return False

# Run test
if __name__ == "__main__":
    asyncio.run(test_batch_performance())
```

---

## 📝 **Required Documentation**

### **README.md Template**
```markdown
# Social Media Content Generator

## Performance Results ⚡
- ✅ 10 posts: 67 seconds (100% success rate)
- ✅ 50 posts: 4.2 minutes (96% success rate)  
- ✅ 100 posts: 8.5 minutes (94% success rate)

## Quick Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
```
DATABASE_URL=postgresql://user:pass@localhost/db
OPENAI_API_KEY=your_key_here
SECRET_KEY=your_jwt_secret
```

## Features Implemented
- [x] JWT Authentication
- [x] Campaign Management
- [x] Batch Content Generation (10-100 posts)
- [x] Real-time Progress Tracking
- [x] shadcn/ui Components
- [x] Performance Optimization

## Architecture Decisions
- Used async/await with semaphore for concurrent processing
- Implemented rate limiting to respect OpenAI API limits
- PostgreSQL with proper indexing for performance
- Next.js with TypeScript for type safety
```

### **PERFORMANCE.md Template**
```markdown
# Performance Testing Results

## Test Environment
- Python 3.11, FastAPI 0.104
- PostgreSQL 15
- Next.js 14, TypeScript
- 8GB RAM, 4 CPU cores

## Batch Generation Results
| Posts | Time    | Success Rate | Rate (posts/min) | Notes |
|-------|---------|--------------|------------------|-------|
| 10    | 67s     | 100%         | 8.9             | Perfect |
| 25    | 2m 15s  | 96%          | 11.1            | 1 failed |
| 50    | 4m 32s  | 94%          | 11.0            | Good |
| 100   | 8m 45s  | 92%          | 11.4            | Excellent |

## Optimization Strategies
1. **Concurrent Processing**: asyncio with Semaphore(5)
2. **Rate Limiting**: Respect OpenAI API limits
3. **Error Recovery**: Individual post failures don't stop batch
4. **Database Optimization**: Bulk operations and proper indexing

## AI Tools Used
- GitHub Copilot: 70% of boilerplate code
- Claude: Architecture decisions and optimization
- All AI-generated code was reviewed and understood
```

---

## 🚨 **Critical Success Factors**

### **Must-Have Working Features**
- [ ] ✅ System can generate 10+ posts without timeout
- [ ] ✅ Real OpenAI API integration (both text and image)
- [ ] ✅ All UI uses shadcn/ui components
- [ ] ✅ Basic authentication works
- [ ] ✅ Progress tracking shows real-time updates
- [ ] ✅ Can explain all AI-generated code

### **Performance Targets**
- [ ] ✅ 10 posts: < 90 seconds (CRITICAL)
- [ ] ⭐ 50 posts: < 5 minutes (HIGH PRIORITY)
- [ ] 💎 100 posts: < 10 minutes (BONUS)

### **Code Quality**
- [ ] ✅ Clean, readable code structure
- [ ] ✅ Proper error handling
- [ ] ✅ Environment variables for secrets
- [ ] ✅ TypeScript usage throughout frontend
- [ ] ✅ No hardcoded API keys in repository

---

## 💡 **Final Tips for Success**

### **Time Management**
1. ⏰ **Hour 1-8**: Focus on backend core functionality
2. ⏰ **Hour 9-16**: Build frontend and integrate
3. ⏰ **Test frequently**: Don't wait until the end
4. ⏰ **Document as you go**: Save time at the end

### **AI Tools Strategy**
1. 🤖 **Use for boilerplate**: Let AI generate structure
2. 🧠 **Understand everything**: Read and modify AI code
3. 🎯 **Focus on core challenge**: Batch processing performance
4. 📝 **Document AI usage**: Note what tools you used

### **Debugging Tips**
1. 🔍 **Test small batches first**: Start with 3-5 posts
2. 📊 **Add logging**: Track performance at each step
3. 🔄 **Test API separately**: Verify OpenAI integration works
4. 🚀 **Monitor resources**: Watch memory usage during batches

### **Performance Optimization**
1. ⚡ **Async processing**: Use asyncio.gather for concurrency
2. 🚦 **Rate limiting**: Respect API limits with semaphore
3. 💾 **Database efficiency**: Use bulk operations
4. 🔄 **Error recovery**: Don't let single failures stop the batch

**Remember**: This is about building a working system that can handle the core challenge. Focus on getting the batch processing working reliably first, then optimize and polish.

Good luck! 🚀