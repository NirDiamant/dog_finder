from fastapi import FastAPI
from app.MyLogger import logger
from app.routers.dogfinder import router as dogfinder_router
import os

logger.info("Starting up the app")
app = FastAPI()

# if there is environment variable named modules and it contains the string "dogfinder", then load the dogfinder router
if "dogfinder" in os.environ.get("AI_MODULES", ""):
    app.include_router(dogfinder_router)