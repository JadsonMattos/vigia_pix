"""Data sources routes - Integration with external APIs"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
import structlog

from src.infrastructure.external.querido_diario.client import QueridoDiarioClient
from src.infrastructure.external.senado_api.client import SenadoAPIClient
from src.infrastructure.external.tse.client import TSEClient
from src.infrastructure.external.cnj_datjud.client import DataJudClient

logger = structlog.get_logger()
router = APIRouter(prefix="/data-sources", tags=["data-sources"])


@router.get("/querido-diario/search")
async def search_querido_diario(
    terms: str = Query(..., description="Terms to search (comma-separated)"),
    cities: Optional[str] = Query(None, description="City codes (comma-separated)"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back")
):
    """
    Search Querido Diário (Diários Oficiais)
    
    - **terms**: Terms to search (comma-separated)
    - **cities**: City codes (comma-separated, optional)
    - **days**: Number of days to look back (1-365)
    """
    try:
        client = QueridoDiarioClient()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        terms_list = [t.strip() for t in terms.split(",")]
        cities_list = [c.strip() for c in cities.split(",")] if cities else None
        
        results = await client.search_terms(
            terms=terms_list,
            cities=cities_list,
            start_date=start_date,
            end_date=end_date
        )
        await client.close()
        
        return {
            "source": "querido-diario",
            "terms": terms_list,
            "count": len(results),
            "results": results[:50]  # Limit to 50 for response size
        }
    except Exception as e:
        logger.error("error_searching_querido_diario", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error searching Querido Diário: {str(e)}")


@router.get("/senado/matters")
async def get_senado_matters(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back")
):
    """
    Get matters from Senado Federal
    
    - **days**: Number of days to look back (1-365)
    """
    try:
        client = SenadoAPIClient()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        matters = await client.get_matters(start_date=start_date, end_date=end_date)
        await client.close()
        
        return {
            "source": "senado-federal",
            "count": len(matters),
            "matters": matters[:50]  # Limit to 50
        }
    except Exception as e:
        logger.error("error_getting_senado_matters", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting Senado matters: {str(e)}")


@router.get("/senado/senators")
async def get_senators():
    """Get list of senators"""
    try:
        client = SenadoAPIClient()
        senators = await client.get_senators()
        await client.close()
        
        return {
            "source": "senado-federal",
            "count": len(senators),
            "senators": senators
        }
    except Exception as e:
        logger.error("error_getting_senators", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting senators: {str(e)}")


@router.get("/tse/election-results")
async def get_election_results(
    year: int = Query(2022, ge=2000, le=2030, description="Election year"),
    uf: Optional[str] = Query(None, description="State code (optional)")
):
    """
    Get election results from TSE
    
    - **year**: Election year
    - **uf**: State code (optional)
    """
    try:
        client = TSEClient()
        results = await client.get_election_results(year=year, uf=uf)
        await client.close()
        
        return {
            "source": "tse",
            "year": year,
            "count": len(results),
            "results": results[:50]  # Limit to 50
        }
    except Exception as e:
        logger.error("error_getting_election_results", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting election results: {str(e)}")


@router.get("/datjud/processes")
async def get_judicial_processes(
    uf: Optional[str] = Query(None, description="State code (optional)"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back")
):
    """
    Get judicial processes from DataJud
    
    - **uf**: State code (optional)
    - **days**: Number of days to look back (1-365)
    """
    try:
        client = DataJudClient()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        processes = await client.get_judicial_processes(
            uf=uf,
            start_date=start_date,
            end_date=end_date
        )
        await client.close()
        
        return {
            "source": "datjud-cnj",
            "count": len(processes),
            "processes": processes[:50]  # Limit to 50
        }
    except Exception as e:
        logger.error("error_getting_judicial_processes", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting judicial processes: {str(e)}")


@router.get("/sources")
async def list_data_sources():
    """List all available data sources"""
    return {
        "sources": [
            {
                "name": "Câmara dos Deputados",
                "description": "APIs completas com texto de Projetos de Lei, votações, discursos, gastos de deputados e tramitações",
                "url": "https://dadosabertos.camara.leg.br/swagger/api.html",
                "endpoints": [
                    "/api/v1/legislation/sync",
                    "/api/v1/legislation/{id}/votings"
                ]
            },
            {
                "name": "Senado Federal",
                "description": "Lista de senadores, matérias, votações e orçamentos",
                "url": "https://www12.senado.leg.br/dados-abertos",
                "endpoints": [
                    "/api/v1/data-sources/senado/matters",
                    "/api/v1/data-sources/senado/senators"
                ]
            },
            {
                "name": "Querido Diário",
                "description": "API que centraliza e padroniza Diários Oficiais de centenas de municípios brasileiros",
                "url": "https://queridodiario.ok.org.br/tecnologia/api",
                "endpoints": [
                    "/api/v1/data-sources/querido-diario/search"
                ]
            },
            {
                "name": "TSE",
                "description": "Repositório de Dados Eleitorais - Declaração de bens dos candidatos, resultados de eleições, perfil do eleitorado",
                "url": "https://dadosabertos.tse.jus.br/",
                "endpoints": [
                    "/api/v1/data-sources/tse/election-results"
                ]
            },
            {
                "name": "DataJud (CNJ)",
                "description": "Base nacional de dados do Poder Judiciário - Útil para entender judicialização de políticas públicas",
                "url": "https://dadosabertos.cnj.jus.br/",
                "endpoints": [
                    "/api/v1/data-sources/datjud/processes"
                ]
            },
            {
                "name": "Base dos Dados",
                "description": "Datalake público - A melhor plataforma para acessar dados tratados do Brasil (IBGE, RAIS, SUS)",
                "url": "https://basedosdados.org/",
                "note": "Requires BigQuery or Python SDK integration"
            }
        ]
    }



