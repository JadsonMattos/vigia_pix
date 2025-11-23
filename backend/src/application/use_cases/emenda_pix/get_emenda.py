"""Get Emenda Pix by ID use case"""
from typing import Optional
from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository


class GetEmendaPixUseCase:
    """Use case to get Emenda Pix by ID"""
    
    def __init__(self, repository: EmendaPixRepository):
        self.repository = repository
    
    async def execute(self, id: str) -> Optional[EmendaPix]:
        """Get emenda by ID"""
        return await self.repository.find_by_id(id)

