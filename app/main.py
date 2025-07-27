from fastapi import FastAPI, Depends 
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app import models
from app.database import engine, Base
from app.api import auth, campaigns, batch
from app.auth import get_current_user 
from app.models.user import User 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")

app = FastAPI(title="Social Media Generator API", version="1.0.0", lifespan=lifespan)

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

app.include_router(auth.router, prefix="/api") 

app.include_router(campaigns.router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(batch.router, prefix="/api", dependencies=[Depends(get_current_user)])
