"""List Emendas Pix use case"""
from typing import List, Optional
from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository


class ListEmendasPixUseCase:
    """Use case to list Emendas Pix"""
    
    def __init__(self, repository: EmendaPixRepository):
        self.repository = repository
    
    async def execute(
        self,
        limit: int = 100,
        offset: int = 0,
        autor_nome: Optional[str] = None,
        destinatario_uf: Optional[str] = None,
        area: Optional[str] = None,
        status_execucao: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> List[EmendaPix]:
        """List emendas with optional filters"""
        return await self.repository.find_all(
            limit=limit,
            offset=offset,
            autor_nome=autor_nome,
            destinatario_uf=destinatario_uf,
            area=area,
            status_execucao=status_execucao,
            tipo=tipo
        )

