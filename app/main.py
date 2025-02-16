from fastapi import APIRouter
from app.routes import hello_world

api_router = APIRouter()

api_router.include_router(hello_world.router, tags=["Hello"])