"""
Use case para geração de relatórios e exportação
"""
from typing import List, Dict, Optional
import csv
import io
import json
from datetime import datetime
import structlog

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository

logger = structlog.get_logger()


class GenerateReportsUseCase:
    """Gera relatórios e exporta dados"""
    
    def __init__(self, repository: EmendaPixRepository):
        self.repository = repository
    
    async def export_to_csv(
        self,
        filters: Optional[Dict] = None
    ) -> str:
        """
        Exporta emendas para CSV
        
        Args:
            filters: Filtros opcionais (status, autor, destinatario, etc.)
        
        Returns:
            String CSV
        """
        try:
            # Buscar emendas
            emendas = await self._get_filtered_emendas(filters)
            
            # Criar CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Cabeçalho
            writer.writerow([
                "Número Emenda",
                "Ano",
                "Autor",
                "Destinatário",
                "Valor Aprovado",
                "Valor Pago",
                "Percentual Executado",
                "Status Execução",
                "Data Início",
                "Data Vencimento",
                "Processo CEIS",
                "Link Portal Transparência"
            ])
            
            # Dados
            for emenda in emendas:
                writer.writerow([
                    emenda.numero_emenda,
                    emenda.ano,
                    emenda.autor_nome,
                    emenda.destinatario_nome,
                    emenda.valor_aprovado,
                    emenda.valor_pago,
                    emenda.percentual_executado,
                    emenda.status_execucao,
                    emenda.data_inicio.isoformat() if emenda.data_inicio else "",
                    emenda.data_vencimento.isoformat() if emenda.data_vencimento else "",
                    emenda.processo_ceis or "",
                    emenda.link_portal_transparencia or ""
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(
                "csv_exported",
                emendas_count=len(emendas),
                filters=filters
            )
            
            return csv_content
            
        except Exception as e:
            logger.error("csv_export_error", error=str(e))
            raise
    
    async def export_to_json(
        self,
        filters: Optional[Dict] = None
    ) -> str:
        """
        Exporta emendas para JSON
        
        Args:
            filters: Filtros opcionais
        
        Returns:
            String JSON
        """
        try:
            # Buscar emendas
            emendas = await self._get_filtered_emendas(filters)
            
            # Converter para dict
            data = []
            for emenda in emendas:
                data.append({
                    "id": emenda.id,
                    "numero_emenda": emenda.numero_emenda,
                    "ano": emenda.ano,
                    "autor_nome": emenda.autor_nome,
                    "destinatario_nome": emenda.destinatario_nome,
                    "valor_aprovado": emenda.valor_aprovado,
                    "valor_pago": emenda.valor_pago,
                    "percentual_executado": emenda.percentual_executado,
                    "status_execucao": emenda.status_execucao,
                    "data_inicio": emenda.data_inicio.isoformat() if emenda.data_inicio else None,
                    "data_vencimento": emenda.data_vencimento.isoformat() if emenda.data_vencimento else None,
                    "processo_ceis": emenda.processo_ceis,
                    "link_portal_transparencia": emenda.link_portal_transparencia,
                    "plano_trabalho": emenda.plano_trabalho
                })
            
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            
            logger.info(
                "json_exported",
                emendas_count=len(emendas),
                filters=filters
            )
            
            return json_content
            
        except Exception as e:
            logger.error("json_export_error", error=str(e))
            raise
    
    async def generate_summary_report(
        self,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Gera relatório resumo
        
        Args:
            filters: Filtros opcionais
        
        Returns:
            dict com resumo
        """
        try:
            emendas = await self._get_filtered_emendas(filters)
            
            if not emendas:
                return {
                    "success": False,
                    "message": "Nenhuma emenda encontrada"
                }
            
            total_valor = sum(e.valor_aprovado for e in emendas)
            total_executado = sum(
                e.valor_aprovado * (e.percentual_executado / 100)
                for e in emendas
            )
            avg_percentual = sum(e.percentual_executado for e in emendas) / len(emendas)
            
            # Status distribution
            status_count = {}
            for e in emendas:
                status = e.status_execucao
                status_count[status] = status_count.get(status, 0) + 1
            
            # Atrasadas
            atrasadas = sum(1 for e in emendas if e.esta_atrasada())
            
            # Por deputado
            by_deputado = {}
            for e in emendas:
                if e.autor_nome not in by_deputado:
                    by_deputado[e.autor_nome] = {
                        "count": 0,
                        "valor_total": 0,
                        "percentual_medio": 0
                    }
                by_deputado[e.autor_nome]["count"] += 1
                by_deputado[e.autor_nome]["valor_total"] += e.valor_aprovado
            
            # Por município
            by_municipio = {}
            for e in emendas:
                if e.destinatario_nome not in by_municipio:
                    by_municipio[e.destinatario_nome] = {
                        "count": 0,
                        "valor_total": 0,
                        "percentual_medio": 0
                    }
                by_municipio[e.destinatario_nome]["count"] += 1
                by_municipio[e.destinatario_nome]["valor_total"] += e.valor_aprovado
            
            report = {
                "success": True,
                "periodo": {
                    "data_geracao": datetime.now().isoformat(),
                    "filtros_aplicados": filters or {}
                },
                "resumo_geral": {
                    "total_emendas": len(emendas),
                    "valor_total_aprovado": round(total_valor, 2),
                    "valor_total_executado": round(total_executado, 2),
                    "percentual_medio_executado": round(avg_percentual, 2),
                    "emendas_atrasadas": atrasadas,
                    "taxa_atraso": round((atrasadas / len(emendas)) * 100, 2) if emendas else 0
                },
                "distribuicao_status": status_count,
                "por_deputado": {
                    k: {
                        "count": v["count"],
                        "valor_total": round(v["valor_total"], 2)
                    }
                    for k, v in by_deputado.items()
                },
                "por_municipio": {
                    k: {
                        "count": v["count"],
                        "valor_total": round(v["valor_total"], 2)
                    }
                    for k, v in by_municipio.items()
                }
            }
            
            logger.info("summary_report_generated", emendas_count=len(emendas))
            
            return report
            
        except Exception as e:
            logger.error("summary_report_error", error=str(e))
            return {
                "success": False,
                "message": f"Erro ao gerar relatório: {str(e)}"
            }
    
    async def _get_filtered_emendas(
        self,
        filters: Optional[Dict] = None
    ) -> List[EmendaPix]:
        """Busca emendas com filtros"""
        all_emendas = await self.repository.find_all()
        
        if not filters:
            return all_emendas
        
        filtered = []
        for emenda in all_emendas:
            # Filtro por status
            if "status" in filters and emenda.status_execucao != filters["status"]:
                continue
            
            # Filtro por autor
            if "autor" in filters and filters["autor"].lower() not in emenda.autor_nome.lower():
                continue
            
            # Filtro por destinatário
            if "destinatario" in filters and filters["destinatario"].lower() not in emenda.destinatario_nome.lower():
                continue
            
            # Filtro por ano
            if "ano" in filters and emenda.ano != filters["ano"]:
                continue
            
            # Filtro por valor mínimo
            if "valor_min" in filters and emenda.valor_aprovado < filters["valor_min"]:
                continue
            
            # Filtro por valor máximo
            if "valor_max" in filters and emenda.valor_aprovado > filters["valor_max"]:
                continue
            
            filtered.append(emenda)
        
        return filtered

