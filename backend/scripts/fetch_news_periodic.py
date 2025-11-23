#!/usr/bin/env python3
"""
Script para busca periódica de notícias relacionadas a emendas

Este script pode ser executado via cron job para manter as notícias atualizadas.

Exemplo de crontab (executar diariamente às 4h da manhã):
0 4 * * * /usr/bin/python3 /path/to/backend/scripts/fetch_news_periodic.py
"""
import asyncio
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.persistence.postgres.database import AsyncSessionLocal, init_db, close_db
from src.infrastructure.persistence.postgres.emenda_pix_repository_impl import PostgresEmendaPixRepository
from src.application.use_cases.emenda_pix.fetch_news import FetchEmendaNewsUseCase
import structlog

logger = structlog.get_logger()


async def fetch_news():
    """Busca notícias para todas as emendas"""
    session: AsyncSession = None
    try:
        # Inicializar banco de dados
        await init_db()
        
        # Criar sessão
        async with AsyncSessionLocal() as session:
            repository = PostgresEmendaPixRepository(session)
            use_case = FetchEmendaNewsUseCase(repository)
            
            logger.info("fetch_news_periodic_started")
            
            # Buscar notícias para todas as emendas
            result = await use_case.fetch_all_emendas_news(limit_per_emenda=5)
            
            if result["success"]:
                logger.info(
                    "fetch_news_periodic_completed",
                    total_emendas=result["total_emendas"],
                    processed=result["processed"],
                    news_found=result["news_found"],
                    errors=result["errors"]
                )
                print(f"✅ Busca de notícias concluída:")
                print(f"   - Total de emendas: {result['total_emendas']}")
                print(f"   - Processadas: {result['processed']}")
                print(f"   - Notícias encontradas: {result['news_found']}")
                print(f"   - Erros: {result['errors']}")
                return 0
            else:
                logger.error("fetch_news_periodic_failed", message=result["message"])
                print(f"❌ Erro na busca: {result['message']}")
                return 1
                
    except Exception as e:
        logger.error("fetch_news_periodic_error", error=str(e))
        print(f"❌ Erro fatal: {str(e)}")
        return 1
    finally:
        if session:
            await session.close()
        await close_db()


if __name__ == "__main__":
    exit_code = asyncio.run(fetch_news())
    sys.exit(exit_code)

