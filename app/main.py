from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

from app.MyLogger import logger
from app.routers.dogfinder import router as dogfinder_router
import os


class Settings(BaseSettings):
    openapi_url: str = "/openapi.json"


settings = Settings()

app = FastAPI(openapi_url=settings.openapi_url)

logger.info("Starting up the app")

origins = [f"{os.environ.get('ALLOWED_CORS', 'https://localhost:3000')}"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if there is environment variable named modules and it contains the string "dogfinder", then load the dogfinder router
if "dogfinder" in os.environ.get("AI_MODULES", ""):
    app.include_router(dogfinder_router)
