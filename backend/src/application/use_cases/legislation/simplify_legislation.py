"""Simplify legislation text use case"""
from src.domain.entities.legislation import Legislation
from src.domain.value_objects.complexity_level import ComplexityLevel
from src.domain.repositories.legislation_repository import LegislationRepository
from src.domain.exceptions import LegislationNotFoundError
from src.infrastructure.ai.simplification_service import (
    TextSimplificationService,
    get_ai_service,
    get_simplification_service
)
from src.infrastructure.ai.cache_service import get_cache_service
import os


class SimplifyLegislationUseCase:
    """Use case to simplify legislation text"""
    
    def __init__(
        self,
        repository: LegislationRepository,
        simplification_service: TextSimplificationService = None
    ):
        self.repository = repository
        # Use factory to get simplification service with AI and cache
        if simplification_service is None:
            # Get cache service
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            cache_service = get_cache_service(redis_url)
            
            # Get simplification service with AI and cache
            self.simplification_service = get_simplification_service(
                ai_service=None,  # Will use factory
                cache_service=cache_service
            )
        else:
            self.simplification_service = simplification_service
    
    async def execute(
        self, 
        legislation_id: str, 
        level: ComplexityLevel
    ) -> str:
        """
        Simplify legislation text to specified level
        
        Args:
            legislation_id: ID of the legislation
            level: Complexity level for simplification
            
        Returns:
            Simplified text
            
        Raises:
            LegislationNotFoundError: If legislation not found
        """
        # Get legislation
        legislation = await self.repository.find_by_id(legislation_id)
        
        if not legislation:
            raise LegislationNotFoundError(
                f"Legislation {legislation_id} not found"
            )
        
        # Check if already simplified for this level
        if legislation.simplified_content and level == ComplexityLevel.INTERMEDIATE:
            # For now, we only store one simplified version
            # In the future, we could store multiple levels
            return legislation.simplified_content
        
        # Simplify text
        simplified_text = await self.simplification_service.simplify(
            text=legislation.content,
            level=level
        )
        
        # Update legislation
        legislation.simplified_content = simplified_text
        await self.repository.save(legislation)
        
        return simplified_text



