"""
Use case para compartilhamento de emendas em redes sociais
"""
from typing import Dict, Optional
import structlog
import uuid
from datetime import datetime, timedelta

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository

logger = structlog.get_logger()


class ShareEmendaUseCase:
    """Gerencia compartilhamento de emendas"""
    
    def __init__(self, repository: EmendaPixRepository):
        self.repository = repository
        # Em produção, usar banco de dados para armazenar links
        self.share_links: Dict[str, Dict] = {}
    
    async def generate_share_link(
        self,
        emenda_id: str,
        platform: Optional[str] = None
    ) -> dict:
        """
        Gera link de compartilhamento para emenda
        
        Args:
            emenda_id: ID da emenda
            platform: Plataforma (twitter, facebook, whatsapp, etc.)
        
        Returns:
            dict com link e metadados
        """
        try:
            emenda = await self.repository.find_by_id(emenda_id)
            if not emenda:
                return {
                    "success": False,
                    "message": "Emenda não encontrada"
                }
            
            # Gerar link único
            share_id = str(uuid.uuid4())
            share_link = f"https://vozcidada.org/emenda-pix/{emenda_id}?share={share_id}"
            
            # Armazenar link (em produção, usar banco de dados)
            self.share_links[share_id] = {
                "emenda_id": emenda_id,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=30),
                "platform": platform,
                "access_count": 0
            }
            
            # Gerar metadados para compartilhamento
            metadata = self._generate_metadata(emenda, platform)
            
            logger.info(
                "share_link_generated",
                emenda_id=emenda_id,
                share_id=share_id,
                platform=platform
            )
            
            return {
                "success": True,
                "share_id": share_id,
                "share_link": share_link,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(
                "generate_share_link_error",
                emenda_id=emenda_id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao gerar link: {str(e)}"
            }
    
    async def get_share_preview(
        self,
        emenda_id: str,
        platform: str = "default"
    ) -> dict:
        """
        Obtém preview para compartilhamento em redes sociais
        
        Args:
            emenda_id: ID da emenda
            platform: Plataforma (twitter, facebook, whatsapp, etc.)
        
        Returns:
            dict com preview formatado
        """
        try:
            emenda = await self.repository.find_by_id(emenda_id)
            if not emenda:
                return {
                    "success": False,
                    "message": "Emenda não encontrada"
                }
            
            preview = self._generate_preview(emenda, platform)
            
            return {
                "success": True,
                "preview": preview
            }
            
        except Exception as e:
            logger.error(
                "get_share_preview_error",
                emenda_id=emenda_id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao gerar preview: {str(e)}"
            }
    
    def _generate_metadata(
        self,
        emenda: EmendaPix,
        platform: Optional[str]
    ) -> Dict:
        """Gera metadados para compartilhamento"""
        base_url = "https://vozcidada.org"
        emenda_url = f"{base_url}/emenda-pix/{emenda.id}"
        
        # Determinar tipo de alerta
        alert_type = "info"
        if emenda.esta_atrasada():
            alert_type = "warning"
        if emenda.risco_desvio and emenda.risco_desvio > 0.7:
            alert_type = "danger"
        
        # Título
        title = f"Emenda {emenda.numero_emenda} - {emenda.autor_nome}"
        
        # Descrição
        description = f"Valor: R$ {emenda.valor_aprovado:,.2f} | "
        description += f"Executado: {emenda.percentual_executado:.1f}% | "
        description += f"Status: {emenda.status_execucao}"
        
        if emenda.esta_atrasada():
            description += " ⚠️ ATRASADA"
        
        # Imagem (em produção, gerar dinamicamente)
        image_url = f"{base_url}/api/v1/emenda-pix/{emenda.id}/share-image"
        
        metadata = {
            "title": title,
            "description": description,
            "url": emenda_url,
            "image": image_url,
            "type": "website",
            "site_name": "Voz Cidadã",
            "locale": "pt_BR"
        }
        
        # Metadados específicos por plataforma
        if platform == "twitter":
            metadata.update({
                "twitter_card": "summary_large_image",
                "twitter_title": title,
                "twitter_description": description[:200],  # Limite do Twitter
                "twitter_image": image_url
            })
        elif platform == "facebook":
            metadata.update({
                "og_title": title,
                "og_description": description,
                "og_image": image_url,
                "og_url": emenda_url,
                "og_type": "article"
            })
        elif platform == "whatsapp":
            metadata.update({
                "whatsapp_text": f"{title}\n\n{description}\n\n{emenda_url}"
            })
        
        return metadata
    
    def _generate_preview(
        self,
        emenda: EmendaPix,
        platform: str
    ) -> Dict:
        """Gera preview formatado para plataforma"""
        if platform == "twitter":
            # Twitter: 280 caracteres
            text = f"🔍 Emenda {emenda.numero_emenda} - {emenda.autor_nome}\n"
            text += f"💰 R$ {emenda.valor_aprovado:,.0f} | "
            text += f"✅ {emenda.percentual_executado:.0f}% executado\n"
            if emenda.esta_atrasada():
                text += "⚠️ ATRASADA\n"
            text += f"🔗 vozcidada.org/emenda-pix/{emenda.id}"
            
            return {
                "platform": "twitter",
                "text": text[:280],
                "hashtags": ["#Transparencia", "#EmendaPix", "#ControleSocial"]
            }
        
        elif platform == "facebook":
            # Facebook: mais espaço
            text = f"📊 Acompanhe a execução da Emenda {emenda.numero_emenda}\n\n"
            text += f"👤 Autor: {emenda.autor_nome}\n"
            text += f"📍 Destino: {emenda.destinatario_nome}\n"
            text += f"💰 Valor Aprovado: R$ {emenda.valor_aprovado:,.2f}\n"
            text += f"✅ Percentual Executado: {emenda.percentual_executado:.1f}%\n"
            text += f"📈 Status: {emenda.status_execucao}\n\n"
            if emenda.esta_atrasada():
                text += "⚠️ ATENÇÃO: Esta emenda está ATRASADA!\n\n"
            text += f"🔗 Acompanhe: vozcidada.org/emenda-pix/{emenda.id}"
            
            return {
                "platform": "facebook",
                "text": text,
                "hashtags": ["#Transparencia", "#EmendaPix", "#ControleSocial", "#Fiscalizacao"]
            }
        
        elif platform == "whatsapp":
            # WhatsApp: formato simples
            text = f"*Emenda {emenda.numero_emenda}*\n"
            text += f"*Autor:* {emenda.autor_nome}\n"
            text += f"*Destino:* {emenda.destinatario_nome}\n"
            text += f"*Valor:* R$ {emenda.valor_aprovado:,.2f}\n"
            text += f"*Executado:* {emenda.percentual_executado:.1f}%\n"
            text += f"*Status:* {emenda.status_execucao}\n"
            if emenda.esta_atrasada():
                text += "\n⚠️ *ATRASADA*\n"
            text += f"\nvozcidada.org/emenda-pix/{emenda.id}"
            
            return {
                "platform": "whatsapp",
                "text": text,
                "url": f"https://vozcidada.org/emenda-pix/{emenda.id}"
            }
        
        else:
            # Default: formato genérico
            return {
                "platform": "default",
                "title": f"Emenda {emenda.numero_emenda}",
                "description": f"Valor: R$ {emenda.valor_aprovado:,.2f} | Executado: {emenda.percentual_executado:.1f}%",
                "url": f"https://vozcidada.org/emenda-pix/{emenda.id}"
            }

