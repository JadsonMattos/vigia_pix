"""Reports and export routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.infrastructure.persistence.postgres.database import get_db
from src.infrastructure.persistence.postgres.emenda_pix_repository_impl import PostgresEmendaPixRepository
from src.application.use_cases.reports.generate_reports import GenerateReportsUseCase

router = APIRouter(prefix="/reports", tags=["reports"])


def get_emenda_pix_repository(
    session: AsyncSession = Depends(get_db)
) -> PostgresEmendaPixRepository:
    """Dependency for emenda pix repository"""
    return PostgresEmendaPixRepository(session)


@router.get("/export/csv")
async def export_csv(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    autor: Optional[str] = Query(None, description="Filtrar por autor"),
    destinatario: Optional[str] = Query(None, description="Filtrar por destinatário"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    valor_min: Optional[float] = Query(None, description="Valor mínimo"),
    valor_max: Optional[float] = Query(None, description="Valor máximo"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Exporta emendas para CSV
    
    - **status**: Status da execução (opcional)
    - **autor**: Nome do autor (opcional)
    - **destinatario**: Nome do destinatário (opcional)
    - **ano**: Ano da emenda (opcional)
    - **valor_min**: Valor mínimo (opcional)
    - **valor_max**: Valor máximo (opcional)
    
    Retorna arquivo CSV para download.
    """
    use_case = GenerateReportsUseCase(repository)
    
    try:
        filters = {}
        if status:
            filters["status"] = status
        if autor:
            filters["autor"] = autor
        if destinatario:
            filters["destinatario"] = destinatario
        if ano:
            filters["ano"] = ano
        if valor_min:
            filters["valor_min"] = valor_min
        if valor_max:
            filters["valor_max"] = valor_max
        
        csv_content = await use_case.export_to_csv(filters=filters if filters else None)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=emendas_pix_export.csv"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao exportar CSV: {str(e)}"
        )


@router.get("/export/json")
async def export_json(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    autor: Optional[str] = Query(None, description="Filtrar por autor"),
    destinatario: Optional[str] = Query(None, description="Filtrar por destinatário"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    valor_min: Optional[float] = Query(None, description="Valor mínimo"),
    valor_max: Optional[float] = Query(None, description="Valor máximo"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Exporta emendas para JSON
    
    - **status**: Status da execução (opcional)
    - **autor**: Nome do autor (opcional)
    - **destinatario**: Nome do destinatário (opcional)
    - **ano**: Ano da emenda (opcional)
    - **valor_min**: Valor mínimo (opcional)
    - **valor_max**: Valor máximo (opcional)
    
    Retorna arquivo JSON para download.
    """
    use_case = GenerateReportsUseCase(repository)
    
    try:
        filters = {}
        if status:
            filters["status"] = status
        if autor:
            filters["autor"] = autor
        if destinatario:
            filters["destinatario"] = destinatario
        if ano:
            filters["ano"] = ano
        if valor_min:
            filters["valor_min"] = valor_min
        if valor_max:
            filters["valor_max"] = valor_max
        
        json_content = await use_case.export_to_json(filters=filters if filters else None)
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=emendas_pix_export.json"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao exportar JSON: {str(e)}"
        )


@router.get("/summary")
async def generate_summary_report(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    autor: Optional[str] = Query(None, description="Filtrar por autor"),
    destinatario: Optional[str] = Query(None, description="Filtrar por destinatário"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    valor_min: Optional[float] = Query(None, description="Valor mínimo"),
    valor_max: Optional[float] = Query(None, description="Valor máximo"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Gera relatório resumo
    
    - **status**: Status da execução (opcional)
    - **autor**: Nome do autor (opcional)
    - **destinatario**: Nome do destinatário (opcional)
    - **ano**: Ano da emenda (opcional)
    - **valor_min**: Valor mínimo (opcional)
    - **valor_max**: Valor máximo (opcional)
    
    Retorna relatório resumo com estatísticas e análises.
    """
    use_case = GenerateReportsUseCase(repository)
    
    try:
        filters = {}
        if status:
            filters["status"] = status
        if autor:
            filters["autor"] = autor
        if destinatario:
            filters["destinatario"] = destinatario
        if ano:
            filters["ano"] = ano
        if valor_min:
            filters["valor_min"] = valor_min
        if valor_max:
            filters["valor_max"] = valor_max
        
        result = await use_case.generate_summary_report(filters=filters if filters else None)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )

