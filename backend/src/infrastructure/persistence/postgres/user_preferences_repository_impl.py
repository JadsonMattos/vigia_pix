"""PostgreSQL implementation of UserPreferencesRepository"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domain.entities.user_preferences import UserPreferences
from src.infrastructure.persistence.postgres.models.user_preferences import UserPreferencesModel


class PostgresUserPreferencesRepository:
    """PostgreSQL implementation of UserPreferencesRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_email(self, email: str) -> Optional[UserPreferences]:
        """Find preferences by email"""
        stmt = select(UserPreferencesModel).where(
            UserPreferencesModel.user_email == email
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def save(self, preferences: UserPreferences) -> None:
        """Save or update preferences"""
        model = await self.session.get(UserPreferencesModel, preferences.id)
        
        if model:
            # Update
            self._update_model(model, preferences)
        else:
            # Create
            model = self._to_model(preferences)
            self.session.add(model)
        
        await self.session.commit()
        await self.session.refresh(model)
    
    def _to_entity(self, model: UserPreferencesModel) -> UserPreferences:
        """Convert model to entity"""
        return UserPreferences(
            id=str(model.id),
            user_email=model.user_email,
            user_phone=model.user_phone,
            email_notifications_enabled=model.email_notifications_enabled,
            sms_notifications_enabled=model.sms_notifications_enabled,
            notify_on_delay=model.notify_on_delay,
            notify_on_status_change=model.notify_on_status_change,
            notify_on_risk_alert=model.notify_on_risk_alert,
            favorite_emendas=model.favorite_emendas or [],
            preferences=model.preferences or {},
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: UserPreferences) -> UserPreferencesModel:
        """Convert entity to model"""
        return UserPreferencesModel(
            id=entity.id,
            user_email=entity.user_email,
            user_phone=entity.user_phone,
            email_notifications_enabled=entity.email_notifications_enabled,
            sms_notifications_enabled=entity.sms_notifications_enabled,
            notify_on_delay=entity.notify_on_delay,
            notify_on_status_change=entity.notify_on_status_change,
            notify_on_risk_alert=entity.notify_on_risk_alert,
            favorite_emendas=entity.favorite_emendas,
            preferences=entity.preferences
        )
    
    def _update_model(self, model: UserPreferencesModel, entity: UserPreferences) -> None:
        """Update model from entity"""
        model.user_email = entity.user_email
        model.user_phone = entity.user_phone
        model.email_notifications_enabled = entity.email_notifications_enabled
        model.sms_notifications_enabled = entity.sms_notifications_enabled
        model.notify_on_delay = entity.notify_on_delay
        model.notify_on_status_change = entity.notify_on_status_change
        model.notify_on_risk_alert = entity.notify_on_risk_alert
        model.favorite_emendas = entity.favorite_emendas
        model.preferences = entity.preferences

