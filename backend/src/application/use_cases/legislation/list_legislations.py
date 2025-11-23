"""List legislations use case"""
from typing import List
from src.domain.entities.legislation import Legislation
from src.domain.repositories.legislation_repository import LegislationRepository


class ListLegislationsUseCase:
    """Use case to list legislations"""
    
    def __init__(self, repository: LegislationRepository):
        self.repository = repository
    
    async def execute(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Legislation]:
        """
        List legislations with pagination
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of Legislation entities
        """
        return await self.repository.find_all(limit=limit, offset=offset)



