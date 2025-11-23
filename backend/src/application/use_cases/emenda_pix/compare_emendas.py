"""
Use case para análise comparativa de emendas
"""
from typing import List, Dict, Optional
import structlog

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository

logger = structlog.get_logger()


class CompareEmendasUseCase:
    """Compara emendas similares e gera análises comparativas"""
    
    def __init__(self, repository: EmendaPixRepository):
        self.repository = repository
    
    async def compare_similar_emendas(
        self,
        emenda_id: str,
        area: Optional[str] = None,
        valor_range: Optional[float] = None
    ) -> dict:
        """
        Compara emenda com outras similares
        
        Args:
            emenda_id: ID da emenda a comparar
            area: Área temática (opcional, filtra por área)
            valor_range: Faixa de valor (opcional, percentual de variação)
        
        Returns:
            dict com análise comparativa
        """
        try:
            # Buscar emenda principal
            emenda = await self.repository.find_by_id(emenda_id)
            if not emenda:
                return {
                    "success": False,
                    "message": "Emenda não encontrada"
                }
            
            # Buscar emendas similares
            similar_emendas = await self._find_similar_emendas(
                emenda=emenda,
                area=area,
                valor_range=valor_range
            )
            
            # Gerar análise comparativa
            analysis = self._generate_comparative_analysis(
                emenda=emenda,
                similar_emendas=similar_emendas
            )
            
            logger.info(
                "emendas_compared",
                emenda_id=emenda_id,
                similar_count=len(similar_emendas)
            )
            
            return {
                "success": True,
                "emenda": {
                    "id": emenda.id,
                    "numero_emenda": emenda.numero_emenda,
                    "autor_nome": emenda.autor_nome,
                    "destinatario_nome": emenda.destinatario_nome,
                    "valor_aprovado": emenda.valor_aprovado,
                    "percentual_executado": emenda.percentual_executado,
                    "status_execucao": emenda.status_execucao
                },
                "similar_emendas": [
                    {
                        "id": e.id,
                        "numero_emenda": e.numero_emenda,
                        "autor_nome": e.autor_nome,
                        "destinatario_nome": e.destinatario_nome,
                        "valor_aprovado": e.valor_aprovado,
                        "percentual_executado": e.percentual_executado,
                        "status_execucao": e.status_execucao,
                        "similarity_score": self._calculate_similarity(emenda, e)
                    }
                    for e in similar_emendas
                ],
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(
                "compare_emendas_error",
                emenda_id=emenda_id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao comparar emendas: {str(e)}"
            }
    
    async def benchmark_by_deputado(
        self,
        autor_nome: Optional[str] = None
    ) -> dict:
        """
        Gera benchmarking de execução por deputado
        
        Args:
            autor_nome: Nome do deputado (opcional, se None busca todos)
        
        Returns:
            dict com benchmarking
        """
        try:
            # Buscar todas as emendas
            all_emendas = await self.repository.find_all()
            
            # Agrupar por deputado
            by_deputado: Dict[str, List[EmendaPix]] = {}
            for emenda in all_emendas:
                if autor_nome and emenda.autor_nome != autor_nome:
                    continue
                if emenda.autor_nome not in by_deputado:
                    by_deputado[emenda.autor_nome] = []
                by_deputado[emenda.autor_nome].append(emenda)
            
            # Calcular métricas por deputado
            benchmarks = []
            for deputado, emendas in by_deputado.items():
                total_valor = sum(e.valor_aprovado for e in emendas)
                total_executado = sum(
                    e.valor_aprovado * (e.percentual_executado / 100)
                    for e in emendas
                )
                avg_percentual = sum(e.percentual_executado for e in emendas) / len(emendas)
                
                # Contar status
                status_count = {}
                for e in emendas:
                    status = e.status_execucao
                    status_count[status] = status_count.get(status, 0) + 1
                
                # Contar atrasadas
                atrasadas = sum(1 for e in emendas if e.esta_atrasada())
                
                benchmarks.append({
                    "deputado": deputado,
                    "total_emendas": len(emendas),
                    "valor_total_aprovado": total_valor,
                    "valor_total_executado": total_executado,
                    "percentual_medio_executado": round(avg_percentual, 2),
                    "emendas_atrasadas": atrasadas,
                    "taxa_atraso": round((atrasadas / len(emendas)) * 100, 2) if emendas else 0,
                    "status_distribution": status_count
                })
            
            # Ordenar por percentual médio executado
            benchmarks.sort(key=lambda x: x["percentual_medio_executado"], reverse=True)
            
            logger.info(
                "benchmark_by_deputado",
                total_deputados=len(benchmarks),
                filtered_deputado=autor_nome
            )
            
            return {
                "success": True,
                "benchmarks": benchmarks,
                "summary": {
                    "total_deputados": len(benchmarks),
                    "avg_percentual_executado": round(
                        sum(b["percentual_medio_executado"] for b in benchmarks) / len(benchmarks),
                        2
                    ) if benchmarks else 0
                }
            }
            
        except Exception as e:
            logger.error("benchmark_by_deputado_error", error=str(e))
            return {
                "success": False,
                "message": f"Erro ao gerar benchmarking: {str(e)}"
            }
    
    async def benchmark_by_municipio(
        self,
        municipio: Optional[str] = None
    ) -> dict:
        """
        Gera benchmarking de execução por município
        
        Args:
            municipio: Nome do município (opcional, se None busca todos)
        
        Returns:
            dict com benchmarking
        """
        try:
            # Buscar todas as emendas
            all_emendas = await self.repository.find_all()
            
            # Agrupar por município
            by_municipio: Dict[str, List[EmendaPix]] = {}
            for emenda in all_emendas:
                if municipio and emenda.destinatario_nome != municipio:
                    continue
                if emenda.destinatario_nome not in by_municipio:
                    by_municipio[emenda.destinatario_nome] = []
                by_municipio[emenda.destinatario_nome].append(emenda)
            
            # Calcular métricas por município
            benchmarks = []
            for municipio_nome, emendas in by_municipio.items():
                total_valor = sum(e.valor_aprovado for e in emendas)
                total_executado = sum(
                    e.valor_aprovado * (e.percentual_executado / 100)
                    for e in emendas
                )
                avg_percentual = sum(e.percentual_executado for e in emendas) / len(emendas)
                
                # Contar atrasadas
                atrasadas = sum(1 for e in emendas if e.esta_atrasada())
                
                benchmarks.append({
                    "municipio": municipio_nome,
                    "total_emendas": len(emendas),
                    "valor_total_aprovado": total_valor,
                    "valor_total_executado": total_executado,
                    "percentual_medio_executado": round(avg_percentual, 2),
                    "emendas_atrasadas": atrasadas,
                    "taxa_atraso": round((atrasadas / len(emendas)) * 100, 2) if emendas else 0
                })
            
            # Ordenar por percentual médio executado
            benchmarks.sort(key=lambda x: x["percentual_medio_executado"], reverse=True)
            
            logger.info(
                "benchmark_by_municipio",
                total_municipios=len(benchmarks),
                filtered_municipio=municipio
            )
            
            return {
                "success": True,
                "benchmarks": benchmarks,
                "summary": {
                    "total_municipios": len(benchmarks),
                    "avg_percentual_executado": round(
                        sum(b["percentual_medio_executado"] for b in benchmarks) / len(benchmarks),
                        2
                    ) if benchmarks else 0
                }
            }
            
        except Exception as e:
            logger.error("benchmark_by_municipio_error", error=str(e))
            return {
                "success": False,
                "message": f"Erro ao gerar benchmarking: {str(e)}"
            }
    
    async def identify_patterns_and_anomalies(self) -> dict:
        """
        Identifica padrões e anomalias nas emendas
        
        Returns:
            dict com padrões e anomalias identificados
        """
        try:
            all_emendas = await self.repository.find_all()
            
            patterns = []
            anomalies = []
            
            # Padrão 1: Emendas com execução muito baixa
            low_execution = [
                e for e in all_emendas
                if e.percentual_executado < 20 and e.status_execucao != "cancelada"
            ]
            if low_execution:
                patterns.append({
                    "type": "baixa_execucao",
                    "description": f"{len(low_execution)} emendas com execução abaixo de 20%",
                    "count": len(low_execution),
                    "emendas": [
                        {
                            "id": e.id,
                            "numero_emenda": e.numero_emenda,
                            "percentual_executado": e.percentual_executado
                        }
                        for e in low_execution[:10]  # Limitar a 10
                    ]
                })
            
            # Padrão 2: Emendas atrasadas
            delayed = [e for e in all_emendas if e.esta_atrasada()]
            if delayed:
                patterns.append({
                    "type": "atraso",
                    "description": f"{len(delayed)} emendas atrasadas",
                    "count": len(delayed),
                    "emendas": [
                        {
                            "id": e.id,
                            "numero_emenda": e.numero_emenda,
                            "dias_atraso": (e.data_prevista_conclusao - e.data_inicio).days if e.data_prevista_conclusao and e.data_inicio else None
                        }
                        for e in delayed[:10]
                    ]
                })
            
            # Anomalia 1: Valores muito altos
            avg_valor = sum(e.valor_aprovado for e in all_emendas) / len(all_emendas) if all_emendas else 0
            high_value = [
                e for e in all_emendas
                if e.valor_aprovado > avg_valor * 3
            ]
            if high_value:
                anomalies.append({
                    "type": "valor_alto",
                    "description": f"{len(high_value)} emendas com valor muito acima da média",
                    "count": len(high_value),
                    "avg_valor": avg_valor,
                    "emendas": [
                        {
                            "id": e.id,
                            "numero_emenda": e.numero_emenda,
                            "valor_aprovado": e.valor_aprovado,
                            "diferenca_media": e.valor_aprovado - avg_valor
                        }
                        for e in high_value[:10]
                    ]
                })
            
            # Anomalia 2: Execução 100% muito rápida
            fast_execution = [
                e for e in all_emendas
                if e.percentual_executado == 100 and e.status_execucao == "concluida"
            ]
            if fast_execution:
                anomalies.append({
                    "type": "execucao_rapida",
                    "description": f"{len(fast_execution)} emendas concluídas rapidamente",
                    "count": len(fast_execution),
                    "emendas": [
                        {
                            "id": e.id,
                            "numero_emenda": e.numero_emenda,
                            "percentual_executado": e.percentual_executado
                        }
                        for e in fast_execution[:10]
                    ]
                })
            
            logger.info(
                "patterns_anomalies_identified",
                patterns_count=len(patterns),
                anomalies_count=len(anomalies)
            )
            
            return {
                "success": True,
                "patterns": patterns,
                "anomalies": anomalies,
                "summary": {
                    "total_emendas": len(all_emendas),
                    "patterns_found": len(patterns),
                    "anomalies_found": len(anomalies)
                }
            }
            
        except Exception as e:
            logger.error("identify_patterns_error", error=str(e))
            return {
                "success": False,
                "message": f"Erro ao identificar padrões: {str(e)}"
            }
    
    async def _find_similar_emendas(
        self,
        emenda: EmendaPix,
        area: Optional[str] = None,
        valor_range: Optional[float] = None
    ) -> List[EmendaPix]:
        """Encontra emendas similares"""
        all_emendas = await self.repository.find_all()
        
        similar = []
        for e in all_emendas:
            if e.id == emenda.id:
                continue
            
            # Filtrar por área se especificado
            if area and e.area and e.area != area:
                continue
            
            # Filtrar por faixa de valor
            if valor_range:
                min_valor = emenda.valor_aprovado * (1 - valor_range / 100)
                max_valor = emenda.valor_aprovado * (1 + valor_range / 100)
                if not (min_valor <= e.valor_aprovado <= max_valor):
                    continue
            
            similar.append(e)
        
        # Ordenar por similaridade
        similar.sort(
            key=lambda x: self._calculate_similarity(emenda, x),
            reverse=True
        )
        
        return similar[:10]  # Retornar top 10
    
    def _calculate_similarity(self, emenda1: EmendaPix, emenda2: EmendaPix) -> float:
        """Calcula score de similaridade entre duas emendas"""
        score = 0.0
        
        # Mesma área temática (30%)
        if emenda1.area and emenda2.area and emenda1.area == emenda2.area:
            score += 0.3
        elif not emenda1.area and not emenda2.area:
            # Se ambas não têm área, dar pontuação parcial
            score += 0.15
        
        # Valor similar (30%)
        valor_diff = abs(emenda1.valor_aprovado - emenda2.valor_aprovado)
        max_valor = max(emenda1.valor_aprovado, emenda2.valor_aprovado)
        if max_valor > 0:
            valor_similarity = 1 - (valor_diff / max_valor)
            score += 0.3 * max(0, valor_similarity)
        
        # Mesmo município (20%)
        if emenda1.destinatario_nome == emenda2.destinatario_nome:
            score += 0.2
        
        # Status similar (20%)
        if emenda1.status_execucao == emenda2.status_execucao:
            score += 0.2
        
        return round(score, 2)
    
    def _generate_comparative_analysis(
        self,
        emenda: EmendaPix,
        similar_emendas: List[EmendaPix]
    ) -> Dict:
        """Gera análise comparativa"""
        if not similar_emendas:
            return {
                "message": "Nenhuma emenda similar encontrada",
                "comparisons": []
            }
        
        avg_percentual = sum(e.percentual_executado for e in similar_emendas) / len(similar_emendas)
        avg_valor = sum(e.valor_aprovado for e in similar_emendas) / len(similar_emendas)
        
        return {
            "emenda_percentual": emenda.percentual_executado,
            "media_similares_percentual": round(avg_percentual, 2),
            "diferenca_percentual": round(emenda.percentual_executado - avg_percentual, 2),
            "emenda_valor": emenda.valor_aprovado,
            "media_similares_valor": round(avg_valor, 2),
            "diferenca_valor": round(emenda.valor_aprovado - avg_valor, 2),
            "posicao_ranking": self._calculate_ranking_position(emenda, similar_emendas),
            "insights": self._generate_insights(emenda, similar_emendas, avg_percentual)
        }
    
    def _calculate_ranking_position(
        self,
        emenda: EmendaPix,
        similar_emendas: List[EmendaPix]
    ) -> int:
        """Calcula posição no ranking de execução"""
        sorted_emendas = sorted(
            similar_emendas + [emenda],
            key=lambda x: x.percentual_executado,
            reverse=True
        )
        return sorted_emendas.index(emenda) + 1
    
    def _generate_insights(
        self,
        emenda: EmendaPix,
        similar_emendas: List[EmendaPix],
        avg_percentual: float
    ) -> List[str]:
        """Gera insights comparativos"""
        insights = []
        
        if emenda.percentual_executado > avg_percentual + 10:
            insights.append(
                f"Execução {emenda.percentual_executado - avg_percentual:.1f}% acima da média de emendas similares"
            )
        elif emenda.percentual_executado < avg_percentual - 10:
            insights.append(
                f"Execução {avg_percentual - emenda.percentual_executado:.1f}% abaixo da média de emendas similares"
            )
        
        if emenda.esta_atrasada():
            insights.append("Emenda está atrasada em relação ao prazo")
        
        return insights

