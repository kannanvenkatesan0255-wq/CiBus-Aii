"""
CIBUS-AI - FastAPI Main Application Entry Point
File: backend/app/main.py

Purpose:
Main entry point for the CIBUS-AI Surplus Prediction REST API:
1. Configures FastAPI application metadata, CORS middleware, and API routers.
2. Exposes /health check endpoint verifying ML model and preprocessor readiness.
3. Exposes Swagger (/docs) and ReDoc (/redoc) API documentation.
4. Mounts the prediction and model information routers.
"""

import sys
from pathlib import Path
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Set module resolution paths
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
AI_ENGINE_DIR = PROJECT_ROOT / "ai-engine"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(AI_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_DIR))

from app.schemas import HealthResponse
from app.routes.prediction import router as prediction_router
from app.services.prediction_service import PredictionService

# Instantiate FastAPI application
app = FastAPI(
    title="CIBUS-AI Food Surplus Prediction API",
    description=(
        "Production-grade RESTful API integrating the trained CIBUS-AI Random Forest "
        "regression engine to forecast excess food meals in real time. Built for institutional "
        "and commercial dining surplus reduction ('Predict. Connect. Nourish.')."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for development and frontend integration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(prediction_router)


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["System Diagnostics"],
    summary="Health & Readiness Check",
    description="Validates API service responsiveness and confirms that ML model and preprocessor artifacts are loaded."
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint verifying application and ML artifact status.
    """
    model_ok, prep_ok = PredictionService.check_artifacts()
    is_healthy = model_ok and prep_ok
    status_str = "healthy" if is_healthy else "degraded"

    return HealthResponse(
        status=status_str,
        model_loaded=model_ok,
        preprocessor_loaded=prep_ok,
        version="1.0.0"
    )


@app.get("/", tags=["System Diagnostics"], summary="API Root")
async def root():
    """
    Root endpoint directing clients to documentation and health check.
    """
    return {
        "project": "CIBUS-AI Food Surplus Prediction System",
        "tagline": "Predict. Connect. Nourish.",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health",
        "prediction_endpoint": "/api/predict"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
