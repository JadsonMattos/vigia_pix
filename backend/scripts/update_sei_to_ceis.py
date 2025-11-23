#!/usr/bin/env python3
"""
Script para atualizar referências de SEI para CEIS nos dados existentes
Uso: python scripts/update_sei_to_ceis.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.persistence.postgres.database import AsyncSessionLocal
from src.infrastructure.persistence.postgres.emenda_pix_repository_impl import PostgresEmendaPixRepository
from sqlalchemy import text


async def update_sei_to_ceis():
    """Atualiza referências de SEI para CEIS"""
    print("🔄 Atualizando referências de SEI para CEIS...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Atualizar processo_sei que começa com "SEI-"
            result = await session.execute(
                text("""
                    UPDATE emenda_pix 
                    SET processo_sei = REPLACE(processo_sei, 'SEI-', 'CEIS-')
                    WHERE processo_sei LIKE 'SEI-%'
                """)
            )
            
            await session.commit()
            
            rows_updated = result.rowcount
            print(f"✅ {rows_updated} emenda(s) atualizada(s)")
            
            if rows_updated > 0:
                # Verificar resultado
                repository = PostgresEmendaPixRepository(session)
                emendas = await repository.find_all(limit=1000)
                
                ceis_count = sum(1 for e in emendas if e.processo_sei and e.processo_sei.startswith('CEIS-'))
                sei_count = sum(1 for e in emendas if e.processo_sei and e.processo_sei.startswith('SEI-'))
                
                print(f"\n📊 Status após atualização:")
                print(f"   - Processos CEIS: {ceis_count}")
                print(f"   - Processos SEI (restantes): {sei_count}")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(update_sei_to_ceis())

