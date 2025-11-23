"""Emenda Pix SQLAlchemy model"""
from sqlalchemy import Column, String, Text, DateTime, Float, JSON, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.persistence.postgres.database import Base
from datetime import datetime
import uuid


class EmendaPixModel(Base):
    """Emenda Pix database model"""
    __tablename__ = "emenda_pix"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação da Emenda
    numero_emenda = Column(String(50), unique=True, nullable=False, index=True)
    ano = Column(Integer, nullable=False, index=True)
    tipo = Column(String(50), nullable=False)  # 'individual' ou 'bancada'
    
    # Deputado/Autor
    autor_nome = Column(String(200), nullable=False, index=True)
    autor_partido = Column(String(50), nullable=True)
    autor_uf = Column(String(2), nullable=True)
    
    # Destinação
    destinatario_tipo = Column(String(50), nullable=False)  # 'municipio', 'estado', 'orgao'
    destinatario_nome = Column(String(200), nullable=False)
    destinatario_uf = Column(String(2), nullable=True)
    destinatario_cnpj = Column(String(18), nullable=True)
    
    # Valores
    valor_aprovado = Column(Float, nullable=False)
    valor_empenhado = Column(Float, nullable=True, default=0.0)
    valor_liquidado = Column(Float, nullable=True, default=0.0)
    valor_pago = Column(Float, nullable=True, default=0.0)
    
    # Objetivo/Finalidade
    objetivo = Column(Text, nullable=True)
    area = Column(String(100), nullable=True)  # 'saude', 'educacao', 'infraestrutura', etc.
    descricao_detalhada = Column(Text, nullable=True)
    
    # Execução e Rastreabilidade
    status_execucao = Column(String(50), nullable=False, default='pendente')  # 'pendente', 'em_execucao', 'concluida', 'atrasada', 'cancelada'
    percentual_executado = Column(Float, nullable=True, default=0.0)
    data_inicio = Column(DateTime, nullable=True)
    data_prevista_conclusao = Column(DateTime, nullable=True)
    data_real_conclusao = Column(DateTime, nullable=True)
    
    # Plano de Trabalho (metas)
    plano_trabalho = Column(JSON, nullable=True)  # Array de metas com valores e prazos
    numero_metas = Column(Integer, nullable=True, default=0)
    metas_concluidas = Column(Integer, nullable=True, default=0)
    
    # Alertas e Análise IA
    alertas = Column(JSON, nullable=True)  # Array de alertas gerados pela IA
    analise_ia = Column(JSON, nullable=True)  # Análise de risco, transparência, etc.
    risco_desvio = Column(Float, nullable=True)  # Score de 0-1
    
    # Transparência
    tem_noticias = Column(Boolean, default=False)
    noticias_relacionadas = Column(JSON, nullable=True)
    documentos_comprobatórios = Column(JSON, nullable=True)  # Links para fotos, notas fiscais, etc.
    
    # Triangulação de Dados - Fonte Física
    fotos_georreferenciadas = Column(JSON, nullable=True)  # Fotos com coordenadas GPS
    validacao_geofencing = Column(Boolean, nullable=True)  # Validação de geofencing
    
    # Sistema CEIS (conceitual)
    processo_sei = Column(String(100), nullable=True)  # Número do processo no CEIS
    link_portal_transparencia = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_sync = Column(DateTime, nullable=True)

