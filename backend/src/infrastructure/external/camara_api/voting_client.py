"""Client for fetching voting data from Câmara API"""
import httpx
from typing import List, Dict, Optional
import structlog

logger = structlog.get_logger()


class CamaraVotingClient:
    """Client for fetching voting data from Câmara dos Deputados"""
    
    BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
    
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={
                "Accept": "application/json"
            }
        )
    
    async def get_proposal_votings(self, proposal_id: int) -> List[Dict]:
        """
        Get voting data for a proposal
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            List of voting sessions
        """
        try:
            response = await self.client.get(f"/proposicoes/{proposal_id}/votacoes")
            response.raise_for_status()
            data = response.json()
            return data.get("dados", [])
        except Exception as e:
            logger.error("error_fetching_votings", proposal_id=proposal_id, error=str(e))
            return []
    
    async def get_voting_details(self, voting_id: int) -> Optional[Dict]:
        """
        Get details of a voting session
        
        Args:
            voting_id: ID of the voting session
            
        Returns:
            Voting details with votes
        """
        try:
            response = await self.client.get(f"/votacoes/{voting_id}")
            response.raise_for_status()
            data = response.json()
            return data.get("dados")
        except Exception as e:
            logger.error("error_fetching_voting_details", voting_id=voting_id, error=str(e))
            return None
    
    async def get_deputy_votes(self, voting_id: int) -> List[Dict]:
        """
        Get individual deputy votes for a voting session
        
        Args:
            voting_id: ID of the voting session
            
        Returns:
            List of deputy votes
        """
        try:
            response = await self.client.get(f"/votacoes/{voting_id}/votos")
            response.raise_for_status()
            data = response.json()
            return data.get("dados", [])
        except Exception as e:
            logger.error("error_fetching_deputy_votes", voting_id=voting_id, error=str(e))
            return []
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()



