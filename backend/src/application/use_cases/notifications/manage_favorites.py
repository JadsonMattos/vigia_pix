"""
Use case para gerenciar emendas favoritas
"""
from typing import Optional
import structlog
import uuid

from src.domain.entities.user_preferences import UserPreferences
from src.infrastructure.persistence.postgres.user_preferences_repository_impl import PostgresUserPreferencesRepository

logger = structlog.get_logger()


class ManageFavoritesUseCase:
    """Gerencia emendas favoritas do usuário"""
    
    def __init__(self, repository: PostgresUserPreferencesRepository):
        self.repository = repository
    
    async def add_favorite(
        self,
        user_email: str,
        emenda_id: str
    ) -> dict:
        """
        Adiciona emenda aos favoritos
        
        Args:
            user_email: Email do usuário
            emenda_id: ID da emenda
        
        Returns:
            dict com resultado
        """
        try:
            prefs = await self.repository.find_by_email(user_email)
            
            if not prefs:
                # Criar preferências
                prefs = UserPreferences(
                    id=str(uuid.uuid4()),
                    user_email=user_email
                )
            
            if prefs.is_favorite(emenda_id):
                return {
                    "success": False,
                    "message": "Emenda já está nos favoritos"
                }
            
            prefs.add_favorite(emenda_id)
            await self.repository.save(prefs)
            
            logger.info(
                "favorite_added",
                user_email=user_email,
                emenda_id=emenda_id
            )
            
            return {
                "success": True,
                "message": "Emenda adicionada aos favoritos",
                "favorites": prefs.favorite_emendas
            }
            
        except Exception as e:
            logger.error(
                "add_favorite_error",
                user_email=user_email,
                emenda_id=emenda_id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao adicionar favorito: {str(e)}"
            }
    
    async def remove_favorite(
        self,
        user_email: str,
        emenda_id: str
    ) -> dict:
        """
        Remove emenda dos favoritos
        
        Args:
            user_email: Email do usuário
            emenda_id: ID da emenda
        
        Returns:
            dict com resultado
        """
        try:
            prefs = await self.repository.find_by_email(user_email)
            
            if not prefs:
                return {
                    "success": False,
                    "message": "Usuário não encontrado"
                }
            
            if not prefs.is_favorite(emenda_id):
                return {
                    "success": False,
                    "message": "Emenda não está nos favoritos"
                }
            
            prefs.remove_favorite(emenda_id)
            await self.repository.save(prefs)
            
            logger.info(
                "favorite_removed",
                user_email=user_email,
                emenda_id=emenda_id
            )
            
            return {
                "success": True,
                "message": "Emenda removida dos favoritos",
                "favorites": prefs.favorite_emendas
            }
            
        except Exception as e:
            logger.error(
                "remove_favorite_error",
                user_email=user_email,
                emenda_id=emenda_id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao remover favorito: {str(e)}"
            }
    
    async def get_favorites(
        self,
        user_email: str
    ) -> dict:
        """
        Obtém lista de favoritos do usuário
        
        Args:
            user_email: Email do usuário
        
        Returns:
            dict com lista de favoritos
        """
        try:
            prefs = await self.repository.find_by_email(user_email)
            
            if not prefs:
                return {
                    "success": True,
                    "favorites": []
                }
            
            return {
                "success": True,
                "favorites": prefs.favorite_emendas
            }
            
        except Exception as e:
            logger.error(
                "get_favorites_error",
                user_email=user_email,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao obter favoritos: {str(e)}",
                "favorites": []
            }

