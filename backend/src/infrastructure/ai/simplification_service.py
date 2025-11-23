"""Text simplification service using AI"""
from typing import Protocol, Optional
from src.domain.value_objects.complexity_level import ComplexityLevel
import structlog
import os

logger = structlog.get_logger()


class AIService(Protocol):
    """Protocol for AI service"""
    async def simplify(self, text: str, level: ComplexityLevel) -> str:
        ...


class TextSimplificationService:
    """Service for simplifying legislative texts using AI"""
    
    def __init__(self, ai_service: AIService, cache_service: Optional[object] = None):
        self.ai_service = ai_service
        self.cache_service = cache_service
    
    async def simplify(
        self, 
        text: str, 
        level: ComplexityLevel
    ) -> str:
        """
        Simplify text to the specified complexity level
        
        Args:
            text: Original text to simplify
            level: Target complexity level
            
        Returns:
            Simplified text
        """
        try:
            logger.info(
                "simplifying_text",
                text_length=len(text),
                level=level.value
            )
            
            # Check cache first
            if self.cache_service:
                cached = await self.cache_service.get(text, level)
                if cached:
                    logger.info("using_cached_simplification", level=level.value)
                    return cached
            
            # Call AI service
            simplified = await self.ai_service.simplify(text, level)
            
            # Store in cache
            if self.cache_service:
                await self.cache_service.set(text, level, simplified)
            
            # Log for explicability
            self._log_simplification(text, simplified, level)
            
            logger.info(
                "text_simplified",
                original_length=len(text),
                simplified_length=len(simplified),
                level=level.value
            )
            
            return simplified
            
        except Exception as e:
            logger.error("error_simplifying_text", error=str(e), level=level.value)
            raise
    
    def _log_simplification(
        self, 
        original: str, 
        simplified: str, 
        level: ComplexityLevel
    ):
        """Log simplification for transparency"""
        logger.info(
            "ai_decision",
            input_length=len(original),
            output_length=len(simplified),
            level=level.value,
            reduction_percentage=round((1 - len(simplified)/len(original)) * 100, 2) if original else 0
        )


# Placeholder implementation (fallback when OpenAI is not available)
class PlaceholderAIService:
    """Placeholder AI service for development"""
    
    async def simplify(self, text: str, level: ComplexityLevel) -> str:
        """
        Placeholder simplification - returns text with note
        
        Used as fallback when OpenAI is not configured
        """
        prefix = {
            ComplexityLevel.BASIC: "[SIMPLIFICADO - NÍVEL BÁSICO] ",
            ComplexityLevel.INTERMEDIATE: "[SIMPLIFICADO - NÍVEL INTERMEDIÁRIO] ",
            ComplexityLevel.ADVANCED: "[SIMPLIFICADO - NÍVEL AVANÇADO] "
        }[level]
        
        # Simple placeholder: just add prefix and truncate if too long
        max_length = {
            ComplexityLevel.BASIC: 500,
            ComplexityLevel.INTERMEDIATE: 1000,
            ComplexityLevel.ADVANCED: 2000
        }[level]
        
        simplified = text[:max_length]
        if len(text) > max_length:
            simplified += "..."
        
        return prefix + simplified


def get_ai_service():
    """Factory function to get AI service (OpenAI or Placeholder)"""
    try:
        from src.infrastructure.ai.openai_service import OpenAIService
        return OpenAIService()
    except (ImportError, ValueError) as e:
        logger.warning("using_placeholder_ai", error=str(e))
        return PlaceholderAIService()


def get_simplification_service(ai_service: Optional[AIService] = None, cache_service: Optional[object] = None):
    """Factory function to get TextSimplificationService with AI and cache"""
    if ai_service is None:
        ai_service = get_ai_service()
    
    return TextSimplificationService(ai_service, cache_service)



