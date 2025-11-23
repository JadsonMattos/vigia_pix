#!/usr/bin/env python3
"""Script para testar a API de Emenda Pix"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.persistence.postgres.database import AsyncSessionLocal
from src.infrastructure.persistence.postgres.emenda_pix_repository_impl import PostgresEmendaPixRepository


async def test_emenda_pix():
    """Testa se há emendas no banco"""
    print("🔍 Verificando emendas no banco...")
    
    async with AsyncSessionLocal() as session:
        try:
            repository = PostgresEmendaPixRepository(session)
            emendas = await repository.find_all(limit=10)
            
            print(f"✅ Encontradas {len(emendas)} emendas no banco")
            
            if len(emendas) > 0:
                print("\n📋 Primeiras emendas:")
                for i, emenda in enumerate(emendas[:3], 1):
                    print(f"\n{i}. {emenda.numero_emenda}")
                    print(f"   Autor: {emenda.autor_nome}")
                    print(f"   Destinatário: {emenda.destinatario_nome}")
                    print(f"   Valor: R$ {emenda.valor_aprovado:,.2f}")
                    print(f"   Status: {emenda.status_execucao}")
                    print(f"   Executado: {emenda.percentual_executado:.1f}%")
            else:
                print("\n⚠️  Nenhuma emenda encontrada. Execute o seed:")
                print("   python scripts/seed_emenda_pix_data.py")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(test_emenda_pix())

