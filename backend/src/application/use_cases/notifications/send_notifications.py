"""
Use case para enviar notificações sobre emendas
"""
from typing import List, Dict, Optional
import structlog

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.entities.user_preferences import UserPreferences
from src.infrastructure.notifications.email_service import EmailService
from src.infrastructure.notifications.sms_service import SMSService

logger = structlog.get_logger()


class SendNotificationsUseCase:
    """Envia notificações sobre emendas"""
    
    def __init__(
        self,
        email_service: Optional[EmailService] = None,
        sms_service: Optional[SMSService] = None
    ):
        self.email_service = email_service or EmailService()
        self.sms_service = sms_service or SMSService()
    
    async def send_alert_notification(
        self,
        user_prefs: UserPreferences,
        emenda: EmendaPix,
        alert: Dict
    ) -> dict:
        """
        Envia notificação de alerta
        
        Args:
            user_prefs: Preferências do usuário
            emenda: Emenda relacionada
            alert: Dados do alerta
        
        Returns:
            dict com resultado do envio
        """
        alert_type = alert.get("tipo", "alerta")
        alert_message = alert.get("mensagem", "")
        
        # Preparar dados da emenda
        emenda_data = {
            "id": emenda.id,
            "numero_emenda": emenda.numero_emenda,
            "autor_nome": emenda.autor_nome,
            "destinatario_nome": emenda.destinatario_nome,
            "valor_aprovado": emenda.valor_aprovado,
            "percentual_executado": emenda.percentual_executado
        }
        
        results = {
            "email_sent": False,
            "sms_sent": False
        }
        
        # Enviar email se habilitado
        if user_prefs.email_notifications_enabled and user_prefs.user_email:
            if self._should_send_alert(user_prefs, alert_type):
                email_sent = await self.email_service.send_emenda_alert(
                    to=user_prefs.user_email,
                    emenda_data=emenda_data,
                    alert_type=alert_type,
                    alert_message=alert_message
                )
                results["email_sent"] = email_sent
                logger.info(
                    "alert_email_sent",
                    user_email=user_prefs.user_email,
                    emenda_id=emenda.id,
                    alert_type=alert_type
                )
        
        # Enviar SMS se habilitado
        if user_prefs.sms_notifications_enabled and user_prefs.user_phone:
            if self._should_send_alert(user_prefs, alert_type):
                sms_sent = await self.sms_service.send_emenda_alert(
                    to=user_prefs.user_phone,
                    emenda_data=emenda_data,
                    alert_type=alert_type,
                    alert_message=alert_message
                )
                results["sms_sent"] = sms_sent
                logger.info(
                    "alert_sms_sent",
                    user_phone=user_prefs.user_phone,
                    emenda_id=emenda.id,
                    alert_type=alert_type
                )
        
        return {
            "success": results["email_sent"] or results["sms_sent"],
            "results": results
        }
    
    async def send_status_change_notification(
        self,
        user_prefs: UserPreferences,
        emenda: EmendaPix,
        old_status: str,
        new_status: str
    ) -> dict:
        """
        Envia notificação de mudança de status
        
        Args:
            user_prefs: Preferências do usuário
            emenda: Emenda relacionada
            old_status: Status anterior
            new_status: Novo status
        """
        if not user_prefs.notify_on_status_change:
            return {"success": False, "message": "Notificações de status desabilitadas"}
        
        emenda_data = {
            "id": emenda.id,
            "numero_emenda": emenda.numero_emenda,
            "autor_nome": emenda.autor_nome,
            "destinatario_nome": emenda.destinatario_nome,
            "valor_aprovado": emenda.valor_aprovado,
            "percentual_executado": emenda.percentual_executado
        }
        
        message = f"Status da emenda {emenda.numero_emenda} mudou de {old_status} para {new_status}"
        
        results = {
            "email_sent": False,
            "sms_sent": False
        }
        
        # Enviar email
        if user_prefs.email_notifications_enabled and user_prefs.user_email:
            email_sent = await self.email_service.send_emenda_alert(
                to=user_prefs.user_email,
                emenda_data=emenda_data,
                alert_type="status_change",
                alert_message=message
            )
            results["email_sent"] = email_sent
        
        # Enviar SMS
        if user_prefs.sms_notifications_enabled and user_prefs.user_phone:
            sms_sent = await self.sms_service.send_emenda_alert(
                to=user_prefs.user_phone,
                emenda_data=emenda_data,
                alert_type="status_change",
                alert_message=message
            )
            results["sms_sent"] = sms_sent
        
        return {
            "success": results["email_sent"] or results["sms_sent"],
            "results": results
        }
    
    def _should_send_alert(self, user_prefs: UserPreferences, alert_type: str) -> bool:
        """Verifica se deve enviar alerta baseado nas preferências"""
        if alert_type == "atraso":
            return user_prefs.notify_on_delay
        elif alert_type in ["risco_alto", "baixa_execucao"]:
            return user_prefs.notify_on_risk_alert
        return True

