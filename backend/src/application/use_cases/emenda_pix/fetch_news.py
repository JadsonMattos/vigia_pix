"""
Use case para buscar e analisar notícias relacionadas a emendas
"""
from typing import Optional
import structlog
from datetime import datetime

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository
from src.infrastructure.external.news_scraper.client import NewsScraperClient
from src.infrastructure.ai.sentiment_analyzer import SentimentAnalyzer

logger = structlog.get_logger()


class FetchEmendaNewsUseCase:
    """Busca e analisa notícias relacionadas a uma emenda"""
    
    def __init__(
        self,
        repository: EmendaPixRepository,
        news_client: Optional[NewsScraperClient] = None,
        sentiment_analyzer: Optional[SentimentAnalyzer] = None
    ):
        self.repository = repository
        self.news_client = news_client or NewsScraperClient()
        self.sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()
    
    async def execute(
        self,
        emenda_id: str,
        limit: int = 10,
        analyze_sentiment: bool = True
    ) -> dict:
        """
        Busca notícias relacionadas a uma emenda
        
        Args:
            emenda_id: ID da emenda
            limit: Limite de notícias a buscar
            analyze_sentiment: Se deve analisar sentimento das notícias
        
        Returns:
            dict com notícias encontradas e análise
        """
        try:
            # Buscar emenda
            emenda = await self.repository.find_by_id(emenda_id)
            if not emenda:
                return {
                    "success": False,
                    "message": "Emenda não encontrada",
                    "news": []
                }
            
            logger.info(
                "fetch_news_started",
                emenda_id=emenda_id,
                numero_emenda=emenda.numero_emenda
            )
            
            # Buscar notícias
            news = await self.news_client.search_emenda_news(
                numero_emenda=emenda.numero_emenda,
                autor_nome=emenda.autor_nome,
                destinatario_nome=emenda.destinatario_nome,
                limit=limit
            )
            
            if not news:
                logger.info("no_news_found", emenda_id=emenda_id)
                return {
                    "success": True,
                    "message": "Nenhuma notícia encontrada",
                    "news": [],
                    "overall_sentiment": None
                }
            
            # Analisar sentimentos se solicitado
            if analyze_sentiment:
                news = await self.sentiment_analyzer.analyze_news_sentiment(news)
                overall_sentiment = self.sentiment_analyzer.calculate_overall_sentiment(news)
            else:
                overall_sentiment = None
            
            # Atualizar emenda com notícias
            emenda.noticias_relacionadas = news
            emenda.tem_noticias = len(news) > 0
            
            # Adicionar sentimento geral à análise IA se existir
            if overall_sentiment and emenda.analise_ia:
                if "sentimento_noticias" not in emenda.analise_ia:
                    emenda.analise_ia["sentimento_noticias"] = {}
                emenda.analise_ia["sentimento_noticias"] = overall_sentiment
            
            await self.repository.save(emenda)
            
            logger.info(
                "fetch_news_completed",
                emenda_id=emenda_id,
                news_count=len(news),
                overall_sentiment=overall_sentiment.get("sentimento") if overall_sentiment else None
            )
            
            return {
                "success": True,
                "message": f"{len(news)} notícia(s) encontrada(s)",
                "news": news,
                "overall_sentiment": overall_sentiment
            }
            
        except Exception as e:
            logger.error(
                "fetch_news_error",
                emenda_id=emenda_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "success": False,
                "message": f"Erro ao buscar notícias: {str(e)}",
                "news": [],
                "overall_sentiment": None
            }
        finally:
            await self.news_client.close()
    
    async def fetch_all_emendas_news(
        self,
        limit_per_emenda: int = 5
    ) -> dict:
        """
        Busca notícias para todas as emendas
        
        Args:
            limit_per_emenda: Limite de notícias por emenda
        
        Returns:
            dict com estatísticas
        """
        try:
            # Buscar todas as emendas
            all_emendas = await self.repository.find_all(limit=1000)
            
            logger.info(
                "fetch_all_news_started",
                total_emendas=len(all_emendas)
            )
            
            stats = {
                "total_emendas": len(all_emendas),
                "processed": 0,
                "news_found": 0,
                "errors": 0
            }
            
            for emenda in all_emendas:
                try:
                    result = await self.execute(
                        emenda.id,
                        limit=limit_per_emenda,
                        analyze_sentiment=True
                    )
                    
                    if result["success"]:
                        stats["processed"] += 1
                        if result["news"]:
                            stats["news_found"] += len(result["news"])
                    else:
                        stats["errors"] += 1
                        
                except Exception as e:
                    logger.error(
                        "fetch_news_error",
                        emenda_id=emenda.id,
                        error=str(e)
                    )
                    stats["errors"] += 1
            
            logger.info("fetch_all_news_completed", **stats)
            
            return {
                "success": True,
                "message": f"Processadas {stats['processed']} emendas, {stats['news_found']} notícias encontradas",
                **stats
            }
            
        except Exception as e:
            logger.error("fetch_all_news_error", error=str(e))
            return {
                "success": False,
                "message": f"Erro ao buscar notícias: {str(e)}",
                "total_emendas": 0,
                "processed": 0,
                "news_found": 0,
                "errors": 1
            }

