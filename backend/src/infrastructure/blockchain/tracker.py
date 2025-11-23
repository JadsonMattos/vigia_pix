"""
Sistema de Rastreabilidade Imutável (Blockchain Conceitual)
Garante transparência total e auditável das emendas

Nota: Para o hackathon, implementamos um sistema conceitual que demonstra
a viabilidade de blockchain. Em produção, pode ser integrado com uma
blockchain real (Ethereum, Hyperledger, etc.).
"""
import hashlib
import json
from typing import List, Dict, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class BlockchainTracker:
    """
    Rastreador de blockchain conceitual para emendas
    
    Implementa conceitos de blockchain:
    - Hash imutável de transações
    - Cadeia de blocos
    - Rastreabilidade completa
    - Auditoria transparente
    """
    
    def __init__(self):
        self.chain: List[Dict] = []
        self.pending_transactions: List[Dict] = []
    
    def create_block(
        self,
        emenda_id: str,
        transaction_type: str,
        data: Dict,
        previous_hash: Optional[str] = None
    ) -> Dict:
        """
        Cria um novo bloco na cadeia
        
        Args:
            emenda_id: ID da emenda
            transaction_type: Tipo de transação (criacao, execucao, entrega, etc.)
            data: Dados da transação
            previous_hash: Hash do bloco anterior
        
        Returns:
            Dicionário com o bloco criado
        """
        # Obter hash do bloco anterior
        if previous_hash is None:
            previous_hash = self.get_last_hash()
        
        # Criar bloco
        block = {
            "index": len(self.chain) + 1,
            "timestamp": datetime.now().isoformat(),
            "emenda_id": emenda_id,
            "transaction_type": transaction_type,
            "data": data,
            "previous_hash": previous_hash,
            "hash": None  # Será calculado
        }
        
        # Calcular hash do bloco
        block["hash"] = self._calculate_hash(block)
        
        # Adicionar à cadeia
        self.chain.append(block)
        
        logger.info(
            "block_created",
            emenda_id=emenda_id,
            transaction_type=transaction_type,
            block_index=block["index"],
            block_hash=block["hash"][:16] + "..."
        )
        
        return block
    
    def register_emenda_creation(
        self,
        emenda_id: str,
        emenda_data: Dict
    ) -> Dict:
        """
        Registra criação de uma emenda na blockchain
        
        Args:
            emenda_id: ID da emenda
            emenda_data: Dados da emenda
        
        Returns:
            Bloco criado
        """
        transaction_data = {
            "action": "emenda_created",
            "numero_emenda": emenda_data.get("numero_emenda"),
            "ano": emenda_data.get("ano"),
            "autor_nome": emenda_data.get("autor_nome"),
            "destinatario_nome": emenda_data.get("destinatario_nome"),
            "valor_aprovado": emenda_data.get("valor_aprovado"),
            "plano_trabalho": emenda_data.get("plano_trabalho", []),
            "timestamp": datetime.now().isoformat()
        }
        
        return self.create_block(
            emenda_id=emenda_id,
            transaction_type="criacao",
            data=transaction_data
        )
    
    def register_execution_update(
        self,
        emenda_id: str,
        execution_data: Dict
    ) -> Dict:
        """
        Registra atualização de execução na blockchain
        
        Args:
            emenda_id: ID da emenda
            execution_data: Dados da execução
        
        Returns:
            Bloco criado
        """
        transaction_data = {
            "action": "execution_updated",
            "valor_pago": execution_data.get("valor_pago"),
            "percentual_executado": execution_data.get("percentual_executado"),
            "status_execucao": execution_data.get("status_execucao"),
            "metas_concluidas": execution_data.get("metas_concluidas"),
            "timestamp": datetime.now().isoformat()
        }
        
        return self.create_block(
            emenda_id=emenda_id,
            transaction_type="execucao",
            data=transaction_data
        )
    
    def register_meta_completion(
        self,
        emenda_id: str,
        meta_number: int,
        meta_data: Dict
    ) -> Dict:
        """
        Registra conclusão de uma meta na blockchain
        
        Args:
            emenda_id: ID da emenda
            meta_number: Número da meta
            meta_data: Dados da meta
        
        Returns:
            Bloco criado
        """
        transaction_data = {
            "action": "meta_completed",
            "meta": meta_number,
            "descricao": meta_data.get("descricao"),
            "valor": meta_data.get("valor"),
            "data_conclusao": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
        return self.create_block(
            emenda_id=emenda_id,
            transaction_type="entrega",
            data=transaction_data
        )
    
    def register_alert(
        self,
        emenda_id: str,
        alert_data: Dict
    ) -> Dict:
        """
        Registra um alerta na blockchain
        
        Args:
            emenda_id: ID da emenda
            alert_data: Dados do alerta
        
        Returns:
            Bloco criado
        """
        transaction_data = {
            "action": "alert_generated",
            "tipo": alert_data.get("tipo"),
            "severidade": alert_data.get("severidade"),
            "mensagem": alert_data.get("mensagem"),
            "timestamp": datetime.now().isoformat()
        }
        
        return self.create_block(
            emenda_id=emenda_id,
            transaction_type="alerta",
            data=transaction_data
        )
    
    def get_emenda_history(
        self,
        emenda_id: str
    ) -> List[Dict]:
        """
        Obtém histórico completo de uma emenda na blockchain
        
        Args:
            emenda_id: ID da emenda
        
        Returns:
            Lista de blocos relacionados à emenda
        """
        history = [
            block for block in self.chain
            if block.get("emenda_id") == emenda_id
        ]
        
        logger.info(
            "emenda_history_retrieved",
            emenda_id=emenda_id,
            blocks_count=len(history)
        )
        
        return history
    
    def verify_chain_integrity(self) -> bool:
        """
        Verifica integridade da cadeia de blocos
        
        Returns:
            True se a cadeia está íntegra, False caso contrário
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verificar hash do bloco anterior
            if current_block["previous_hash"] != previous_block["hash"]:
                logger.error(
                    "chain_integrity_failed",
                    block_index=i,
                    expected_hash=previous_block["hash"],
                    actual_hash=current_block["previous_hash"]
                )
                return False
            
            # Verificar hash do bloco atual
            calculated_hash = self._calculate_hash(current_block)
            if current_block["hash"] != calculated_hash:
                logger.error(
                    "block_hash_mismatch",
                    block_index=i,
                    expected_hash=calculated_hash,
                    actual_hash=current_block["hash"]
                )
                return False
        
        logger.info("chain_integrity_verified", total_blocks=len(self.chain))
        return True
    
    def get_last_hash(self) -> str:
        """Obtém hash do último bloco"""
        if not self.chain:
            return "0" * 64  # Genesis block hash
        return self.chain[-1]["hash"]
    
    def _calculate_hash(self, block: Dict) -> str:
        """
        Calcula hash SHA-256 de um bloco
        
        Args:
            block: Dicionário com dados do bloco
        
        Returns:
            Hash hexadecimal
        """
        # Criar cópia sem o hash para cálculo
        block_copy = {k: v for k, v in block.items() if k != "hash"}
        block_string = json.dumps(block_copy, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def get_audit_trail(
        self,
        emenda_id: str
    ) -> Dict:
        """
        Gera trilha de auditoria completa de uma emenda
        
        Args:
            emenda_id: ID da emenda
        
        Returns:
            Dicionário com trilha de auditoria
        """
        history = self.get_emenda_history(emenda_id)
        
        audit_trail = {
            "emenda_id": emenda_id,
            "total_transactions": len(history),
            "chain_integrity": self.verify_chain_integrity(),
            "transactions": []
        }
        
        for block in history:
            audit_trail["transactions"].append({
                "index": block["index"],
                "timestamp": block["timestamp"],
                "type": block["transaction_type"],
                "action": block["data"].get("action"),
                "hash": block["hash"],
                "previous_hash": block["previous_hash"],
                "data": block["data"]
            })
        
        logger.info(
            "audit_trail_generated",
            emenda_id=emenda_id,
            transactions_count=len(history)
        )
        
        return audit_trail
    
    def export_chain(self) -> List[Dict]:
        """Exporta toda a cadeia para auditoria externa"""
        return self.chain.copy()


# Instância global do tracker
_global_tracker: Optional[BlockchainTracker] = None


def get_blockchain_tracker() -> BlockchainTracker:
    """Obtém instância global do blockchain tracker"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = BlockchainTracker()
    return _global_tracker


# Nota para o pitch:
# "Implementamos um sistema de rastreabilidade imutável baseado em conceitos
#  de blockchain. Cada transação relacionada à emenda é registrada em um bloco
#  com hash criptográfico, garantindo que nenhuma alteração possa ser feita
#  sem ser detectada. Em produção, isso pode ser integrado com uma blockchain
#  real (Ethereum, Hyperledger) para máxima transparência e auditabilidade."

