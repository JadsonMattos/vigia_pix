"""Client for DataJud (CNJ) API"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class DataJudClient:
    """Client for DataJud (CNJ) API - Base nacional de dados do Poder Judiciário"""
    
    BASE_URL = "https://dadosabertos.cnj.jus.br"
    
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={
                "Accept": "application/json"
            }
        )
    
    async def get_judicial_processes(
        self,
        uf: Optional[str] = None,
        court: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get judicial processes
        
        Args:
            uf: State code (optional)
            court: Court code (optional)
            start_date: Start date
            end_date: End date
            limit: Maximum number of results
            
        Returns:
            List of judicial processes
        """
        try:
            params = {
                "limite": limit
            }
            
            if uf:
                params["uf"] = uf
            
            if court:
                params["tribunal"] = court
            
            if start_date:
                params["data_inicio"] = start_date.isoformat()
            
            if end_date:
                params["data_fim"] = end_date.isoformat()
            
            # Note: Adjust endpoint based on actual DataJud API structure
            response = await self.client.get("/api/v1/processos", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error("error_getting_judicial_processes", error=str(e))
            return []
    
    async def get_courts(self) -> List[Dict]:
        """Get list of courts"""
        try:
            response = await self.client.get("/api/v1/tribunais")
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error("error_getting_courts", error=str(e))
            return []
    
    async def get_statistics(
        self,
        uf: Optional[str] = None,
        year: Optional[int] = None
    ) -> Optional[Dict]:
        """Get judicial statistics"""
        try:
            params = {}
            if uf:
                params["uf"] = uf
            if year:
                params["ano"] = year
            
            response = await self.client.get("/api/v1/estatisticas", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("error_getting_statistics", error=str(e))
            return None
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()



