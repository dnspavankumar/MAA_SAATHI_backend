from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import iot_routes, health_routes, alert_routes, communication_routes
from app.config.firebase import initialize_firebase
from app.utils.logger import logger

app = FastAPI(
    title="VitalSync API",
    description="Smart Health Monitoring System Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase on startup
@app.on_event("startup")
async def startup_event():
    try:
        initialize_firebase()
        logger.info("🚀 VitalSync backend started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "VitalSync"}

# Include routers
app.include_router(iot_routes.router)
app.include_router(health_routes.router)
app.include_router(alert_routes.router)
app.include_router(communication_routes.router)
