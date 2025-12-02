# src/v2/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def version_status():
    return {"version": "v2", "status": "in development"}
