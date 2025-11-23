#!/usr/bin/env python3
"""
Script para sincronização periódica de dados do CEIS

Este script pode ser executado via cron job para manter os dados atualizados.

Exemplo de crontab (executar diariamente às 3h da manhã):
0 3 * * * /usr/bin/python3 /path/to/backend/scripts/sync_ceis_periodic.py
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
from src.application.use_cases.emenda_pix.sync_ceis_data import SyncCEISDataUseCase
import structlog

logger = structlog.get_logger()


async def sync_ceis():
    """Sincroniza dados do CEIS para todas as emendas"""
    session: AsyncSession = None
    try:
        # Inicializar banco de dados
        await init_db()
        
        # Criar sessão
        async with AsyncSessionLocal() as session:
            repository = PostgresEmendaPixRepository(session)
            use_case = SyncCEISDataUseCase(repository)
            
            logger.info("sync_ceis_periodic_started")
            
            # Sincronizar todas as emendas com processo SEI
            result = await use_case.sync_all_emendas_with_ceis()
            
            if result["success"]:
                logger.info(
                    "sync_ceis_periodic_completed",
                    total=result["total"],
                    synced=result["synced"],
                    updated=result["updated"],
                    errors=result["errors"]
                )
                print(f"✅ Sincronização CEIS concluída:")
                print(f"   - Total processadas: {result['total']}")
                print(f"   - Sincronizadas: {result['synced']}")
                print(f"   - Atualizadas: {result['updated']}")
                print(f"   - Erros: {result['errors']}")
                return 0
            else:
                logger.error("sync_ceis_periodic_failed", message=result["message"])
                print(f"❌ Erro na sincronização: {result['message']}")
                return 1
                
    except Exception as e:
        logger.error("sync_ceis_periodic_error", error=str(e))
        print(f"❌ Erro fatal: {str(e)}")
        return 1
    finally:
        if session:
            await session.close()
        await close_db()


if __name__ == "__main__":
    exit_code = asyncio.run(sync_ceis())
    sys.exit(exit_code)

