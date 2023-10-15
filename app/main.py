from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.MyLogger import logger
from app.routers.dogfinder import router as dogfinder_router
import os

logger.info("Starting up the app")
app = FastAPI()

# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if there is environment variable named modules and it contains the string "dogfinder", then load the dogfinder router
if "dogfinder" in os.environ.get("AI_MODULES", ""):
    app.include_router(dogfinder_router)