"""
CIBUS-AI - FastAPI Main Application Entry Point
File: backend/app/main.py

Purpose:
Main entry point for the CIBUS-AI Surplus Prediction & Redistribution REST API:
1. Configures FastAPI application metadata, dynamic CORS middleware, and API routers.
2. Implements centralized exception handlers preventing internal stack trace leaks.
3. Exposes /health check endpoint verifying ML model and preprocessor readiness.
4. Exposes Swagger (/docs) and ReDoc (/redoc) API documentation.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cibus_ai.api")

from app.schemas import HealthResponse
from app.routes.prediction import router as prediction_router
from app.routes.ngo_matching import router as ngo_matching_router
from app.routes.route_optimization import router as route_optimization_router
from app.routes.dashboard import router as dashboard_router
from app.services.prediction_service import PredictionService

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Dynamic CORS Configuration from Environment
raw_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
)
ALLOWED_ORIGINS: List[str] = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

# Instantiate FastAPI application
app = FastAPI(
    title="CIBUS-AI Food Surplus Prediction & Redistribution API",
    description=(
        "Production-grade RESTful API integrating the trained CIBUS-AI Random Forest "
        "regression engine to forecast excess food meals, a deterministic rule-based NGO "
        "matching service, route optimization, and operational impact analytics ('Predict. Connect. Nourish.')."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Apply CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ==============================================================================
# Centralized Error Handlers (Information Leakage Prevention)
# ==============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Sanitizes request validation errors into a clean, human-readable format.
    """
    formatted_errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        msg = err.get("msg", "Invalid value")
        formatted_errors.append(f"{field}: {msg}" if field else msg)

    logger.warning("Validation failure on %s: %s", request.url.path, formatted_errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": formatted_errors if len(formatted_errors) > 1 else formatted_errors[0]}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Standardizes HTTP exception responses.
    """
    logger.info("HTTP %d on %s: %s", exc.status_code, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled server exceptions to prevent raw stack traces or
    filesystem directory structures from leaking to API clients.
    """
    logger.exception("Unhandled server exception processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again later."}
    )


# Mount API Routers
app.include_router(prediction_router)
app.include_router(ngo_matching_router)
app.include_router(route_optimization_router)
app.include_router(dashboard_router)


# System Health & Root Endpoints
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
    Does not leak internal filesystem paths or secret configurations.
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
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=(ENVIRONMENT == "development"))
