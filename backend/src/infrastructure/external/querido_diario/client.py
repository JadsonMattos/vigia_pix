"""Client for Querido Diário API"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class QueridoDiarioClient:
    """Client for Querido Diário API - Diários Oficiais de municípios brasileiros"""
    
    BASE_URL = "https://api.queridodiario.ok.org.br/api"
    
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={
                "Accept": "application/json"
            }
        )
    
    async def search_terms(
        self,
        terms: List[str],
        cities: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search for terms in Diários Oficiais
        
        Args:
            terms: List of terms to search for
            cities: List of city codes (optional)
            start_date: Start date for search
            end_date: End date for search
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            params = {
                "termos": ",".join(terms),
                "limite": limit
            }
            
            if cities:
                params["municipios"] = ",".join(cities)
            
            if start_date:
                params["data_inicio"] = start_date.isoformat()
            
            if end_date:
                params["data_fim"] = end_date.isoformat()
            
            response = await self.client.get("/gazettes", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error("error_searching_querido_diario", error=str(e), terms=terms)
            return []
    
    async def get_cities(self) -> List[Dict]:
        """Get list of available cities"""
        try:
            response = await self.client.get("/cities")
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error("error_getting_cities", error=str(e))
            return []
    
    async def get_gazette(self, gazette_id: str) -> Optional[Dict]:
        """Get specific gazette by ID"""
        try:
            response = await self.client.get(f"/gazettes/{gazette_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("error_getting_gazette", error=str(e), gazette_id=gazette_id)
            return None
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()



