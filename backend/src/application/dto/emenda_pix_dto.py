"""Emenda Pix DTOs"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class EmendaPixDTO(BaseModel):
    """Emenda Pix DTO"""
    id: str
    numero_emenda: str
    ano: int
    tipo: str
    
    # Deputado/Autor
    autor_nome: str
    autor_partido: Optional[str] = None
    autor_uf: Optional[str] = None
    
    # Destinação
    destinatario_tipo: str
    destinatario_nome: str
    destinatario_uf: Optional[str] = None
    destinatario_cnpj: Optional[str] = None
    
    # Valores
    valor_aprovado: float
    valor_empenhado: float = 0.0
    valor_liquidado: float = 0.0
    valor_pago: float = 0.0
    
    # Objetivo
    objetivo: Optional[str] = None
    area: Optional[str] = None
    descricao_detalhada: Optional[str] = None
    
    # Execução
    status_execucao: str
    percentual_executado: float = 0.0
    data_inicio: Optional[datetime] = None
    data_prevista_conclusao: Optional[datetime] = None
    data_real_conclusao: Optional[datetime] = None
    
    # Plano de Trabalho
    plano_trabalho: Optional[List[Dict]] = None
    numero_metas: int = 0
    metas_concluidas: int = 0
    
    # Análise IA
    alertas: Optional[List[Dict]] = None
    analise_ia: Optional[Dict] = None
    risco_desvio: Optional[float] = None
    
    # Transparência
    tem_noticias: bool = False
    noticias_relacionadas: Optional[List[Dict]] = None
    documentos_comprobatórios: Optional[List[Dict]] = None
    
    # Triangulação de Dados - Fonte Física
    fotos_georreferenciadas: Optional[List[Dict]] = None
    validacao_geofencing: Optional[bool] = None
    
    # Sistema CEIS
    processo_sei: Optional[str] = None  # Número do processo no CEIS
    link_portal_transparencia: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EmendaPixListResponse(BaseModel):
    """Response for list emendas"""
    items: List[EmendaPixDTO]
    total: int
    limit: int
    offset: int

