"""Legislation routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.infrastructure.persistence.postgres.database import get_db
from src.infrastructure.persistence.postgres.legislation_repository_impl import PostgresLegislationRepository
from src.application.use_cases.legislation import (
    GetLegislationUseCase, 
    ListLegislationsUseCase,
    SyncLegislationsUseCase,
    SimplifyLegislationUseCase
)
from src.infrastructure.external.camara_api import CamaraAPIClient
from src.infrastructure.external.camara_api.voting_client import CamaraVotingClient
from src.domain.value_objects.complexity_level import ComplexityLevel
from src.application.dto.legislation_dto import LegislationDTO, LegislationListResponse
from src.domain.exceptions import LegislationNotFoundError

router = APIRouter(prefix="/legislation", tags=["legislation"])


def get_legislation_repository(
    session: AsyncSession = Depends(get_db)
) -> PostgresLegislationRepository:
    """Dependency for legislation repository"""
    return PostgresLegislationRepository(session)


def get_get_legislation_use_case(
    repository: PostgresLegislationRepository = Depends(get_legislation_repository)
) -> GetLegislationUseCase:
    """Dependency for get legislation use case"""
    return GetLegislationUseCase(repository)


def get_list_legislations_use_case(
    repository: PostgresLegislationRepository = Depends(get_legislation_repository)
) -> ListLegislationsUseCase:
    """Dependency for list legislations use case"""
    return ListLegislationsUseCase(repository)


@router.get("/", response_model=LegislationListResponse)
async def list_legislations(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    use_case: ListLegislationsUseCase = Depends(get_list_legislations_use_case)
):
    """
    List legislations with pagination
    
    - **limit**: Maximum number of results (1-1000)
    - **offset**: Number of results to skip
    """
    legislations = await use_case.execute(limit=limit, offset=offset)
    
    return LegislationListResponse(
        items=[LegislationDTO.model_validate(l) for l in legislations],
        total=len(legislations),
        limit=limit,
        offset=offset
    )


@router.get("/{legislation_id}", response_model=LegislationDTO)
async def get_legislation(
    legislation_id: str,
    use_case: GetLegislationUseCase = Depends(get_get_legislation_use_case)
):
    """
    Get legislation by ID
    
    - **legislation_id**: ID of the legislation
    """
    try:
        legislation = await use_case.execute(legislation_id)
        return LegislationDTO.model_validate(legislation)
    except LegislationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sync")
async def sync_legislations(
    days: int = Query(30, ge=1, le=365),
    repository: PostgresLegislationRepository = Depends(get_legislation_repository)
):
    """
    Sync legislations from external APIs
    
    - **days**: Number of days to look back (1-365)
    
    Note: This endpoint may take some time as it fetches data from external APIs.
    For large date ranges, consider using smaller values (e.g., days=7).
    """
    camara_client = CamaraAPIClient()
    use_case = SyncLegislationsUseCase(repository, camara_client)
    
    try:
        # Add timeout to prevent hanging
        synced = await asyncio.wait_for(
            use_case.execute(days=days),
            timeout=120.0  # 2 minutes max
        )
        await camara_client.close()
        return {
            "message": f"Synced {len(synced)} legislations",
            "count": len(synced)
        }
    except asyncio.TimeoutError:
        await camara_client.close()
        raise HTTPException(
            status_code=504,
            detail="Sync operation timed out. Try with fewer days (e.g., days=7)."
        )
    except Exception as e:
        await camara_client.close()
        raise HTTPException(status_code=500, detail=f"Error syncing: {str(e)}")


@router.post("/{legislation_id}/simplify")
async def simplify_legislation(
    legislation_id: str,
    level: str = Query("intermediate", regex="^(basic|intermediate|advanced)$"),
    repository: PostgresLegislationRepository = Depends(get_legislation_repository)
):
    """
    Simplify legislation text to specified complexity level
    
    - **legislation_id**: ID of the legislation
    - **level**: Complexity level (basic, intermediate, advanced)
    
    Returns simplified text with metadata
    """
    try:
        complexity_level = ComplexityLevel(level)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid level. Use: basic, intermediate, or advanced"
        )
    
    use_case = SimplifyLegislationUseCase(repository)
    
    try:
        simplified_text = await use_case.execute(legislation_id, complexity_level)
        
        # Get legislation to return metadata
        legislation = await repository.find_by_id(legislation_id)
        
        return {
            "legislation_id": legislation_id,
            "level": level,
            "simplified_text": simplified_text,
            "original_length": len(legislation.content) if legislation else 0,
            "simplified_length": len(simplified_text),
            "reduction_percentage": round(
                (1 - len(simplified_text) / len(legislation.content)) * 100, 
                2
            ) if legislation and legislation.content else 0
        }
    except LegislationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simplifying: {str(e)}")


@router.get("/{legislation_id}/votings")
async def get_legislation_votings(
    legislation_id: str,
    repository: PostgresLegislationRepository = Depends(get_legislation_repository)
):
    """
    Get voting data for a legislation
    
    - **legislation_id**: ID of the legislation
    """
    try:
        legislation = await repository.find_by_id(legislation_id)
        if not legislation:
            raise HTTPException(status_code=404, detail="Legislation not found")
        
        # Get external ID (PL number)
        proposal_id = int(legislation.external_id) if legislation.external_id.isdigit() else None
        
        if not proposal_id:
            return {
                "message": "Voting data not available for this legislation",
                "votings": []
            }
        
        # Fetch voting data
        voting_client = CamaraVotingClient()
        votings = await voting_client.get_proposal_votings(proposal_id)
        await voting_client.close()
        
        return {
            "legislation_id": legislation_id,
            "votings": votings,
            "count": len(votings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching votings: {str(e)}")
