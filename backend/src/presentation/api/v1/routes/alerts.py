"""Alerts routes"""
from fastapi import APIRouter

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/")
async def list_alerts():
    """List alerts"""
    return {"message": "List alerts - TODO"}




