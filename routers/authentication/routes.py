from fastapi import APIRouter, HTTPException


router = APIRouter()


@router.get("/test")
async def get_users():
    return {
        "Users": "Hello"
    }
