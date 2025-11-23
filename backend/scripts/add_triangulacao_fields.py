"""
Script para adicionar campos de Triangulação de Dados ao banco
Executa ALTER TABLE para adicionar fotos_georreferenciadas e validacao_geofencing
"""
import asyncio
import sys
from sqlalchemy import text

sys.path.insert(0, '.')

from src.infrastructure.persistence.postgres.database import AsyncSessionLocal


async def add_triangulacao_fields():
    """Adiciona campos de Triangulação de Dados"""
    async with AsyncSessionLocal() as session:
        try:
            # Verificar se colunas já existem
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'emenda_pix' 
                AND column_name IN ('fotos_georreferenciadas', 'validacao_geofencing')
            """)
            result = await session.execute(check_query)
            existing_columns = [row[0] for row in result.fetchall()]
            
            # Adicionar fotos_georreferenciadas se não existir
            if 'fotos_georreferenciadas' not in existing_columns:
                print("Adicionando coluna fotos_georreferenciadas...")
                await session.execute(text("""
                    ALTER TABLE emenda_pix 
                    ADD COLUMN fotos_georreferenciadas JSON
                """))
                print("✅ Coluna fotos_georreferenciadas adicionada")
            else:
                print("⚠️  Coluna fotos_georreferenciadas já existe")
            
            # Adicionar validacao_geofencing se não existir
            if 'validacao_geofencing' not in existing_columns:
                print("Adicionando coluna validacao_geofencing...")
                await session.execute(text("""
                    ALTER TABLE emenda_pix 
                    ADD COLUMN validacao_geofencing BOOLEAN
                """))
                print("✅ Coluna validacao_geofencing adicionada")
            else:
                print("⚠️  Coluna validacao_geofencing já existe")
            
            await session.commit()
            print("\n✅ Migração concluída com sucesso!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Erro na migração: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(add_triangulacao_fields())

