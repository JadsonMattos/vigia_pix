"""Client for Senado Federal API"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class SenadoAPIClient:
    """Client for Senado Federal API"""
    
    BASE_URL = "https://legis.senado.leg.br/dadosabertos"
    
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={
                "Accept": "application/json"
            }
        )
    
    async def get_senators(self) -> List[Dict]:
        """Get list of senators"""
        try:
            response = await self.client.get("/senador/lista/atual")
            response.raise_for_status()
            data = response.json()
            return data.get("ListaParlamentarEmExercicio", {}).get("Parlamentares", {}).get("Parlamentar", [])
        except Exception as e:
            logger.error("error_getting_senators", error=str(e))
            return []
    
    async def get_matters(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get matters (proposições) from Senado
        
        Args:
            start_date: Start date
            end_date: End date
            limit: Maximum number of results
            
        Returns:
            List of matters
        """
        try:
            params = {
                "itens": limit
            }
            
            if start_date:
                params["dataInicio"] = start_date.strftime("%d/%m/%Y")
            
            if end_date:
                params["dataFim"] = end_date.strftime("%d/%m/%Y")
            
            response = await self.client.get("/materia", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("Materias", {}).get("Materia", [])
        except Exception as e:
            logger.error("error_getting_matters", error=str(e))
            return []
    
    async def get_matter_details(self, matter_id: int) -> Optional[Dict]:
        """Get details of a specific matter"""
        try:
            response = await self.client.get(f"/materia/{matter_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("error_getting_matter_details", error=str(e), matter_id=matter_id)
            return None
    
    async def get_votings(self, matter_id: int) -> List[Dict]:
        """Get votings for a matter"""
        try:
            response = await self.client.get(f"/materia/{matter_id}/votacoes")
            response.raise_for_status()
            data = response.json()
            return data.get("Votacoes", {}).get("Votacao", [])
        except Exception as e:
            logger.error("error_getting_votings", error=str(e), matter_id=matter_id)
            return []
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()



