#!/usr/bin/env python3
"""
Script para sincronização periódica de emendas do Portal da Transparência

Este script pode ser executado via cron job para manter os dados atualizados.

Exemplo de crontab (executar diariamente às 2h da manhã):
0 2 * * * /usr/bin/python3 /path/to/backend/scripts/sync_emendas_periodic.py
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
from src.application.use_cases.emenda_pix.sync_emendas_portal import SyncEmendasPortalUseCase
import structlog

logger = structlog.get_logger()


async def sync_emendas():
    """Sincroniza emendas do Portal da Transparência"""
    session: AsyncSession = None
    try:
        # Inicializar banco de dados
        await init_db()
        
        # Criar sessão
        async with AsyncSessionLocal() as session:
            repository = PostgresEmendaPixRepository(session)
            use_case = SyncEmendasPortalUseCase(repository)
            
            # Sincronizar emendas do ano atual
            from datetime import datetime
            ano_atual = datetime.now().year
            
            logger.info("sync_periodic_started", ano=ano_atual)
            
            result = await use_case.execute(
                ano=ano_atual,
                limit=500  # Limite razoável para sincronização periódica
            )
            
            if result["success"]:
                logger.info(
                    "sync_periodic_completed",
                    total_fetched=result["total_fetched"],
                    total_saved=result["total_saved"],
                    total_updated=result["total_updated"],
                    total_errors=result["total_errors"]
                )
                print(f"✅ Sincronização concluída:")
                print(f"   - Buscadas: {result['total_fetched']}")
                print(f"   - Novas: {result['total_saved']}")
                print(f"   - Atualizadas: {result['total_updated']}")
                print(f"   - Erros: {result['total_errors']}")
                return 0
            else:
                logger.error("sync_periodic_failed", message=result["message"])
                print(f"❌ Erro na sincronização: {result['message']}")
                return 1
                
    except Exception as e:
        logger.error("sync_periodic_error", error=str(e))
        print(f"❌ Erro fatal: {str(e)}")
        return 1
    finally:
        if session:
            await session.close()
        await close_db()


if __name__ == "__main__":
    exit_code = asyncio.run(sync_emendas())
    sys.exit(exit_code)

