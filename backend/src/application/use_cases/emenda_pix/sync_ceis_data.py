"""
Use case para sincronizar dados do CEIS e processos eletrônicos
"""
from typing import Optional
from datetime import datetime
import structlog

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository
from src.infrastructure.external.ceis.client import CEISClient

logger = structlog.get_logger()


class SyncCEISDataUseCase:
    """Sincroniza dados do CEIS e processos eletrônicos para uma emenda"""
    
    def __init__(
        self,
        repository: EmendaPixRepository,
        ceis_client: Optional[CEISClient] = None
    ):
        self.repository = repository
        self.ceis_client = ceis_client or CEISClient()
    
    async def execute(self, emenda_id: str) -> dict:
        """
        Sincroniza dados do CEIS para uma emenda específica
        
        Args:
            emenda_id: ID da emenda
        
        Returns:
            dict com resultado da sincronização
        """
        try:
            # Buscar emenda
            emenda = await self.repository.find_by_id(emenda_id)
            if not emenda:
                return {
                    "success": False,
                    "message": "Emenda não encontrada",
                    "updated": False
                }
            
            if not emenda.processo_sei:
                return {
                    "success": False,
                    "message": "Emenda não possui processo SEI vinculado",
                    "updated": False
                }
            
            logger.info(
                "sync_ceis_started",
                emenda_id=emenda_id,
                processo_sei=emenda.processo_sei
            )
            
            updates = {}
            
            # 1. Buscar plano de trabalho
            plano_trabalho = await self.ceis_client.get_plano_trabalho(
                emenda.processo_sei
            )
            if plano_trabalho:
                updates["plano_trabalho"] = plano_trabalho.get("metas", [])
                updates["numero_metas"] = len(updates["plano_trabalho"])
                logger.info(
                    "plano_trabalho_synced",
                    emenda_id=emenda_id,
                    metas_count=updates["numero_metas"]
                )
            
            # 2. Buscar status das metas
            metas_status = await self.ceis_client.get_metas_status(
                emenda.processo_sei
            )
            if metas_status:
                # Atualizar status das metas no plano de trabalho
                if updates.get("plano_trabalho"):
                    metas_dict = {m.get("meta"): m for m in metas_status}
                    for meta in updates["plano_trabalho"]:
                        meta_num = meta.get("meta")
                        if meta_num in metas_dict:
                            meta["status"] = metas_dict[meta_num].get("status")
                            meta["data_conclusao"] = metas_dict[meta_num].get("data_conclusao")
                    
                    # Contar metas concluídas
                    updates["metas_concluidas"] = sum(
                        1 for m in updates["plano_trabalho"]
                        if m.get("status") == "concluida"
                    )
                    logger.info(
                        "metas_status_synced",
                        emenda_id=emenda_id,
                        concluidas=updates["metas_concluidas"]
                    )
            
            # 3. Buscar entregas
            entregas = await self.ceis_client.get_entregas(
                emenda.processo_sei
            )
            if entregas:
                updates["documentos_comprobatórios"] = [
                    {
                        "tipo": entrega.get("tipo"),
                        "descricao": entrega.get("descricao"),
                        "data": entrega.get("data"),
                        "link": entrega.get("link")
                    }
                    for entrega in entregas
                ]
                logger.info(
                    "entregas_synced",
                    emenda_id=emenda_id,
                    entregas_count=len(entregas)
                )
            
            # 4. Verificar empresa no CEIS (se houver CNPJ)
            if emenda.destinatario_cnpj:
                ceis_info = await self.ceis_client.verificar_empresa_ceis(
                    emenda.destinatario_cnpj
                )
                if ceis_info:
                    # Adicionar alerta se empresa estiver no CEIS
                    if not emenda.alertas:
                        emenda.alertas = []
                    
                    alerta_ceis = {
                        "tipo": "empresa_ceis",
                        "severidade": "alta",
                        "mensagem": f"Empresa destinatária está cadastrada no CEIS: {ceis_info.get('motivo', 'Não informado')}",
                        "data": str(datetime.now().date())
                    }
                    emenda.alertas.append(alerta_ceis)
                    updates["alertas"] = emenda.alertas
                    logger.warning(
                        "empresa_in_ceis",
                        emenda_id=emenda_id,
                        cnpj=emenda.destinatario_cnpj
                    )
            
            # 5. Atualizar emenda com dados sincronizados
            if updates:
                # Atualizar campos da emenda
                if "plano_trabalho" in updates:
                    emenda.plano_trabalho = updates["plano_trabalho"]
                if "numero_metas" in updates:
                    emenda.numero_metas = updates["numero_metas"]
                if "metas_concluidas" in updates:
                    emenda.metas_concluidas = updates["metas_concluidas"]
                if "documentos_comprobatórios" in updates:
                    emenda.documentos_comprobatórios = updates["documentos_comprobatórios"]
                if "alertas" in updates:
                    emenda.alertas = updates["alertas"]
                
                # Salvar emenda atualizada
                await self.repository.save(emenda)
                
                logger.info(
                    "ceis_sync_completed",
                    emenda_id=emenda_id,
                    updates=list(updates.keys())
                )
                
                return {
                    "success": True,
                    "message": "Dados do CEIS sincronizados com sucesso",
                    "updated": True,
                    "updates": list(updates.keys())
                }
            else:
                return {
                    "success": True,
                    "message": "Nenhum dado novo encontrado no CEIS",
                    "updated": False
                }
                
        except Exception as e:
            logger.error(
                "ceis_sync_error",
                emenda_id=emenda_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "success": False,
                "message": f"Erro ao sincronizar dados do CEIS: {str(e)}",
                "updated": False
            }
        finally:
            await self.ceis_client.close()
    
    async def sync_all_emendas_with_ceis(self) -> dict:
        """
        Sincroniza dados do CEIS para todas as emendas que possuem processo SEI
        
        Returns:
            dict com estatísticas da sincronização
        """
        try:
            # Buscar todas as emendas com processo SEI
            all_emendas = await self.repository.find_all(limit=1000)
            emendas_com_sei = [
                e for e in all_emendas
                if e.processo_sei
            ]
            
            logger.info(
                "sync_all_ceis_started",
                total_emendas=len(emendas_com_sei)
            )
            
            stats = {
                "total": len(emendas_com_sei),
                "synced": 0,
                "updated": 0,
                "errors": 0
            }
            
            for emenda in emendas_com_sei:
                result = await self.execute(emenda.id)
                if result["success"]:
                    stats["synced"] += 1
                    if result["updated"]:
                        stats["updated"] += 1
                else:
                    stats["errors"] += 1
            
            logger.info("sync_all_ceis_completed", **stats)
            
            return {
                "success": True,
                "message": f"Sincronização concluída: {stats['synced']} processadas, {stats['updated']} atualizadas",
                **stats
            }
            
        except Exception as e:
            logger.error("sync_all_ceis_error", error=str(e))
            return {
                "success": False,
                "message": f"Erro ao sincronizar: {str(e)}",
                "total": 0,
                "synced": 0,
                "updated": 0,
                "errors": 1
            }

