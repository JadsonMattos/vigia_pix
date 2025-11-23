"""User preferences model for notifications and favorites"""
from sqlalchemy import Column, String, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from src.infrastructure.persistence.postgres.database import Base


class UserPreferencesModel(Base):
    """User preferences for notifications and favorites"""
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email = Column(String(255), nullable=False, unique=True, index=True)
    user_phone = Column(String(20), nullable=True)
    
    # Notificações
    email_notifications_enabled = Column(Boolean, default=True)
    sms_notifications_enabled = Column(Boolean, default=False)
    notify_on_delay = Column(Boolean, default=True)
    notify_on_status_change = Column(Boolean, default=True)
    notify_on_risk_alert = Column(Boolean, default=True)
    
    # Emendas favoritas
    favorite_emendas = Column(JSON, default=list)  # Lista de IDs de emendas
    
    # Preferências
    preferences = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

