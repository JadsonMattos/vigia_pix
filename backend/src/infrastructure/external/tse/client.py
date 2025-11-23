"""Client for TSE (Tribunal Superior Eleitoral) API"""
import httpx
from typing import List, Dict, Optional
import structlog

logger = structlog.get_logger()


class TSEClient:
    """Client for TSE (Tribunal Superior Eleitoral) API"""
    
    BASE_URL = "https://dadosabertos.tse.jus.br"
    
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={
                "Accept": "application/json"
            }
        )
    
    async def get_candidate_assets(self, year: int, uf: Optional[str] = None) -> List[Dict]:
        """
        Get candidate asset declarations
        
        Args:
            year: Election year
            uf: State code (optional)
            
        Returns:
            List of candidate asset declarations
        """
        try:
            # TSE API structure may vary, this is a template
            params = {
                "ano": year
            }
            
            if uf:
                params["uf"] = uf
            
            # Note: TSE API endpoints may require specific paths
            # This is a template that should be adjusted based on actual API
            response = await self.client.get("/api/v1/candidatos/bens", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error("error_getting_candidate_assets", error=str(e), year=year)
            return []
    
    async def get_election_results(
        self,
        year: int,
        uf: Optional[str] = None,
        position: Optional[str] = None
    ) -> List[Dict]:
        """
        Get election results
        
        Args:
            year: Election year
            uf: State code (optional)
            position: Position code (optional)
            
        Returns:
            List of election results
        """
        try:
            params = {
                "ano": year
            }
            
            if uf:
                params["uf"] = uf
            
            if position:
                params["cargo"] = position
            
            # Note: Adjust endpoint based on actual TSE API structure
            response = await self.client.get("/api/v1/resultados", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error("error_getting_election_results", error=str(e), year=year)
            return []
    
    async def get_voter_profile(self, uf: Optional[str] = None) -> Optional[Dict]:
        """Get voter profile statistics"""
        try:
            params = {}
            if uf:
                params["uf"] = uf
            
            # Note: Adjust endpoint based on actual TSE API structure
            response = await self.client.get("/api/v1/perfil-eleitorado", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("error_getting_voter_profile", error=str(e))
            return None
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()



