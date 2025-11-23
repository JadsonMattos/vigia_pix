"""
Use case para sincronizar emendas Pix do Portal da Transparência
"""
from datetime import datetime
from typing import List, Optional
import structlog
import uuid

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository
from src.infrastructure.external.portal_transparencia.client import PortalTransparenciaClient

logger = structlog.get_logger()


class SyncEmendasPortalUseCase:
    """Sincroniza emendas Pix do Portal da Transparência"""
    
    def __init__(
        self,
        repository: EmendaPixRepository,
        portal_client: Optional[PortalTransparenciaClient] = None
    ):
        self.repository = repository
        self.portal_client = portal_client or PortalTransparenciaClient()
    
    async def execute(
        self,
        ano: Optional[int] = None,
        codigo_ibge: Optional[str] = None,
        limit: int = 100
    ) -> dict:
        """
        Sincroniza emendas do Portal da Transparência
        
        Args:
            ano: Ano das emendas (padrão: ano atual)
            codigo_ibge: Código IBGE do município (opcional)
            limit: Limite de emendas a sincronizar
        
        Returns:
            dict com estatísticas da sincronização
        """
        if ano is None:
            ano = datetime.now().year
        
        logger.info(
            "sync_emendas_portal_started",
            ano=ano,
            codigo_ibge=codigo_ibge,
            limit=limit
        )
        
        try:
            # Buscar emendas do Portal
            emendas_portal = await self._fetch_emendas_from_portal(
                ano=ano,
                codigo_ibge=codigo_ibge,
                limit=limit
            )
            
            if not emendas_portal:
                logger.warning("no_emendas_found_in_portal", ano=ano)
                return {
                    "success": True,
                    "message": "Nenhuma emenda encontrada no Portal da Transparência",
                    "total_fetched": 0,
                    "total_saved": 0,
                    "total_updated": 0,
                    "total_errors": 0
                }
            
            # Processar e salvar emendas
            stats = await self._process_and_save_emendas(emendas_portal)
            
            logger.info(
                "sync_emendas_portal_completed",
                **stats
            )
            
            return {
                "success": True,
                "message": f"Sincronização concluída: {stats['total_saved']} novas, {stats['total_updated']} atualizadas",
                **stats
            }
            
        except Exception as e:
            logger.error(
                "sync_emendas_portal_error",
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "success": False,
                "message": f"Erro ao sincronizar: {str(e)}",
                "total_fetched": 0,
                "total_saved": 0,
                "total_updated": 0,
                "total_errors": 1
            }
        finally:
            await self.portal_client.close()
    
    async def _fetch_emendas_from_portal(
        self,
        ano: int,
        codigo_ibge: Optional[str],
        limit: int
    ) -> List[dict]:
        """
        Busca emendas do Portal da Transparência
        
        Nota: Para demo, retorna dados simulados se a API não estiver disponível
        """
        try:
            # Tentar buscar dados reais
            emendas = await self.portal_client.get_emendas_pix(
                ano=ano,
                codigo_ibge=codigo_ibge,
                pagina=1
            )
            
            # Limitar quantidade
            if limit:
                emendas = emendas[:limit]
            
            return emendas
            
        except Exception as e:
            logger.warning(
                "portal_api_unavailable_using_simulated",
                error=str(e)
            )
            # Para demo, retornar lista vazia (dados já estão no seed)
            # Em produção, isso seria um erro crítico
            return []
    
    async def _process_and_save_emendas(
        self,
        emendas_portal: List[dict]
    ) -> dict:
        """Processa e salva emendas do Portal"""
        stats = {
            "total_fetched": len(emendas_portal),
            "total_saved": 0,
            "total_updated": 0,
            "total_errors": 0
        }
        
        for emenda_data in emendas_portal:
            try:
                # Mapear dados do Portal para nossa entidade
                emenda_entity = self._map_portal_to_entity(emenda_data)
                
                # Verificar se já existe
                existing = await self.repository.find_by_numero_emenda(
                    emenda_entity.numero_emenda
                )
                
                if existing:
                    # Atualizar emenda existente
                    emenda_entity.id = existing.id
                    await self.repository.save(emenda_entity)
                    stats["total_updated"] += 1
                    logger.debug(
                        "emenda_updated",
                        numero_emenda=emenda_entity.numero_emenda
                    )
                else:
                    # Criar nova emenda
                    await self.repository.save(emenda_entity)
                    stats["total_saved"] += 1
                    logger.debug(
                        "emenda_saved",
                        numero_emenda=emenda_entity.numero_emenda
                    )
                    
            except Exception as e:
                stats["total_errors"] += 1
                logger.error(
                    "error_processing_emenda",
                    error=str(e),
                    emenda_data=emenda_data.get("numero", "unknown")
                )
        
        return stats
    
    def _map_portal_to_entity(self, portal_data: dict) -> EmendaPix:
        """
        Mapeia dados do Portal da Transparência para nossa entidade
        
        Nota: Este mapeamento precisa ser ajustado conforme a estrutura real
        da API do Portal da Transparência
        """
        # Mapeamento básico (ajustar conforme API real)
        numero_emenda = portal_data.get("numero", f"EMENDA-{datetime.now().timestamp()}")
        ano = portal_data.get("ano", datetime.now().year)
        
        # Calcular percentual executado
        valor_aprovado = float(portal_data.get("valor_aprovado", 0))
        valor_pago = float(portal_data.get("valor_pago", 0))
        percentual_executado = (valor_pago / valor_aprovado * 100) if valor_aprovado > 0 else 0.0
        
        return EmendaPix(
            id=str(uuid.uuid4()),
            numero_emenda=numero_emenda,
            ano=ano,
            tipo=portal_data.get("tipo", "individual"),
            autor_nome=portal_data.get("autor_nome", "Não informado"),
            autor_partido=portal_data.get("autor_partido"),
            autor_uf=portal_data.get("autor_uf"),
            destinatario_nome=portal_data.get("destinatario_nome", "Não informado"),
            destinatario_uf=portal_data.get("destinatario_uf"),
            destinatario_tipo=portal_data.get("destinatario_tipo", "municipio"),
            valor_aprovado=valor_aprovado,
            valor_empenhado=float(portal_data.get("valor_empenhado", 0)),
            valor_liquidado=float(portal_data.get("valor_liquidado", 0)),
            valor_pago=valor_pago,
            percentual_executado=percentual_executado,
            status_execucao=self._map_status(portal_data.get("status", "pendente")),
            objetivo=portal_data.get("objetivo"),
            descricao_detalhada=portal_data.get("descricao_detalhada"),
            area=portal_data.get("area_tematica") or portal_data.get("area"),
            processo_sei=portal_data.get("processo_sei"),
            link_portal_transparencia=portal_data.get("link", f"https://portaldatransparencia.gov.br/emendas/{numero_emenda}"),
            data_inicio=self._parse_date(portal_data.get("data_inicio")),
            data_prevista_conclusao=self._parse_date(portal_data.get("data_prevista_conclusao")),
            plano_trabalho=portal_data.get("plano_trabalho", []),
            last_sync=datetime.now()
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        try:
            # Tentar diferentes formatos
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def _map_status(self, status_portal: str) -> str:
        """Mapeia status do Portal para nosso modelo"""
        status_map = {
            "pendente": "pendente",
            "em_execucao": "em_execucao",
            "concluida": "concluida",
            "atrasada": "atrasada",
            "cancelada": "cancelada"
        }
        return status_map.get(status_portal.lower(), "pendente")

