"""Notifications and favorites routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel, EmailStr

from src.infrastructure.persistence.postgres.database import get_db
from src.infrastructure.persistence.postgres.user_preferences_repository_impl import PostgresUserPreferencesRepository
from src.application.use_cases.notifications.manage_favorites import ManageFavoritesUseCase
from src.application.use_cases.notifications.send_notifications import SendNotificationsUseCase
from src.infrastructure.notifications.email_service import EmailService
from src.infrastructure.notifications.sms_service import SMSService

router = APIRouter(prefix="/notifications", tags=["notifications"])


class UserPreferencesRequest(BaseModel):
    """Request model for user preferences"""
    user_email: EmailStr
    user_phone: Optional[str] = None
    email_notifications_enabled: bool = True
    sms_notifications_enabled: bool = False
    notify_on_delay: bool = True
    notify_on_status_change: bool = True
    notify_on_risk_alert: bool = True


def get_user_preferences_repository(
    session: AsyncSession = Depends(get_db)
) -> PostgresUserPreferencesRepository:
    """Dependency for user preferences repository"""
    return PostgresUserPreferencesRepository(session)


@router.post("/preferences")
async def update_preferences(
    preferences: UserPreferencesRequest,
    repository: PostgresUserPreferencesRepository = Depends(get_user_preferences_repository)
):
    """
    Atualiza preferências de notificações do usuário
    
    - **user_email**: Email do usuário (obrigatório)
    - **user_phone**: Telefone (opcional)
    - **email_notifications_enabled**: Habilitar notificações por email
    - **sms_notifications_enabled**: Habilitar notificações por SMS
    - **notify_on_delay**: Notificar quando emenda atrasar
    - **notify_on_status_change**: Notificar mudanças de status
    - **notify_on_risk_alert**: Notificar alertas de risco
    """
    from src.domain.entities.user_preferences import UserPreferences
    import uuid
    
    try:
        # Buscar ou criar preferências
        existing = await repository.find_by_email(preferences.user_email)
        
        if existing:
            # Atualizar
            existing.user_phone = preferences.user_phone
            existing.email_notifications_enabled = preferences.email_notifications_enabled
            existing.sms_notifications_enabled = preferences.sms_notifications_enabled
            existing.notify_on_delay = preferences.notify_on_delay
            existing.notify_on_status_change = preferences.notify_on_status_change
            existing.notify_on_risk_alert = preferences.notify_on_risk_alert
            user_prefs = existing
        else:
            # Criar
            user_prefs = UserPreferences(
                id=str(uuid.uuid4()),
                user_email=preferences.user_email,
                user_phone=preferences.user_phone,
                email_notifications_enabled=preferences.email_notifications_enabled,
                sms_notifications_enabled=preferences.sms_notifications_enabled,
                notify_on_delay=preferences.notify_on_delay,
                notify_on_status_change=preferences.notify_on_status_change,
                notify_on_risk_alert=preferences.notify_on_risk_alert
            )
        
        await repository.save(user_prefs)
        
        return {
            "success": True,
            "message": "Preferências atualizadas com sucesso",
            "preferences": {
                "user_email": user_prefs.user_email,
                "email_notifications_enabled": user_prefs.email_notifications_enabled,
                "sms_notifications_enabled": user_prefs.sms_notifications_enabled,
                "notify_on_delay": user_prefs.notify_on_delay,
                "notify_on_status_change": user_prefs.notify_on_status_change,
                "notify_on_risk_alert": user_prefs.notify_on_risk_alert
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar preferências: {str(e)}"
        )


@router.get("/preferences/{user_email}")
async def get_preferences(
    user_email: str,
    repository: PostgresUserPreferencesRepository = Depends(get_user_preferences_repository)
):
    """
    Obtém preferências de notificações do usuário
    
    - **user_email**: Email do usuário
    """
    try:
        prefs = await repository.find_by_email(user_email)
        
        if not prefs:
            return {
                "success": True,
                "preferences": None,
                "message": "Preferências não encontradas"
            }
        
        return {
            "success": True,
            "preferences": {
                "user_email": prefs.user_email,
                "user_phone": prefs.user_phone,
                "email_notifications_enabled": prefs.email_notifications_enabled,
                "sms_notifications_enabled": prefs.sms_notifications_enabled,
                "notify_on_delay": prefs.notify_on_delay,
                "notify_on_status_change": prefs.notify_on_status_change,
                "notify_on_risk_alert": prefs.notify_on_risk_alert,
                "favorite_emendas": prefs.favorite_emendas
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter preferências: {str(e)}"
        )


@router.post("/favorites/{user_email}/{emenda_id}")
async def add_favorite(
    user_email: str,
    emenda_id: str,
    repository: PostgresUserPreferencesRepository = Depends(get_user_preferences_repository)
):
    """
    Adiciona emenda aos favoritos do usuário
    
    - **user_email**: Email do usuário
    - **emenda_id**: ID da emenda
    """
    use_case = ManageFavoritesUseCase(repository)
    
    try:
        result = await use_case.add_favorite(user_email, emenda_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao adicionar favorito: {str(e)}"
        )


@router.delete("/favorites/{user_email}/{emenda_id}")
async def remove_favorite(
    user_email: str,
    emenda_id: str,
    repository: PostgresUserPreferencesRepository = Depends(get_user_preferences_repository)
):
    """
    Remove emenda dos favoritos do usuário
    
    - **user_email**: Email do usuário
    - **emenda_id**: ID da emenda
    """
    use_case = ManageFavoritesUseCase(repository)
    
    try:
        result = await use_case.remove_favorite(user_email, emenda_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover favorito: {str(e)}"
        )


@router.get("/favorites/{user_email}")
async def get_favorites(
    user_email: str,
    repository: PostgresUserPreferencesRepository = Depends(get_user_preferences_repository)
):
    """
    Obtém lista de emendas favoritas do usuário
    
    - **user_email**: Email do usuário
    """
    use_case = ManageFavoritesUseCase(repository)
    
    try:
        result = await use_case.get_favorites(user_email)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter favoritos: {str(e)}"
        )


@router.post("/test/{user_email}")
async def test_notification(
    user_email: str,
    repository: PostgresUserPreferencesRepository = Depends(get_user_preferences_repository)
):
    """
    Envia notificação de teste para o usuário
    
    - **user_email**: Email do usuário
    """
    try:
        prefs = await repository.find_by_email(user_email)
        if not prefs:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        email_service = EmailService()
        sms_service = SMSService()
        
        # Enviar email de teste
        if prefs.email_notifications_enabled:
            await email_service.send_email(
                to=prefs.user_email,
                subject="Teste de Notificação - Voz Cidadã",
                body="Esta é uma notificação de teste do sistema Voz Cidadã."
            )
        
        # Enviar SMS de teste
        if prefs.sms_notifications_enabled and prefs.user_phone:
            await sms_service.send_sms(
                to=prefs.user_phone,
                message="Teste: Sistema Voz Cidadã funcionando!"
            )
        
        return {
            "success": True,
            "message": "Notificação de teste enviada"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar notificação de teste: {str(e)}"
        )

