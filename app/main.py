import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.db.session import engine, Base
from app.api.routes_menu import router as menu_router
from app.api.routes_ai import router as ai_router
from app.api.routes_orders import router as orders_router
from app.api.routes_analytics import router as analytics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: could not auto-create tables on startup: {e}")
    yield

app = FastAPI(
    title="SipSense AI",
    description="Intelligent Specialty Coffee Discovery & Real-Time Ordering API powered by Google Gemini and Cloud SQL PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(menu_router)
app.include_router(ai_router)
app.include_router(orders_router)
app.include_router(analytics_router)

# Mount Static Files for Customer Web App
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "status": "online",
        "app": "SipSense AI",
        "docs": "/docs",
        "cloud_sql": "connected",
        "gemini": "active"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_ID,
        "region": settings.REGION,
        "database": settings.DB_NAME,
        "model": settings.GEMINI_MODEL
    }
