"""
GovernAI - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title="GovernAI API",
    description="Enterprise AI Reporting, Compliance, and Contract Intelligence Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware
cors_origins = settings.CORS_ORIGINS.split(",") if "," in settings.CORS_ORIGINS else [settings.CORS_ORIGINS]
# Clean up origins (remove whitespace)
cors_origins = [origin.strip() for origin in cors_origins]
# Add common development origins
cors_origins.extend([
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001"
])
# Remove duplicates
cors_origins = list(set(cors_origins))
print(f"[CORS] Allowed origins: {cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development (change in production)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
print(f"[CORS] CORS middleware configured - allowing all origins for development")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "GovernAI API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - no auth required"""
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.now().isoformat()}

# CORS middleware should handle OPTIONS automatically, but add explicit handler if needed
@app.api_route("/{full_path:path}", methods=["OPTIONS"])
async def options_handler(full_path: str):
    """Handle CORS preflight requests for all paths"""
    from fastapi import Response
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "3600"
        }
    )

