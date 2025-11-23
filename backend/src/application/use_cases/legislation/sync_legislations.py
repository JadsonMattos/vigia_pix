"""Sync legislations from external APIs"""
from typing import List
from datetime import datetime, timedelta
import uuid
import asyncio
import structlog

from src.domain.entities.legislation import Legislation
from src.domain.repositories.legislation_repository import LegislationRepository
from src.infrastructure.external.camara_api import CamaraAPIClient, CamaraAPIAdapter

logger = structlog.get_logger()


class SyncLegislationsUseCase:
    """Use case to sync legislations from external APIs"""
    
    def __init__(
        self,
        repository: LegislationRepository,
        camara_client: CamaraAPIClient
    ):
        self.repository = repository
        self.camara_client = camara_client
    
    async def execute(self, days: int = 30) -> List[Legislation]:
        """
        Sync legislations from external APIs
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of synced legislations
        """
        synced_legislations = []
        
        # Calculate date range (use today as end date, not future)
        from datetime import date
        data_fim = datetime.combine(date.today(), datetime.min.time())
        data_inicio = data_fim - timedelta(days=days)
        
        # Ensure we don't request future dates
        if data_fim > datetime.now():
            data_fim = datetime.now()
        
        # Get proposals from Câmara
        logger.info("sync_starting", days=days, data_inicio=data_inicio, data_fim=data_fim)
        proposals = await self.camara_client.get_proposals(
            data_inicio=data_inicio,
            data_fim=data_fim,
            limit=100
        )
        
        logger.info("sync_proposals_fetched", count=len(proposals))
        
        # Process proposals with limited concurrency to avoid overwhelming the API
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def process_proposal(proposal):
            async with semaphore:
                return await self._process_single_proposal(proposal)
        
        # Process all proposals concurrently (but limited)
        tasks = [process_proposal(proposal) for proposal in proposals]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        for result in results:
            if isinstance(result, Exception):
                logger.error("sync_proposal_failed", error=str(result))
            elif result:
                synced_legislations.append(result)
        
        logger.info("sync_completed", synced_count=len(synced_legislations), total_proposals=len(proposals))
        return synced_legislations
    
    async def _process_single_proposal(self, proposal: dict) -> Legislation | None:
        """Process a single proposal"""
        try:
            # Check if already exists
            existing = await self.repository.find_by_external_id(
                str(proposal.get("id", ""))
            )
            
            if existing:
                return None  # Skip if already exists
            
            proposal_id = proposal.get("id")
            
            # Fetch data in parallel (text, authors, details)
            tasks = []
            if proposal_id:
                tasks.append(self.camara_client.get_proposal_text(proposal_id))
                tasks.append(self.camara_client.get_proposal_authors(proposal_id))
                tasks.append(self.camara_client.get_proposal_details(proposal_id))
            else:
                tasks = [asyncio.sleep(0), asyncio.sleep(0), asyncio.sleep(0)]
            
            # Wait for all with timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=10.0  # 10 seconds max per proposal
                )
                text, autores, proposal_details = results
            except asyncio.TimeoutError:
                logger.warning("sync_proposal_timeout", proposal_id=proposal_id)
                text, autores, proposal_details = None, [], None
            
            # Handle exceptions in results
            if isinstance(text, Exception):
                logger.warning("sync_text_error", proposal_id=proposal_id, error=str(text))
                text = None
            if isinstance(autores, Exception):
                logger.warning("sync_authors_error", proposal_id=proposal_id, error=str(autores))
                autores = []
            if isinstance(proposal_details, Exception):
                logger.warning("sync_details_error", proposal_id=proposal_id, error=str(proposal_details))
                proposal_details = None
            
            # Add autores to proposal data
            if autores and len(autores) > 0:
                proposal["autores"] = autores
            
            # Merge details into proposal data
            if proposal_details:
                proposal.update(proposal_details)
            
            # Convert to domain entity
            legislation = CamaraAPIAdapter.to_legislation(proposal, text)
            legislation.id = str(uuid.uuid4())
            
            # Truncate title if too long (safety check)
            if legislation.title and len(legislation.title) > 10000:
                legislation.title = legislation.title[:10000] + "..."
            
            # Save to database
            await self.repository.save(legislation)
            return legislation
            
        except Exception as e:
            logger.error("error_syncing_proposal", proposal_id=proposal.get("id"), error=str(e))
            return None



