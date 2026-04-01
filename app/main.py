from fastapi import FastAPI

from app.routes.validate import router as validate_router
from app.routes.match import router as match_router
from app.routes.process import router as process_router
from app.routes.health import router as health_router

app = FastAPI(title="Document Intelligence Pipeline API")

# Include routers (no prefixes for simplicity)
app.include_router(validate_router)
app.include_router(match_router)
app.include_router(process_router)
app.include_router(health_router)
