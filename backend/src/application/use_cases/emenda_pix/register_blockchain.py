"""
Use case para registrar transações de emendas na blockchain
"""
from typing import Optional
import structlog

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository
from src.infrastructure.blockchain.tracker import get_blockchain_tracker

logger = structlog.get_logger()


class RegisterBlockchainUseCase:
    """Registra transações de emendas na blockchain"""
    
    def __init__(self, repository: EmendaPixRepository):
        self.repository = repository
        self.blockchain = get_blockchain_tracker()
    
    async def register_emenda_creation(self, emenda: EmendaPix) -> dict:
        """
        Registra criação de uma emenda na blockchain
        
        Args:
            emenda: Entidade da emenda
        
        Returns:
            dict com resultado do registro
        """
        try:
            emenda_data = {
                "numero_emenda": emenda.numero_emenda,
                "ano": emenda.ano,
                "autor_nome": emenda.autor_nome,
                "destinatario_nome": emenda.destinatario_nome,
                "valor_aprovado": emenda.valor_aprovado,
                "plano_trabalho": emenda.plano_trabalho or []
            }
            
            block = self.blockchain.register_emenda_creation(
                emenda_id=emenda.id,
                emenda_data=emenda_data
            )
            
            logger.info(
                "emenda_registered_blockchain",
                emenda_id=emenda.id,
                block_hash=block["hash"][:16] + "..."
            )
            
            return {
                "success": True,
                "message": "Emenda registrada na blockchain",
                "block": {
                    "index": block["index"],
                    "hash": block["hash"],
                    "timestamp": block["timestamp"]
                }
            }
            
        except Exception as e:
            logger.error(
                "blockchain_registration_error",
                emenda_id=emenda.id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao registrar na blockchain: {str(e)}"
            }
    
    async def register_execution_update(self, emenda: EmendaPix) -> dict:
        """
        Registra atualização de execução na blockchain
        
        Args:
            emenda: Entidade da emenda
        
        Returns:
            dict com resultado do registro
        """
        try:
            execution_data = {
                "valor_pago": emenda.valor_pago,
                "percentual_executado": emenda.percentual_executado,
                "status_execucao": emenda.status_execucao,
                "metas_concluidas": emenda.metas_concluidas
            }
            
            block = self.blockchain.register_execution_update(
                emenda_id=emenda.id,
                execution_data=execution_data
            )
            
            logger.info(
                "execution_registered_blockchain",
                emenda_id=emenda.id,
                block_hash=block["hash"][:16] + "..."
            )
            
            return {
                "success": True,
                "message": "Execução registrada na blockchain",
                "block": {
                    "index": block["index"],
                    "hash": block["hash"],
                    "timestamp": block["timestamp"]
                }
            }
            
        except Exception as e:
            logger.error(
                "blockchain_execution_error",
                emenda_id=emenda.id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao registrar execução: {str(e)}"
            }
    
    async def register_meta_completion(
        self,
        emenda: EmendaPix,
        meta_number: int
    ) -> dict:
        """
        Registra conclusão de uma meta na blockchain
        
        Args:
            emenda: Entidade da emenda
            meta_number: Número da meta
        
        Returns:
            dict com resultado do registro
        """
        try:
            # Encontrar meta no plano de trabalho
            meta_data = None
            if emenda.plano_trabalho:
                for meta in emenda.plano_trabalho:
                    if meta.get("meta") == meta_number:
                        meta_data = meta
                        break
            
            if not meta_data:
                return {
                    "success": False,
                    "message": f"Meta {meta_number} não encontrada"
                }
            
            block = self.blockchain.register_meta_completion(
                emenda_id=emenda.id,
                meta_number=meta_number,
                meta_data=meta_data
            )
            
            logger.info(
                "meta_registered_blockchain",
                emenda_id=emenda.id,
                meta_number=meta_number,
                block_hash=block["hash"][:16] + "..."
            )
            
            return {
                "success": True,
                "message": f"Meta {meta_number} registrada na blockchain",
                "block": {
                    "index": block["index"],
                    "hash": block["hash"],
                    "timestamp": block["timestamp"]
                }
            }
            
        except Exception as e:
            logger.error(
                "blockchain_meta_error",
                emenda_id=emenda.id,
                meta_number=meta_number,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao registrar meta: {str(e)}"
            }
    
    async def get_audit_trail(self, emenda_id: str) -> dict:
        """
        Obtém trilha de auditoria completa de uma emenda
        
        Args:
            emenda_id: ID da emenda
        
        Returns:
            dict com trilha de auditoria
        """
        try:
            audit_trail = self.blockchain.get_audit_trail(emenda_id)
            
            logger.info(
                "audit_trail_retrieved",
                emenda_id=emenda_id,
                transactions_count=audit_trail["total_transactions"]
            )
            
            return {
                "success": True,
                "audit_trail": audit_trail
            }
            
        except Exception as e:
            logger.error(
                "audit_trail_error",
                emenda_id=emenda_id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao obter trilha de auditoria: {str(e)}"
            }
    
    async def verify_integrity(self) -> dict:
        """
        Verifica integridade da cadeia de blocos
        
        Returns:
            dict com resultado da verificação
        """
        try:
            is_valid = self.blockchain.verify_chain_integrity()
            
            return {
                "success": True,
                "integrity_valid": is_valid,
                "total_blocks": len(self.blockchain.chain),
                "message": "Cadeia íntegra" if is_valid else "Cadeia comprometida"
            }
            
        except Exception as e:
            logger.error("integrity_check_error", error=str(e))
            return {
                "success": False,
                "message": f"Erro ao verificar integridade: {str(e)}"
            }

