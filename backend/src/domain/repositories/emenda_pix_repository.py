"""Emenda Pix repository interface"""
from typing import Protocol, Optional, List
from src.domain.entities.emenda_pix import EmendaPix


class EmendaPixRepository(Protocol):
    """Repository interface for Emenda Pix"""
    
    async def find_by_id(self, id: str) -> Optional[EmendaPix]:
        """Find emenda by ID"""
        ...
    
    async def find_by_numero(self, numero: str, ano: int) -> Optional[EmendaPix]:
        """Find emenda by number and year"""
        ...
    
    async def find_all(
        self, 
        limit: int = 100, 
        offset: int = 0,
        autor_nome: Optional[str] = None,
        destinatario_uf: Optional[str] = None,
        area: Optional[str] = None,
        status_execucao: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> List[EmendaPix]:
        """Find all emendas with optional filters"""
        ...
    
    async def find_by_autor(self, autor_nome: str) -> List[EmendaPix]:
        """Find emendas by author"""
        ...
    
    async def find_by_destinatario(self, destinatario_nome: str) -> List[EmendaPix]:
        """Find emendas by recipient"""
        ...
    
    async def save(self, emenda: EmendaPix) -> None:
        """Save or update emenda"""
        ...
    
    async def delete(self, id: str) -> None:
        """Delete emenda"""
        ...

