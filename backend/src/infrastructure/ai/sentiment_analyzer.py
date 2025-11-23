"""
Análise de Sentimentos para Notícias
Usa IA para analisar o sentimento de notícias relacionadas a emendas
"""
from typing import List, Dict, Optional
import structlog
import os

logger = structlog.get_logger()

# Tentar importar OpenAI, mas não falhar se não estiver disponível
try:
    from src.infrastructure.ai.openai_service import OpenAIService
    OPENAI_AVAILABLE = True
except (ImportError, ValueError):
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI não disponível. Usando análise simples baseada em palavras-chave.")


class SentimentAnalyzer:
    """Analisador de sentimentos para notícias"""
    
    def __init__(self, openai_service: Optional['OpenAIService'] = None):
        self.openai_service = None
        if OPENAI_AVAILABLE:
            try:
                self.openai_service = openai_service or OpenAIService()
            except (ImportError, ValueError):
                logger.warning("OpenAI não configurado. Usando análise simples.")
                self.openai_service = None
    
    async def analyze_news_sentiment(
        self,
        news: List[Dict]
    ) -> List[Dict]:
        """
        Analisa sentimento de uma lista de notícias
        
        Args:
            news: Lista de notícias
        
        Returns:
            Lista de notícias com análise de sentimento
        """
        analyzed_news = []
        
        for item in news:
            try:
                sentiment = await self._analyze_single_news(item)
                item["sentimento"] = sentiment["sentimento"]
                item["sentimento_score"] = sentiment["score"]
                item["sentimento_explicacao"] = sentiment.get("explicacao", "")
                analyzed_news.append(item)
            except Exception as e:
                logger.error(
                    "sentiment_analysis_error",
                    news_title=item.get("titulo", "unknown"),
                    error=str(e)
                )
                # Manter notícia com sentimento neutro em caso de erro
                item["sentimento"] = "neutro"
                item["sentimento_score"] = 0.0
                analyzed_news.append(item)
        
        return analyzed_news
    
    async def _analyze_single_news(self, news_item: Dict) -> Dict:
        """
        Analisa sentimento de uma notícia individual
        
        Args:
            news_item: Dicionário com dados da notícia
        
        Returns:
            Dicionário com análise de sentimento
        """
        titulo = news_item.get("titulo", "")
        resumo = news_item.get("resumo", "")
        conteudo = news_item.get("conteudo", "")
        
        # Combinar texto para análise
        text = f"{titulo}. {resumo}. {conteudo[:500]}"
        
        # Prompt para análise de sentimento
        prompt = f"""Analise o sentimento da seguinte notícia sobre emenda parlamentar e retorne APENAS um JSON com:
- "sentimento": "positivo", "negativo" ou "neutro"
- "score": número de 0.0 a 1.0 (0.0 = muito negativo, 0.5 = neutro, 1.0 = muito positivo)
- "explicacao": breve explicação do sentimento

Notícia:
{text}

Retorne APENAS o JSON, sem markdown, sem explicações adicionais."""

        # Se OpenAI não estiver disponível, usar análise simples
        if not self.openai_service:
            return self._simple_sentiment_analysis(text)
        
        try:
            response = await self.openai_service.generate_text(
                prompt=prompt,
                max_tokens=150,
                temperature=0.3
            )
            
            # Parsear resposta JSON
            import json
            # Remover markdown se houver
            response_clean = response.strip()
            if response_clean.startswith("```"):
                response_clean = response_clean.split("```")[1]
                if response_clean.startswith("json"):
                    response_clean = response_clean[4:]
            response_clean = response_clean.strip()
            
            sentiment_data = json.loads(response_clean)
            
            return {
                "sentimento": sentiment_data.get("sentimento", "neutro"),
                "score": float(sentiment_data.get("score", 0.5)),
                "explicacao": sentiment_data.get("explicacao", "")
            }
            
        except Exception as e:
            logger.error("sentiment_analysis_failed", error=str(e))
            # Fallback: análise simples baseada em palavras-chave
            return self._simple_sentiment_analysis(text)
    
    def _simple_sentiment_analysis(self, text: str) -> Dict:
        """
        Análise simples de sentimento baseada em palavras-chave
        (fallback quando IA não está disponível)
        """
        text_lower = text.lower()
        
        # Palavras positivas
        positive_words = [
            "aprovado", "concluído", "sucesso", "benefício", "melhoria",
            "investimento", "recursos", "executado", "entregue", "funcionando"
        ]
        
        # Palavras negativas
        negative_words = [
            "atraso", "problema", "irregularidade", "desvio", "corrupção",
            "investigação", "suspenso", "cancelado", "falha", "erro"
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentimento = "positivo"
            score = min(0.5 + (positive_count * 0.1), 1.0)
        elif negative_count > positive_count:
            sentimento = "negativo"
            score = max(0.5 - (negative_count * 0.1), 0.0)
        else:
            sentimento = "neutro"
            score = 0.5
        
        return {
            "sentimento": sentimento,
            "score": score,
            "explicacao": f"Análise baseada em palavras-chave: {positive_count} positivas, {negative_count} negativas"
        }
    
    def calculate_overall_sentiment(self, news: List[Dict]) -> Dict:
        """
        Calcula sentimento geral de uma lista de notícias
        
        Args:
            news: Lista de notícias com análise de sentimento
        
        Returns:
            Dicionário com sentimento geral
        """
        if not news:
            return {
                "sentimento": "neutro",
                "score": 0.5,
                "total_noticias": 0
            }
        
        scores = [n.get("sentimento_score", 0.5) for n in news]
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 0.6:
            sentimento = "positivo"
        elif avg_score < 0.4:
            sentimento = "negativo"
        else:
            sentimento = "neutro"
        
        return {
            "sentimento": sentimento,
            "score": avg_score,
            "total_noticias": len(news),
            "positivas": sum(1 for n in news if n.get("sentimento") == "positivo"),
            "negativas": sum(1 for n in news if n.get("sentimento") == "negativo"),
            "neutras": sum(1 for n in news if n.get("sentimento") == "neutro")
        }

