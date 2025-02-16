from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/")
async def hello_world():
    return {"response": "Hello, I am here!"}
