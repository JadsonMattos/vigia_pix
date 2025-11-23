#!/usr/bin/env python3
"""
Script para popular banco de dados com dados de demonstração
Uso: python scripts/seed_demo_data.py
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.persistence.postgres.database import get_db_session
from src.infrastructure.persistence.postgres.models.legislation import Legislation
from sqlalchemy import select


async def seed_demo_data():
    """Popula banco com dados de demonstração"""
    print("🌱 Iniciando seed de dados de demonstração...")
    
    async for session in get_db_session():
        try:
            # Verificar se já existem dados
            result = await session.execute(select(Legislation).limit(1))
            existing = result.scalar_one_or_none()
            
            if existing:
                print("⚠️  Já existem dados no banco. Use --force para sobrescrever.")
                return
            
            # Dados de demonstração
            demo_legislations = [
                {
                    "external_id": "PL-1234-2024",
                    "title": "PL 1234/2024 - Direitos das Trabalhadoras Domésticas",
                    "content": """Art. 1º Esta Lei institui normas gerais sobre a prestação de serviços de trabalho doméstico, visando à proteção dos direitos fundamentais das trabalhadoras e trabalhadores domésticos, garantindo condições dignas de trabalho, remuneração justa, jornada de trabalho adequada, descanso semanal remunerado, férias anuais remuneradas, décimo terceiro salário, adicional de férias, salário-família, seguro-desemprego, aposentadoria, assistência à saúde, proteção à maternidade, proteção à infância, seguro contra acidentes de trabalho, e demais direitos previstos na legislação trabalhista e previdenciária.""",
                    "simplified_content": None,
                    "status": "TRAMITACAO",
                    "type": "PROJETO_LEI",
                    "url": "https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=1234",
                    "ementa": "Institui normas gerais sobre trabalho doméstico",
                    "authors": "Deputada Federal Maria Silva",
                    "processing_status": "EM_ANALISE",
                    "created_at": datetime.now() - timedelta(days=30),
                    "updated_at": datetime.now() - timedelta(days=1),
                },
                {
                    "external_id": "PL-5678-2024",
                    "title": "PL 5678/2024 - Melhoria do Transporte Público",
                    "content": """Art. 1º Esta Lei estabelece diretrizes para a melhoria da qualidade e da eficiência dos serviços de transporte público coletivo urbano, visando à universalização do acesso, à redução dos custos de deslocamento, ao aumento da frequência e da pontualidade dos serviços, à modernização da frota, à acessibilidade universal, à integração modal, à sustentabilidade ambiental, e ao fortalecimento da participação social no planejamento e na gestão do transporte público.""",
                    "simplified_content": None,
                    "status": "TRAMITACAO",
                    "type": "PROJETO_LEI",
                    "url": "https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=5678",
                    "ementa": "Estabelece diretrizes para melhoria do transporte público",
                    "authors": "Deputado Federal João Santos",
                    "processing_status": "EM_ANALISE",
                    "created_at": datetime.now() - timedelta(days=20),
                    "updated_at": datetime.now() - timedelta(days=2),
                },
                {
                    "external_id": "PL-9012-2024",
                    "title": "PL 9012/2024 - Proteção de Dados Pessoais",
                    "content": """Art. 1º Esta Lei estabelece normas gerais sobre a proteção de dados pessoais, visando à garantia do direito à privacidade, à autodeterminação informativa, à transparência no tratamento de dados, ao controle dos titulares sobre seus dados pessoais, à segurança da informação, à prevenção de danos, à responsabilização dos agentes de tratamento, e à conformidade com a legislação aplicável, especialmente a Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709, de 14 de agosto de 2018).""",
                    "simplified_content": None,
                    "status": "TRAMITACAO",
                    "type": "PROJETO_LEI",
                    "url": "https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=9012",
                    "ementa": "Estabelece normas sobre proteção de dados pessoais",
                    "authors": "Deputado Federal Carlos Oliveira",
                    "processing_status": "EM_ANALISE",
                    "created_at": datetime.now() - timedelta(days=15),
                    "updated_at": datetime.now() - timedelta(days=3),
                },
                {
                    "external_id": "PL-3456-2024",
                    "title": "PL 3456/2024 - Educação Básica de Qualidade",
                    "content": """Art. 1º Esta Lei institui o Programa Nacional de Melhoria da Qualidade da Educação Básica, com a finalidade de promover a universalização do acesso à educação, a melhoria da qualidade do ensino, a valorização dos profissionais da educação, a gestão democrática, o financiamento adequado, a avaliação sistemática, a formação continuada, a infraestrutura adequada, a tecnologia educacional, e a participação da comunidade escolar.""",
                    "simplified_content": None,
                    "status": "APROVADO",
                    "type": "PROJETO_LEI",
                    "url": "https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=3456",
                    "ementa": "Institui programa de melhoria da educação básica",
                    "authors": "Deputada Federal Ana Costa",
                    "processing_status": "APROVADO",
                    "created_at": datetime.now() - timedelta(days=60),
                    "updated_at": datetime.now() - timedelta(days=10),
                },
                {
                    "external_id": "PL-7890-2024",
                    "title": "PL 7890/2024 - Saúde Mental",
                    "content": """Art. 1º Esta Lei estabelece diretrizes para a política nacional de saúde mental, visando à promoção da saúde mental, à prevenção de transtornos mentais, ao tratamento adequado, à reabilitação psicossocial, à atenção integral, à desinstitucionalização, à redução do estigma, à participação social, à intersetorialidade, e ao fortalecimento da rede de atenção psicossocial.""",
                    "simplified_content": None,
                    "status": "TRAMITACAO",
                    "type": "PROJETO_LEI",
                    "url": "https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=7890",
                    "ementa": "Estabelece diretrizes para política de saúde mental",
                    "authors": "Deputado Federal Pedro Alves",
                    "processing_status": "EM_ANALISE",
                    "created_at": datetime.now() - timedelta(days=10),
                    "updated_at": datetime.now() - timedelta(days=1),
                },
            ]
            
            # Criar legislações
            for leg_data in demo_legislations:
                legislation = Legislation(**leg_data)
                session.add(legislation)
            
            await session.commit()
            print(f"✅ {len(demo_legislations)} legislações de demonstração criadas!")
            print("\n📋 Legislações criadas:")
            for leg in demo_legislations:
                print(f"  - {leg['title']}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Erro ao criar dados de demonstração: {e}")
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed dados de demonstração")
    parser.add_argument("--force", action="store_true", help="Forçar criação mesmo se já existirem dados")
    args = parser.parse_args()
    
    if args.force:
        print("⚠️  Modo --force ativado. Dados existentes serão mantidos.")
    
    asyncio.run(seed_demo_data())



