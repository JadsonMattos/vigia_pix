"""Participation routes"""
from fastapi import APIRouter

router = APIRouter(prefix="/participation", tags=["participation"])


@router.get("/")
async def list_participations():
    """List participations"""
    return {"message": "List participations - TODO"}




