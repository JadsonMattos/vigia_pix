"""Cache service for AI simplifications"""
import hashlib
from typing import Optional
import structlog
from src.domain.value_objects.complexity_level import ComplexityLevel

logger = structlog.get_logger()

# Try to import async redis
try:
    from redis.asyncio import Redis
    from redis.asyncio.connection import ConnectionPool
    REDIS_ASYNC_AVAILABLE = True
except ImportError:
    REDIS_ASYNC_AVAILABLE = False
    logger.warning("Redis async not available. Cache will be disabled.")


class SimplificationCache:
    """Cache for simplified texts using Redis"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.redis_client = None
        self.cache_enabled = False
        
        if REDIS_ASYNC_AVAILABLE and redis_url:
            try:
                self.redis_client = Redis.from_url(redis_url, decode_responses=True)
                self.cache_enabled = True
                logger.info("simplification_cache_enabled", redis_url=redis_url)
            except Exception as e:
                logger.warning("redis_connection_failed", error=str(e))
                self.cache_enabled = False
                self.redis_client = None
        else:
            if not REDIS_ASYNC_AVAILABLE:
                logger.info("cache_disabled", reason="Redis async not available")
            else:
                logger.info("cache_disabled", reason="Redis URL not provided")
    
    def _generate_cache_key(self, text: str, level: ComplexityLevel) -> str:
        """Generate cache key from text and level"""
        # Create hash of text + level
        text_hash = hashlib.md5(f"{text}:{level.value}".encode()).hexdigest()
        return f"simplify:{level.value}:{text_hash}"
    
    async def get(self, text: str, level: ComplexityLevel) -> Optional[str]:
        """
        Get simplified text from cache
        
        Args:
            text: Original text
            level: Complexity level
            
        Returns:
            Simplified text if found, None otherwise
        """
        if not self.cache_enabled or not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(text, level)
            cached = await self.redis_client.get(cache_key)
            
            if cached:
                logger.info("cache_hit", level=level.value, text_length=len(text))
                return cached
            
            logger.debug("cache_miss", level=level.value, text_length=len(text))
            return None
            
        except Exception as e:
            logger.error("cache_get_error", error=str(e))
            return None
    
    async def set(
        self, 
        text: str, 
        level: ComplexityLevel, 
        simplified: str,
        ttl: int = 86400  # 24 hours
    ) -> None:
        """
        Store simplified text in cache
        
        Args:
            text: Original text
            level: Complexity level
            simplified: Simplified text
            ttl: Time to live in seconds (default: 24h)
        """
        if not self.cache_enabled or not self.redis_client:
            return
        
        try:
            cache_key = self._generate_cache_key(text, level)
            await self.redis_client.setex(cache_key, ttl, simplified)
            logger.info(
                "cache_set",
                level=level.value,
                text_length=len(text),
                simplified_length=len(simplified),
                ttl=ttl
            )
        except Exception as e:
            logger.error("cache_set_error", error=str(e))
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()


def get_cache_service(redis_url: Optional[str] = None) -> SimplificationCache:
    """Factory function to get cache service"""
    return SimplificationCache(redis_url)
