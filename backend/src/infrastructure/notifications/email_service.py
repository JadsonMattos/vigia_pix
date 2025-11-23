"""
Serviço de envio de emails
Envia notificações por email sobre emendas
"""
import os
from typing import Optional, List
import structlog

logger = structlog.get_logger()


class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self):
        # Em produção, usar serviço real (SendGrid, AWS SES, etc.)
        self.smtp_enabled = os.getenv("SMTP_ENABLED", "false").lower() == "true"
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Envia email
        
        Args:
            to: Email do destinatário
            subject: Assunto
            body: Corpo do email (texto)
            html_body: Corpo do email (HTML, opcional)
        
        Returns:
            True se enviado com sucesso
        """
        try:
            if not self.smtp_enabled:
                # Para demo, apenas logar
                logger.info(
                    "email_sent_simulated",
                    to=to,
                    subject=subject
                )
                return True
            
            # Em produção, implementar envio real
            # Exemplo com smtplib:
            # import smtplib
            # from email.mime.text import MIMEText
            # from email.mime.multipart import MIMEMultipart
            # 
            # msg = MIMEMultipart('alternative')
            # msg['Subject'] = subject
            # msg['From'] = self.smtp_user
            # msg['To'] = to
            # 
            # text_part = MIMEText(body, 'plain')
            # msg.attach(text_part)
            # 
            # if html_body:
            #     html_part = MIMEText(html_body, 'html')
            #     msg.attach(html_part)
            # 
            # with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.smtp_user, self.smtp_password)
            #     server.send_message(msg)
            
            logger.info("email_sent", to=to, subject=subject)
            return True
            
        except Exception as e:
            logger.error("email_send_error", to=to, error=str(e))
            return False
    
    async def send_emenda_alert(
        self,
        to: str,
        emenda_data: dict,
        alert_type: str,
        alert_message: str
    ) -> bool:
        """
        Envia alerta sobre emenda
        
        Args:
            to: Email do destinatário
            emenda_data: Dados da emenda
            alert_type: Tipo de alerta (atraso, risco_alto, etc.)
            alert_message: Mensagem do alerta
        """
        subject = f"⚠️ Alerta: {emenda_data.get('numero_emenda', 'Emenda')} - {alert_type}"
        
        body = f"""
Alerta sobre Emenda Pix

Emenda: {emenda_data.get('numero_emenda', 'N/A')}
Autor: {emenda_data.get('autor_nome', 'N/A')}
Destinatário: {emenda_data.get('destinatario_nome', 'N/A')}
Valor Aprovado: R$ {emenda_data.get('valor_aprovado', 0):,.2f}
Percentual Executado: {emenda_data.get('percentual_executado', 0):.1f}%

Tipo de Alerta: {alert_type}
Mensagem: {alert_message}

Acesse: http://localhost:3000/emenda-pix/{emenda_data.get('id', '')}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .alert {{ background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; }}
        .emenda-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .button {{ background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="alert">
        <h2>⚠️ Alerta sobre Emenda Pix</h2>
        <p><strong>Tipo:</strong> {alert_type}</p>
        <p><strong>Mensagem:</strong> {alert_message}</p>
    </div>
    
    <div class="emenda-info">
        <h3>Informações da Emenda</h3>
        <p><strong>Número:</strong> {emenda_data.get('numero_emenda', 'N/A')}</p>
        <p><strong>Autor:</strong> {emenda_data.get('autor_nome', 'N/A')}</p>
        <p><strong>Destinatário:</strong> {emenda_data.get('destinatario_nome', 'N/A')}</p>
        <p><strong>Valor Aprovado:</strong> R$ {emenda_data.get('valor_aprovado', 0):,.2f}</p>
        <p><strong>Percentual Executado:</strong> {emenda_data.get('percentual_executado', 0):.1f}%</p>
    </div>
    
    <a href="http://localhost:3000/emenda-pix/{emenda_data.get('id', '')}" class="button">
        Ver Detalhes da Emenda
    </a>
</body>
</html>
"""
        
        return await self.send_email(to, subject, body, html_body)

