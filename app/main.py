from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.api.routes import router
from app.utils.image_utils import setup_directories

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Universal Medicine Verifier API...")
    setup_directories()
    print("✅ API ready!")
    yield
    # Shutdown
    print("🛑 Shutting down...")

app = FastAPI(
    title="Universal Medicine Verifier API",
    description="AI-powered medicine authentication for global medicines",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Universal Medicine Verifier API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
