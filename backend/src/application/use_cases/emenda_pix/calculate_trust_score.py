"""
Use case para calcular Trust Score (Índice de Integridade) de uma emenda
"""
from typing import Dict, List
import structlog

from src.domain.entities.emenda_pix import EmendaPix

logger = structlog.get_logger()


class CalculateTrustScoreUseCase:
    """Calcula Trust Score (0-100) baseado em múltiplos fatores"""
    
    def calculate(self, emenda: EmendaPix) -> Dict:
        """
        Calcula Trust Score de uma emenda
        
        Fatores considerados:
        - Execução conforme plano (30%)
        - Tempo de execução (20%)
        - Documentação completa (20%)
        - Análise de IA - risco de desvio (20%)
        - Histórico de mudanças (10%)
        
        Returns:
            dict com score e detalhamento
        """
        try:
            score = 100.0
            factors = {}
            
            # Fator 1: Execução conforme plano (30%)
            execution_score = self._calculate_execution_score(emenda)
            factors["execucao"] = {
                "score": execution_score,
                "weight": 0.30,
                "contribution": execution_score * 0.30,
                "details": self._get_execution_details(emenda)
            }
            score = score - (100 - execution_score) * 0.30
            
            # Fator 2: Tempo de execução (20%)
            timing_score = self._calculate_timing_score(emenda)
            factors["tempo"] = {
                "score": timing_score,
                "weight": 0.20,
                "contribution": timing_score * 0.20,
                "details": self._get_timing_details(emenda)
            }
            score = score - (100 - timing_score) * 0.20
            
            # Fator 3: Documentação completa (20%)
            documentation_score = self._calculate_documentation_score(emenda)
            factors["documentacao"] = {
                "score": documentation_score,
                "weight": 0.20,
                "contribution": documentation_score * 0.20,
                "details": self._get_documentation_details(emenda)
            }
            score = score - (100 - documentation_score) * 0.20
            
            # Fator 4: Risco de desvio (IA) (20%)
            risk_score = self._calculate_risk_score(emenda)
            factors["risco"] = {
                "score": risk_score,
                "weight": 0.20,
                "contribution": risk_score * 0.20,
                "details": self._get_risk_details(emenda)
            }
            score = score - (100 - risk_score) * 0.20
            
            # Fator 5: Histórico de mudanças (10%)
            history_score = self._calculate_history_score(emenda)
            factors["historico"] = {
                "score": history_score,
                "weight": 0.10,
                "contribution": history_score * 0.10,
                "details": self._get_history_details(emenda)
            }
            score = score - (100 - history_score) * 0.10
            
            # Garantir score entre 0 e 100
            final_score = max(0.0, min(100.0, score))
            
            # Determinar nível
            level = self._get_score_level(final_score)
            
            logger.info(
                "trust_score_calculated",
                emenda_id=emenda.id,
                score=final_score,
                level=level
            )
            
            return {
                "success": True,
                "trust_score": round(final_score, 2),
                "level": level,
                "factors": factors,
                "recommendations": self._get_recommendations(final_score, factors)
            }
            
        except Exception as e:
            logger.error(
                "calculate_trust_score_error",
                emenda_id=emenda.id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao calcular Trust Score: {str(e)}"
            }
    
    def _calculate_execution_score(self, emenda: EmendaPix) -> float:
        """Calcula score de execução (0-100)"""
        if emenda.percentual_executado >= 100:
            return 100.0
        elif emenda.percentual_executado >= 80:
            return 90.0
        elif emenda.percentual_executado >= 50:
            return 70.0
        elif emenda.percentual_executado >= 20:
            return 50.0
        else:
            return 30.0
    
    def _calculate_timing_score(self, emenda: EmendaPix) -> float:
        """Calcula score de tempo (0-100)"""
        if not emenda.esta_atrasada():
            return 100.0
        
        # Se está atrasada, penalizar
        if emenda.percentual_executado < 50:
            return 30.0  # Muito atrasada
        elif emenda.percentual_executado < 80:
            return 60.0  # Moderadamente atrasada
        else:
            return 80.0  # Pouco atrasada
    
    def _calculate_documentation_score(self, emenda: EmendaPix) -> float:
        """Calcula score de documentação (0-100)"""
        if not emenda.documentos_comprobatórios:
            return 0.0
        
        doc_count = len(emenda.documentos_comprobatórios)
        
        if doc_count >= 5:
            return 100.0
        elif doc_count >= 3:
            return 80.0
        elif doc_count >= 2:
            return 60.0
        elif doc_count >= 1:
            return 40.0
        else:
            return 20.0
    
    def _calculate_risk_score(self, emenda: EmendaPix) -> float:
        """Calcula score de risco (0-100) - inverso do risco"""
        if emenda.risco_desvio is None:
            return 80.0  # Sem análise ainda
        
        # Converter risco (0-1) para score (0-100)
        # Risco alto = score baixo
        risk_score = (1 - emenda.risco_desvio) * 100
        
        return max(0.0, min(100.0, risk_score))
    
    def _calculate_history_score(self, emenda: EmendaPix) -> float:
        """Calcula score de histórico (0-100)"""
        # Por enquanto, baseado em status
        # Em produção, analisar histórico de mudanças
        
        status_scores = {
            "concluida": 100.0,
            "em_execucao": 80.0,
            "pendente": 60.0,
            "atrasada": 40.0,
            "cancelada": 0.0
        }
        
        return status_scores.get(emenda.status_execucao, 50.0)
    
    def _get_execution_details(self, emenda: EmendaPix) -> str:
        """Detalhes do fator execução"""
        return f"Percentual executado: {emenda.percentual_executado:.1f}%"
    
    def _get_timing_details(self, emenda: EmendaPix) -> str:
        """Detalhes do fator tempo"""
        if emenda.esta_atrasada():
            return "Emenda está atrasada"
        return "Emenda dentro do prazo"
    
    def _get_documentation_details(self, emenda: EmendaPix) -> str:
        """Detalhes do fator documentação"""
        doc_count = len(emenda.documentos_comprobatórios) if emenda.documentos_comprobatórios else 0
        return f"{doc_count} documento(s) comprobatório(s)"
    
    def _get_risk_details(self, emenda: EmendaPix) -> str:
        """Detalhes do fator risco"""
        if emenda.risco_desvio is None:
            return "Análise de risco não disponível"
        
        risk_pct = emenda.risco_desvio * 100
        if risk_pct >= 70:
            return f"Risco alto de desvio: {risk_pct:.0f}%"
        elif risk_pct >= 40:
            return f"Risco moderado de desvio: {risk_pct:.0f}%"
        else:
            return f"Risco baixo de desvio: {risk_pct:.0f}%"
    
    def _get_history_details(self, emenda: EmendaPix) -> str:
        """Detalhes do fator histórico"""
        return f"Status atual: {emenda.status_execucao}"
    
    def _get_score_level(self, score: float) -> str:
        """Determina nível do score"""
        if score >= 80:
            return "excelente"
        elif score >= 60:
            return "bom"
        elif score >= 40:
            return "regular"
        elif score >= 20:
            return "ruim"
        else:
            return "crítico"
    
    def _get_recommendations(self, score: float, factors: Dict) -> List[str]:
        """Gera recomendações baseadas no score"""
        recommendations = []
        
        if score < 50:
            recommendations.append("⚠️ Trust Score crítico - requer atenção imediata")
        
        if factors["execucao"]["score"] < 50:
            recommendations.append("📊 Melhorar execução - percentual muito baixo")
        
        if factors["tempo"]["score"] < 50:
            recommendations.append("⏰ Emenda atrasada - verificar prazos")
        
        if factors["documentacao"]["score"] < 50:
            recommendations.append("📄 Adicionar mais documentos comprobatórios")
        
        if factors["risco"]["score"] < 50:
            recommendations.append("🚨 Risco alto detectado - investigar possíveis desvios")
        
        if not recommendations:
            recommendations.append("✅ Emenda com boa integridade")
        
        return recommendations


# Import necessário
from typing import List

