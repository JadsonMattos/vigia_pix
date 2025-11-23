#!/usr/bin/env python3
"""
Script para popular banco de dados com dados de Emenda Pix de demonstração
Uso: python scripts/seed_emenda_pix_data.py
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import uuid

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.persistence.postgres.database import AsyncSessionLocal
from src.domain.entities.emenda_pix import EmendaPix
from src.infrastructure.persistence.postgres.emenda_pix_repository_impl import PostgresEmendaPixRepository


async def seed_emenda_pix_data():
    """Popula banco com dados de Emenda Pix de demonstração"""
    print("🌱 Iniciando seed de dados de Emenda Pix...")
    
    async with AsyncSessionLocal() as session:
        try:
            repository = PostgresEmendaPixRepository(session)
            
            # Verificar se já existem dados
            existing = await repository.find_all(limit=1)
            if existing:
                print("⚠️  Já existem emendas no banco. Use --force para sobrescrever ou limpe a tabela primeiro.")
                print(f"   Encontradas {len(await repository.find_all(limit=1000))} emendas existentes.")
                return
            
            # Dados de demonstração baseados em casos reais
            demo_emendas = [
                {
                    "numero_emenda": "EP-001-2025",
                    "ano": 2025,
                    "tipo": "individual",
                    "autor_nome": "Abílio Bruno",
                    "autor_partido": "PL",
                    "autor_uf": "MT",
                    "destinatario_tipo": "municipio",
                    "destinatario_nome": "Cuiabá",
                    "destinatario_uf": "MT",
                    "destinatario_cnpj": "17.222.333/0001-44",
                    "valor_aprovado": 13000000.0,  # 13 milhões
                    "valor_empenhado": 13000000.0,
                    "valor_liquidado": 10000000.0,
                    "valor_pago": 8000000.0,
                    "objetivo": "Assistência hospitalar e ambulatorial",
                    "area": "saude",
                    "descricao_detalhada": "Aquisição de equipamentos médicos e materiais hospitalares para unidades de saúde do município",
                    "status_execucao": "em_execucao",
                    "data_inicio": datetime(2025, 1, 15),
                    "data_prevista_conclusao": datetime(2025, 6, 30),
                    "plano_trabalho": [
                        {"meta": 1, "descricao": "Aquisição de equipamentos", "valor": 5000000, "prazo": "2025-03-31", "status": "concluida"},
                        {"meta": 2, "descricao": "Aquisição de materiais", "valor": 5000000, "prazo": "2025-04-30", "status": "em_execucao"},
                        {"meta": 3, "descricao": "Distribuição e instalação", "valor": 3000000, "prazo": "2025-06-30", "status": "pendente"}
                    ],
                    "numero_metas": 3,
                    "metas_concluidas": 1,
                    "tem_noticias": True,
                    "noticias_relacionadas": [
                        {"titulo": "Deputado destina 13 milhões para saúde de Cuiabá", "fonte": "G1 MT", "data": "2025-01-20"},
                        {"titulo": "Equipamentos médicos chegam a Cuiabá", "fonte": "Diário de Cuiabá", "data": "2025-03-15"}
                    ],
                    "processo_sei": "CEIS-1234567",
                    "link_portal_transparencia": "https://portaldatransparencia.gov.br/emendas/123456"
                },
                {
                    "numero_emenda": "EP-002-2025",
                    "ano": 2025,
                    "tipo": "bancada",
                    "autor_nome": "Bancada da Segurança",
                    "autor_partido": "PL",
                    "autor_uf": "SP",
                    "destinatario_tipo": "estado",
                    "destinatario_nome": "São Paulo",
                    "destinatario_uf": "SP",
                    "valor_aprovado": 50000000.0,  # 50 milhões
                    "valor_empenhado": 50000000.0,
                    "valor_liquidado": 20000000.0,
                    "valor_pago": 10000000.0,  # Apenas 20% pago
                    "objetivo": "Segurança pública e combate à violência",
                    "area": "seguranca",
                    "descricao_detalhada": "Recursos para aquisição de viaturas, equipamentos e capacitação de policiais",
                    "status_execucao": "atrasada",
                    "data_inicio": datetime(2025, 2, 1),
                    "data_prevista_conclusao": datetime(2025, 5, 31),  # Já passou
                    "plano_trabalho": [
                        {"meta": 1, "descricao": "Aquisição de viaturas", "valor": 20000000, "prazo": "2025-03-31", "status": "concluida"},
                        {"meta": 2, "descricao": "Equipamentos policiais", "valor": 20000000, "prazo": "2025-04-30", "status": "atrasada"},
                        {"meta": 3, "descricao": "Capacitação", "valor": 10000000, "prazo": "2025-05-31", "status": "atrasada"}
                    ],
                    "numero_metas": 3,
                    "metas_concluidas": 1,
                    "tem_noticias": False,
                    "risco_desvio": 0.75,
                    "processo_sei": "CEIS-2345678"
                },
                {
                    "numero_emenda": "EP-003-2025",
                    "ano": 2025,
                    "tipo": "individual",
                    "autor_nome": "Dep. João Silva",
                    "autor_partido": "PT",
                    "autor_uf": "CE",
                    "destinatario_tipo": "municipio",
                    "destinatario_nome": "Fortaleza",
                    "destinatario_uf": "CE",
                    "valor_aprovado": 8000000.0,  # 8 milhões
                    "valor_empenhado": 8000000.0,
                    "valor_liquidado": 0.0,
                    "valor_pago": 0.0,  # Nada foi pago ainda
                    "objetivo": "Educação básica",
                    "area": "educacao",
                    "descricao_detalhada": "Construção de escolas e aquisição de material didático",
                    "status_execucao": "pendente",
                    "data_inicio": datetime(2025, 1, 10),
                    "data_prevista_conclusao": datetime(2025, 12, 31),
                    "plano_trabalho": [
                        {"meta": 1, "descricao": "Projeto arquitetônico", "valor": 500000, "prazo": "2025-02-28", "status": "concluida"},
                        {"meta": 2, "descricao": "Construção", "valor": 6000000, "prazo": "2025-08-31", "status": "pendente"},
                        {"meta": 3, "descricao": "Material didático", "valor": 1500000, "prazo": "2025-10-31", "status": "pendente"}
                    ],
                    "numero_metas": 3,
                    "metas_concluidas": 1,
                    "tem_noticias": True,
                    "noticias_relacionadas": [
                        {"titulo": "Deputado anuncia emenda para educação em Fortaleza", "fonte": "O Povo", "data": "2025-01-15"}
                    ],
                    "processo_sei": "CEIS-3456789"
                },
                {
                    "numero_emenda": "EP-004-2025",
                    "ano": 2025,
                    "tipo": "individual",
                    "autor_nome": "Dep. Maria Santos",
                    "autor_partido": "PSDB",
                    "autor_uf": "RJ",
                    "destinatario_tipo": "municipio",
                    "destinatario_nome": "Rio de Janeiro",
                    "destinatario_uf": "RJ",
                    "valor_aprovado": 25000000.0,  # 25 milhões
                    "valor_empenhado": 25000000.0,
                    "valor_liquidado": 25000000.0,
                    "valor_pago": 25000000.0,  # 100% pago
                    "objetivo": "Infraestrutura urbana",
                    "area": "infraestrutura",
                    "descricao_detalhada": "Pavimentação de ruas e construção de calçadas",
                    "status_execucao": "concluida",
                    "data_inicio": datetime(2024, 11, 1),
                    "data_prevista_conclusao": datetime(2025, 3, 31),
                    "data_real_conclusao": datetime(2025, 3, 15),
                    "plano_trabalho": [
                        {"meta": 1, "descricao": "Pavimentação", "valor": 15000000, "prazo": "2025-02-28", "status": "concluida"},
                        {"meta": 2, "descricao": "Calçadas", "valor": 10000000, "prazo": "2025-03-31", "status": "concluida"}
                    ],
                    "numero_metas": 2,
                    "metas_concluidas": 2,
                    "tem_noticias": True,
                    "noticias_relacionadas": [
                        {"titulo": "Obras de pavimentação concluídas no Rio", "fonte": "O Globo", "data": "2025-03-20"},
                        {"titulo": "Deputada entrega obras de infraestrutura", "fonte": "Extra", "data": "2025-03-25"}
                    ],
                    "documentos_comprobatórios": [
                        {"tipo": "foto", "descricao": "Ruas pavimentadas", "url": "https://exemplo.com/foto1.jpg"},
                        {"tipo": "nota_fiscal", "descricao": "Nota fiscal de materiais", "url": "https://exemplo.com/nf.pdf"}
                    ],
                    "processo_sei": "CEIS-4567890"
                },
                {
                    "numero_emenda": "EP-005-2025",
                    "ano": 2025,
                    "tipo": "individual",
                    "autor_nome": "Dep. Carlos Oliveira",
                    "autor_partido": "MDB",
                    "autor_uf": "BA",
                    "destinatario_tipo": "municipio",
                    "destinatario_nome": "Salvador",
                    "destinatario_uf": "BA",
                    "valor_aprovado": 15000000.0,  # 15 milhões
                    "valor_empenhado": 15000000.0,
                    "valor_liquidado": 5000000.0,
                    "valor_pago": 2000000.0,  # Apenas 13% pago
                    "objetivo": "Saneamento básico",
                    "area": "saneamento",
                    "descricao_detalhada": "Ampliação da rede de esgoto e tratamento de água",
                    "status_execucao": "atrasada",
                    "data_inicio": datetime(2024, 12, 1),
                    "data_prevista_conclusao": datetime(2025, 4, 30),  # Já passou
                    "plano_trabalho": [
                        {"meta": 1, "descricao": "Projeto técnico", "valor": 2000000, "prazo": "2025-01-31", "status": "concluida"},
                        {"meta": 2, "descricao": "Obras de rede", "valor": 10000000, "prazo": "2025-03-31", "status": "atrasada"},
                        {"meta": 3, "descricao": "Estação de tratamento", "valor": 3000000, "prazo": "2025-04-30", "status": "atrasada"}
                    ],
                    "numero_metas": 3,
                    "metas_concluidas": 1,
                    "tem_noticias": False,
                    "risco_desvio": 0.65,
                    "processo_sei": "CEIS-5678901"
                }
            ]
            
            print(f"📝 Criando {len(demo_emendas)} emendas de demonstração...")
            
            for emenda_data in demo_emendas:
                emenda = EmendaPix(
                    id=str(uuid.uuid4()),
                    **emenda_data,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    last_sync=datetime.now()
                )
                
                # Calcular percentual executado
                emenda.percentual_executado = emenda.calcular_percentual_executado()
                
                await repository.save(emenda)
                print(f"  ✅ Criada emenda {emenda.numero_emenda} - {emenda.autor_nome} → {emenda.destinatario_nome} (R$ {emenda.valor_aprovado:,.2f})")
            
            print(f"\n✨ Seed concluído! {len(demo_emendas)} emendas criadas.")
            
        except Exception as e:
            print(f"❌ Erro ao fazer seed: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(seed_emenda_pix_data())

