"""
Main FastAPI application for Medical AI Consultation System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.routes import conversation
from backend.services.rag import get_rag_service
import config


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    """
    # Startup
    print("Starting Medical AI Consultation System...")
    try:
        rag_service = get_rag_service()
        rag_service.initialize()
        print("RAG service initialized successfully")
    except Exception as e:
        print(f"Warning: Failed to initialize RAG service: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down Medical AI Consultation System...")


# Create FastAPI app
app = FastAPI(
    title="Medical AI Consultation System",
    description="AI system that evaluates a doctor's medical knowledge through simulated patient conversations",
    version="1.0.0",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routes
app.include_router(conversation.router)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "Medical AI Consultation System",
        "description": "Evaluate doctor's medical knowledge through AI patient simulation",
        "version": "1.0.0",
        "endpoints": {
            "start_case": "POST /api/start_case",
            "doctor_input": "POST /api/doctor_input",
            "evaluate": "POST /api/evaluate",
            "health": "GET /api/health"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT
    )
