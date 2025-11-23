"""Legislation entity"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Legislation:
    """Legislation entity"""
    id: str
    external_id: str  # ID from Câmara/Senado API
    title: str
    content: str
    author: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Optional fields
    simplified_content: Optional[str] = None
    complexity_score: Optional[float] = None
    impact_analysis: Optional[dict] = None
    
    def is_active(self) -> bool:
        """Check if legislation is active"""
        return self.status in ["EM_TRAMITACAO", "APROVADO"]
    
    def needs_simplification(self) -> bool:
        """Check if needs simplification"""
        return self.simplified_content is None




