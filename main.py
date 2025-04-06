from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.db.session import engine
from app.db.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="LinkedIn Growth Agent",
    description="Ein automatisierter Agent für LinkedIn-Wachstum und Engagement",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion anpassen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Willkommen beim LinkedIn Growth Agent",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 