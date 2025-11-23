"""Get legislation use case"""
from typing import Protocol
from src.domain.entities.legislation import Legislation
from src.domain.repositories.legislation_repository import LegislationRepository
from src.domain.exceptions import LegislationNotFoundError


class GetLegislationUseCase:
    """Use case to get a legislation by ID"""
    
    def __init__(self, repository: LegislationRepository):
        self.repository = repository
    
    async def execute(self, legislation_id: str) -> Legislation:
        """
        Get legislation by ID
        
        Args:
            legislation_id: ID of the legislation
            
        Returns:
            Legislation entity
            
        Raises:
            LegislationNotFoundError: If legislation not found
        """
        legislation = await self.repository.find_by_id(legislation_id)
        
        if not legislation:
            raise LegislationNotFoundError(
                f"Legislation {legislation_id} not found"
            )
        
        return legislation



