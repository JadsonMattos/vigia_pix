"""Emenda Pix entity"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class EmendaPix:
    """Emenda Pix entity"""
    # Campos obrigatórios primeiro
    id: str
    numero_emenda: str
    ano: int
    tipo: str  # 'individual' ou 'bancada'
    autor_nome: str
    destinatario_tipo: str  # 'municipio', 'estado', 'orgao'
    destinatario_nome: str
    valor_aprovado: float
    status_execucao: str = 'pendente'
    
    # Campos opcionais depois
    autor_partido: Optional[str] = None
    autor_uf: Optional[str] = None
    destinatario_uf: Optional[str] = None
    destinatario_cnpj: Optional[str] = None
    valor_empenhado: float = 0.0
    valor_liquidado: float = 0.0
    valor_pago: float = 0.0
    objetivo: Optional[str] = None
    area: Optional[str] = None
    descricao_detalhada: Optional[str] = None
    percentual_executado: float = 0.0
    data_inicio: Optional[datetime] = None
    data_prevista_conclusao: Optional[datetime] = None
    data_real_conclusao: Optional[datetime] = None
    plano_trabalho: Optional[List[Dict]] = None
    numero_metas: int = 0
    metas_concluidas: int = 0
    alertas: Optional[List[Dict]] = None
    analise_ia: Optional[Dict] = None
    risco_desvio: Optional[float] = None
    tem_noticias: bool = False
    noticias_relacionadas: Optional[List[Dict]] = None
    documentos_comprobatórios: Optional[List[Dict]] = None
    fotos_georreferenciadas: Optional[List[Dict]] = None  # Fonte Física - Triangulação
    validacao_geofencing: Optional[bool] = None  # Validação de geofencing
    processo_sei: Optional[str] = None  # Número do processo no CEIS
    link_portal_transparencia: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    
    def calcular_percentual_executado(self) -> float:
        """Calcula percentual executado baseado nos valores"""
        if self.valor_aprovado == 0:
            return 0.0
        return (self.valor_pago / self.valor_aprovado) * 100
    
    def esta_atrasada(self) -> bool:
        """Verifica se a emenda está atrasada"""
        if not self.data_prevista_conclusao:
            return False
        hoje = datetime.now()
        if self.data_prevista_conclusao < hoje and self.percentual_executado < 100:
            return True
        return False
    
    def precisa_alerta(self) -> bool:
        """Verifica se precisa gerar alerta"""
        return (
            self.esta_atrasada() or
            self.percentual_executado == 0 and self.data_inicio and 
            (datetime.now() - self.data_inicio).days > 90 or
            self.risco_desvio and self.risco_desvio > 0.7
        )
    
    def get_status_display(self) -> str:
        """Retorna status formatado para exibição"""
        status_map = {
            'pendente': 'Pendente',
            'em_execucao': 'Em Execução',
            'concluida': 'Concluída',
            'atrasada': 'Atrasada',
            'cancelada': 'Cancelada'
        }
        return status_map.get(self.status_execucao, self.status_execucao)
