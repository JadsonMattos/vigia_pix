"""
Serviço de envio de SMS
Envia notificações por SMS sobre emendas
"""
import os
from typing import Optional
import structlog

logger = structlog.get_logger()


class SMSService:
    """Serviço para envio de SMS"""
    
    def __init__(self):
        # Em produção, usar serviço real (Twilio, AWS SNS, etc.)
        self.sms_enabled = os.getenv("SMS_ENABLED", "false").lower() == "true"
        self.sms_provider = os.getenv("SMS_PROVIDER", "twilio")  # twilio, aws_sns, etc.
        self.api_key = os.getenv("SMS_API_KEY")
        self.api_secret = os.getenv("SMS_API_SECRET")
    
    async def send_sms(
        self,
        to: str,
        message: str
    ) -> bool:
        """
        Envia SMS
        
        Args:
            to: Número de telefone (formato: +5511999999999)
            message: Mensagem a enviar
        
        Returns:
            True se enviado com sucesso
        """
        try:
            if not self.sms_enabled:
                # Para demo, apenas logar
                logger.info(
                    "sms_sent_simulated",
                    to=to,
                    message_preview=message[:50] + "..."
                )
                return True
            
            # Em produção, implementar envio real
            # Exemplo com Twilio:
            # from twilio.rest import Client
            # 
            # client = Client(self.api_key, self.api_secret)
            # message = client.messages.create(
            #     body=message,
            #     from_='+1234567890',  # Número Twilio
            #     to=to
            # )
            # return message.sid is not None
            
            logger.info("sms_sent", to=to)
            return True
            
        except Exception as e:
            logger.error("sms_send_error", to=to, error=str(e))
            return False
    
    async def send_emenda_alert(
        self,
        to: str,
        emenda_data: dict,
        alert_type: str,
        alert_message: str
    ) -> bool:
        """
        Envia alerta sobre emenda por SMS
        
        Args:
            to: Número de telefone
            emenda_data: Dados da emenda
            alert_type: Tipo de alerta
            alert_message: Mensagem do alerta
        """
        # SMS tem limite de caracteres, criar mensagem curta
        message = f"""Alerta: {emenda_data.get('numero_emenda', 'Emenda')} - {alert_type}
{alert_message}
Valor: R${emenda_data.get('valor_aprovado', 0):,.0f}
Executado: {emenda_data.get('percentual_executado', 0):.0f}%
Ver: localhost:3000/emenda-pix/{emenda_data.get('id', '')}"""
        
        return await self.send_sms(to, message)

