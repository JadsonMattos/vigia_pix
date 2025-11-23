"""User preferences entity"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class UserPreferences:
    """User preferences for notifications and favorites"""
    id: str
    user_email: str
    user_phone: Optional[str] = None
    
    # Notificações
    email_notifications_enabled: bool = True
    sms_notifications_enabled: bool = False
    notify_on_delay: bool = True
    notify_on_status_change: bool = True
    notify_on_risk_alert: bool = True
    
    # Emendas favoritas
    favorite_emendas: List[str] = field(default_factory=list)
    
    # Preferências
    preferences: Dict = field(default_factory=dict)
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def is_favorite(self, emenda_id: str) -> bool:
        """Verifica se emenda é favorita"""
        return emenda_id in self.favorite_emendas
    
    def add_favorite(self, emenda_id: str) -> None:
        """Adiciona emenda aos favoritos"""
        if emenda_id not in self.favorite_emendas:
            self.favorite_emendas.append(emenda_id)
    
    def remove_favorite(self, emenda_id: str) -> None:
        """Remove emenda dos favoritos"""
        if emenda_id in self.favorite_emendas:
            self.favorite_emendas.remove(emenda_id)

