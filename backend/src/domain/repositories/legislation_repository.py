"""Legislation repository interface"""
from typing import Protocol, Optional, List
from src.domain.entities.legislation import Legislation


class LegislationRepository(Protocol):
    """Repository interface for Legislation"""
    
    async def find_by_id(self, id: str) -> Optional[Legislation]:
        """Find legislation by ID"""
        ...
    
    async def find_by_external_id(self, external_id: str) -> Optional[Legislation]:
        """Find legislation by external ID"""
        ...
    
    async def find_all(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Legislation]:
        """Find all legislations"""
        ...
    
    async def save(self, legislation: Legislation) -> None:
        """Save or update legislation"""
        ...
    
    async def delete(self, id: str) -> None:
        """Delete legislation"""
        ...




