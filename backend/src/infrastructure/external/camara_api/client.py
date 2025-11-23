"""Client for Câmara dos Deputados API"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class CamaraAPIClient:
    """Client for Câmara dos Deputados API"""
    
    BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
    
    def __init__(self, timeout: int = 10):  # Reduced from 30 to 10 seconds
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={
                "Accept": "application/json"
            },
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)  # Connection pooling
        )
    
    async def get_proposals(
        self,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get proposals from Câmara
        
        Args:
            data_inicio: Start date
            data_fim: End date
            limit: Maximum number of results
            
        Returns:
            List of proposals
        """
        params = {
            "itens": limit,
            "ordem": "DESC"
            # Removido "ordenarPor": pode causar erro 400 na API
            # A API ordena por padrão
        }
        
        # Only add date parameters if provided and valid
        if data_inicio:
            params["dataInicio"] = data_inicio.strftime("%Y-%m-%d")
        if data_fim:
            # Ensure we don't send future dates
            hoje = datetime.now().date()
            data_fim_date = data_fim.date()
            if data_fim_date <= hoje:
                params["dataFim"] = data_fim.strftime("%Y-%m-%d")
            else:
                # Use today if future date
                params["dataFim"] = hoje.strftime("%Y-%m-%d")
        
        # Log request for debugging
        logger.debug("fetching_proposals", params=params)
        
        try:
            response = await self.client.get("/proposicoes", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("dados", [])
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.json().get("detail", e.response.text[:200])
            except:
                error_detail = e.response.text[:200]
            
            logger.error(
                "error_fetching_proposals_http",
                status_code=e.response.status_code,
                url=str(e.request.url),
                params=params,
                error_detail=error_detail
            )
            raise
        except Exception as e:
            logger.error("error_fetching_proposals", error=str(e), params=params)
            raise
    
    async def get_proposal_details(self, proposal_id: int) -> Optional[Dict]:
        """
        Get proposal details by ID
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Proposal details or None
        """
        try:
            response = await self.client.get(f"/proposicoes/{proposal_id}")
            response.raise_for_status()
            data = response.json()
            return data.get("dados")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error("error_fetching_proposal", proposal_id=proposal_id, error=str(e))
            raise
        except Exception as e:
            logger.error("error_fetching_proposal", proposal_id=proposal_id, error=str(e))
            raise
    
    async def get_proposal_authors(self, proposal_id: int) -> List[Dict]:
        """
        Get proposal authors
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            List of authors
        """
        try:
            response = await self.client.get(f"/proposicoes/{proposal_id}/autores")
            response.raise_for_status()
            data = response.json()
            return data.get("dados", [])
        except Exception as e:
            logger.error("error_fetching_proposal_authors", proposal_id=proposal_id, error=str(e))
            return []
    
    async def get_proposal_text(self, proposal_id: int) -> Optional[str]:
        """
        Get proposal text content
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Proposal text or None
        """
        try:
            # Skip text fetching for now - it's slow and often returns 405
            # Use ementa as content instead
            return None
        except Exception as e:
            logger.error("error_fetching_proposal_text", proposal_id=proposal_id, error=str(e))
            return None
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()



