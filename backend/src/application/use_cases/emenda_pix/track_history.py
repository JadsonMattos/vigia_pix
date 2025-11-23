"""
Use case para rastrear histórico de execução de emendas
"""
from typing import List, Optional, Dict
import structlog
import uuid
from datetime import datetime

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository

logger = structlog.get_logger()


class TrackHistoryUseCase:
    """Rastreia histórico de execução de emendas"""
    
    def __init__(self, repository: EmendaPixRepository):
        self.repository = repository
        # Em produção, usar banco de dados
        # Por enquanto, armazenar em memória para demo
        self.history: Dict[str, List[Dict]] = {}
    
    async def record_change(
        self,
        emenda: EmendaPix,
        old_status: Optional[str] = None,
        old_percentual: Optional[float] = None,
        old_valor_pago: Optional[float] = None,
        changed_by: str = "system",
        change_reason: Optional[str] = None
    ) -> dict:
        """
        Registra mudança no histórico
        
        Args:
            emenda: Emenda atualizada
            old_status: Status anterior
            old_percentual: Percentual anterior
            old_valor_pago: Valor pago anterior
            changed_by: Quem fez a mudança
            change_reason: Motivo da mudança
        """
        try:
            # Verificar se houve mudança significativa
            if old_status == emenda.status_execucao and \
               old_percentual == emenda.percentual_executado and \
               old_valor_pago == emenda.valor_pago:
                return {
                    "success": False,
                    "message": "Nenhuma mudança detectada"
                }
            
            # Criar registro de histórico
            history_entry = {
                "id": str(uuid.uuid4()),
                "emenda_id": emenda.id,
                "timestamp": datetime.now().isoformat(),
                "status_anterior": old_status,
                "status_novo": emenda.status_execucao,
                "percentual_anterior": old_percentual,
                "percentual_novo": emenda.percentual_executado,
                "valor_pago_anterior": old_valor_pago,
                "valor_pago_novo": emenda.valor_pago,
                "changed_by": changed_by,
                "change_reason": change_reason,
                "changes": self._detect_changes(
                    old_status, emenda.status_execucao,
                    old_percentual, emenda.percentual_executado,
                    old_valor_pago, emenda.valor_pago
                )
            }
            
            # Armazenar (em produção, salvar no banco)
            if emenda.id not in self.history:
                self.history[emenda.id] = []
            self.history[emenda.id].append(history_entry)
            
            logger.info(
                "history_recorded",
                emenda_id=emenda.id,
                changes=history_entry["changes"]
            )
            
            return {
                "success": True,
                "history_entry": history_entry
            }
            
        except Exception as e:
            logger.error(
                "record_history_error",
                emenda_id=emenda.id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao registrar histórico: {str(e)}"
            }
    
    async def get_history(
        self,
        emenda_id: str,
        limit: int = 50
    ) -> dict:
        """
        Obtém histórico de uma emenda
        
        Args:
            emenda_id: ID da emenda
            limit: Limite de registros
        """
        try:
            # Buscar histórico (em produção, do banco)
            history = self.history.get(emenda_id, [])
            
            # Ordenar por timestamp (mais recente primeiro)
            history_sorted = sorted(
                history,
                key=lambda x: x["timestamp"],
                reverse=True
            )[:limit]
            
            # Gerar timeline
            timeline = self._generate_timeline(history_sorted)
            
            return {
                "success": True,
                "emenda_id": emenda_id,
                "total_entries": len(history),
                "history": history_sorted,
                "timeline": timeline
            }
            
        except Exception as e:
            logger.error(
                "get_history_error",
                emenda_id=emenda_id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao obter histórico: {str(e)}"
            }
    
    def _detect_changes(
        self,
        old_status: Optional[str],
        new_status: str,
        old_percentual: Optional[float],
        new_percentual: float,
        old_valor_pago: Optional[float],
        new_valor_pago: float
    ) -> List[str]:
        """Detecta e lista mudanças"""
        changes = []
        
        if old_status and old_status != new_status:
            changes.append(f"Status mudou de '{old_status}' para '{new_status}'")
        
        if old_percentual is not None and old_percentual != new_percentual:
            diff = new_percentual - old_percentual
            changes.append(f"Percentual executado: {old_percentual:.1f}% → {new_percentual:.1f}% ({diff:+.1f}%)")
        
        if old_valor_pago is not None and old_valor_pago != new_valor_pago:
            diff = new_valor_pago - old_valor_pago
            changes.append(f"Valor pago: R$ {old_valor_pago:,.2f} → R$ {new_valor_pago:,.2f} (R$ {diff:+,.2f})")
        
        return changes
    
    def _generate_timeline(self, history: List[Dict]) -> List[Dict]:
        """Gera timeline visual do histórico"""
        timeline = []
        
        for entry in history:
            timeline_item = {
                "date": entry["timestamp"],
                "type": "status_change" if entry["status_anterior"] != entry["status_novo"] else "execution_update",
                "title": self._generate_timeline_title(entry),
                "description": ", ".join(entry["changes"]),
                "changes": entry["changes"]
            }
            timeline.append(timeline_item)
        
        return timeline
    
    def _generate_timeline_title(self, entry: Dict) -> str:
        """Gera título para item da timeline"""
        if entry["status_anterior"] != entry["status_novo"]:
            return f"Status alterado para {entry['status_novo']}"
        elif entry["percentual_anterior"] != entry["percentual_novo"]:
            return f"Execução atualizada: {entry['percentual_novo']:.1f}%"
        else:
            return "Atualização de execução"

