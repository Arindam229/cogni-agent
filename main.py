"""
Main FastAPI application for Cognizance AI Assistant.
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import settings
from api.routes import router, limiter, start_summary_cache_cleanup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    # Startup
    print(f"🚀 Starting {settings.app_name}")
    print(f"📍 Host: {settings.api_host}:{settings.api_port}")
    print(f"🤖 LLM Provider: Google Gemini ({settings.google_model})")
    print(f"🌐 CORS Origins: {settings.cors_origins_list}")
    print(f"✅ Service ready!")
    # Start background cleanup for summary cache (non-blocking)
    start_summary_cache_cleanup()
    yield
    # Shutdown
    print("👋 Shutting down Cognizance AI Assistant")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered chatbot for Cognizance 2026 - IIT Roorkee's Annual Technical Festival",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return JSONResponse(
        content={
            "service": settings.app_name,
            "version": "1.0.0",
            "description": "AI Assistant for Cognizance 2026",
            "endpoints": {
                "chat": "/api/v1/chat",
                "info": "/api/v1/info",
                "health": "/api/v1/health",
                "docs": "/docs",
            },
            "festival": {
                "name": "Cognizance 2026",
                "dates": "13th - 15th March 2026",
                "website": "https://www.cognizance.org.in",
            },
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
    )
