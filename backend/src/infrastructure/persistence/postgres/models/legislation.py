"""Legislation SQLAlchemy model"""
from sqlalchemy import Column, String, Text, DateTime, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.persistence.postgres.database import Base
from datetime import datetime
import uuid


class LegislationModel(Base):
    """Legislation database model"""
    __tablename__ = "legislations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)  # Changed from String(500) to Text to support longer titles
    content = Column(Text, nullable=False)
    author = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Optional fields
    simplified_content = Column(Text, nullable=True)
    complexity_score = Column(Float, nullable=True)
    impact_analysis = Column(JSON, nullable=True)

