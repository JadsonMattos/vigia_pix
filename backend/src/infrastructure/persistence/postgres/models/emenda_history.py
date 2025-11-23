"""Emenda execution history model"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from src.infrastructure.persistence.postgres.database import Base


class EmendaHistoryModel(Base):
    """History of emenda execution changes"""
    __tablename__ = "emenda_history"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    emenda_id = Column(UUID(as_uuid=False), ForeignKey("emenda_pix.id"), nullable=False, index=True)
    
    # Dados do histórico
    status_anterior = Column(String(50), nullable=True)
    status_novo = Column(String(50), nullable=False)
    percentual_anterior = Column(Float, nullable=True)
    percentual_novo = Column(Float, nullable=False)
    valor_pago_anterior = Column(Float, nullable=True)
    valor_pago_novo = Column(Float, nullable=True)
    
    # Metadados
    changed_by = Column(String(255), nullable=True)  # Sistema, usuário, etc.
    change_reason = Column(String(500), nullable=True)
    extra_data = Column(JSON, nullable=True)  # Dados adicionais (metadata é palavra reservada do SQLAlchemy)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

