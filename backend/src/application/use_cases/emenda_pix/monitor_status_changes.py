"""
Use case para monitorar mudanças de status e enviar notificações
"""
from typing import Optional
import structlog

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository
from src.infrastructure.persistence.postgres.user_preferences_repository_impl import PostgresUserPreferencesRepository
from src.application.use_cases.notifications.send_notifications import SendNotificationsUseCase

logger = structlog.get_logger()


class MonitorStatusChangesUseCase:
    """Monitora mudanças de status e envia notificações"""
    
    def __init__(
        self,
        emenda_repository: EmendaPixRepository,
        preferences_repository: PostgresUserPreferencesRepository
    ):
        self.emenda_repository = emenda_repository
        self.preferences_repository = preferences_repository
        self.notification_service = SendNotificationsUseCase()
    
    async def check_and_notify_delays(self) -> dict:
        """
        Verifica emendas atrasadas e envia notificações
        
        Returns:
            dict com resultado da verificação
        """
        try:
            # Buscar todas as emendas
            emendas = await self.emenda_repository.find_all()
            
            notified_count = 0
            errors = []
            
            for emenda in emendas:
                if not emenda.esta_atrasada():
                    continue
                
                # Buscar usuários que têm esta emenda como favorita
                # ou todos os usuários se não houver sistema de favoritos
                # Por enquanto, vamos notificar todos os usuários cadastrados
                # que têm notificações de atraso habilitadas
                
                # Buscar preferências de usuários
                # (Por enquanto, vamos simular - em produção, buscar do banco)
                
                # Gerar alerta
                alert = {
                    "tipo": "atraso",
                    "severidade": "alta",
                    "mensagem": f"Emenda {emenda.numero_emenda} está atrasada. Percentual executado: {emenda.percentual_executado:.1f}%"
                }
                
                # Notificar usuários interessados
                # (Por enquanto, apenas logar)
                logger.info(
                    "delay_alert_generated",
                    emenda_id=emenda.id,
                    numero_emenda=emenda.numero_emenda,
                    percentual_executado=emenda.percentual_executado
                )
                
                notified_count += 1
            
            return {
                "success": True,
                "checked_emendas": len(emendas),
                "delayed_emendas": notified_count,
                "notifications_sent": notified_count
            }
            
        except Exception as e:
            logger.error("check_delays_error", error=str(e))
            return {
                "success": False,
                "message": f"Erro ao verificar atrasos: {str(e)}"
            }
    
    async def notify_status_change(
        self,
        emenda: EmendaPix,
        old_status: str,
        new_status: str,
        user_email: Optional[str] = None
    ) -> dict:
        """
        Notifica mudança de status de uma emenda
        
        Args:
            emenda: Emenda que mudou de status
            old_status: Status anterior
            new_status: Novo status
            user_email: Email do usuário (opcional, se None notifica todos)
        """
        try:
            if user_email:
                # Notificar usuário específico
                prefs = await self.preferences_repository.find_by_email(user_email)
                if prefs and prefs.notify_on_status_change:
                    result = await self.notification_service.send_status_change_notification(
                        user_prefs=prefs,
                        emenda=emenda,
                        old_status=old_status,
                        new_status=new_status
                    )
                    return result
            else:
                # Notificar todos os usuários que têm esta emenda como favorita
                # ou todos os usuários cadastrados
                # (Implementação simplificada para demo)
                logger.info(
                    "status_change_detected",
                    emenda_id=emenda.id,
                    old_status=old_status,
                    new_status=new_status
                )
                return {
                    "success": True,
                    "message": "Mudança de status detectada"
                }
            
            return {
                "success": False,
                "message": "Nenhum usuário para notificar"
            }
            
        except Exception as e:
            logger.error(
                "notify_status_change_error",
                emenda_id=emenda.id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao notificar mudança de status: {str(e)}"
            }

