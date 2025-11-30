"""
FastAPI application - Property Search Engine API
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config.database import get_db
from api.routers import search, listings, reports

# Create FastAPI app
app = FastAPI(
    title="UK Property Search Engine API",
    description="Prototype API for property search with enriched data",
    version="0.1.0"
)

# CORS (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(listings.router, prefix="/api", tags=["listings"])
app.include_router(reports.router, prefix="/api", tags=["reports"])


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "UK Property Search Engine API",
        "status": "operational",
        "version": "0.1.0"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Detailed health check with DB connectivity"""
    try:
        # Test DB connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "api": "ok",
        "database": db_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
