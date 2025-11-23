"""Legislation DTOs"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LegislationDTO(BaseModel):
    """Legislation Data Transfer Object"""
    id: str
    external_id: str
    title: str
    content: str
    author: str
    status: str
    created_at: datetime
    updated_at: datetime
    simplified_content: Optional[str] = None
    complexity_score: Optional[float] = None
    impact_analysis: Optional[dict] = None
    
    class Config:
        from_attributes = True


class LegislationListResponse(BaseModel):
    """Response for legislation list"""
    items: list[LegislationDTO]
    total: int
    limit: int
    offset: int



