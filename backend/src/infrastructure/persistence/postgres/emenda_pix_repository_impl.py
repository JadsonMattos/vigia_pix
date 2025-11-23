"""PostgreSQL implementation of EmendaPixRepository"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository
from src.infrastructure.persistence.postgres.models.emenda_pix import EmendaPixModel


class PostgresEmendaPixRepository(EmendaPixRepository):
    """PostgreSQL implementation of EmendaPixRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, id: str) -> Optional[EmendaPix]:
        """Find emenda by ID"""
        result = await self.session.get(EmendaPixModel, id)
        return self._to_entity(result) if result else None
    
    async def find_by_numero(self, numero: str, ano: int) -> Optional[EmendaPix]:
        """Find emenda by number and year"""
        stmt = select(EmendaPixModel).where(
            and_(
                EmendaPixModel.numero_emenda == numero,
                EmendaPixModel.ano == ano
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def find_by_numero_emenda(self, numero_emenda: str) -> Optional[EmendaPix]:
        """Find emenda by number (most recent year)"""
        stmt = select(EmendaPixModel).where(
            EmendaPixModel.numero_emenda == numero_emenda
        ).order_by(EmendaPixModel.ano.desc()).limit(1)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def find_all(
        self, 
        limit: int = 100, 
        offset: int = 0,
        autor_nome: Optional[str] = None,
        destinatario_uf: Optional[str] = None,
        area: Optional[str] = None,
        status_execucao: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> List[EmendaPix]:
        """Find all emendas with optional filters"""
        stmt = select(EmendaPixModel)
        
        conditions = []
        if autor_nome:
            conditions.append(EmendaPixModel.autor_nome.ilike(f"%{autor_nome}%"))
        if destinatario_uf:
            conditions.append(EmendaPixModel.destinatario_uf == destinatario_uf)
        if area:
            conditions.append(EmendaPixModel.area == area)
        if status_execucao:
            conditions.append(EmendaPixModel.status_execucao == status_execucao)
        if tipo:
            conditions.append(EmendaPixModel.tipo == tipo)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.limit(limit).offset(offset).order_by(EmendaPixModel.created_at.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def find_by_autor(self, autor_nome: str) -> List[EmendaPix]:
        """Find emendas by author"""
        stmt = select(EmendaPixModel).where(
            EmendaPixModel.autor_nome.ilike(f"%{autor_nome}%")
        ).order_by(EmendaPixModel.ano.desc(), EmendaPixModel.valor_aprovado.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def find_by_destinatario(self, destinatario_nome: str) -> List[EmendaPix]:
        """Find emendas by recipient"""
        stmt = select(EmendaPixModel).where(
            EmendaPixModel.destinatario_nome.ilike(f"%{destinatario_nome}%")
        ).order_by(EmendaPixModel.ano.desc(), EmendaPixModel.valor_aprovado.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def save(self, emenda: EmendaPix) -> None:
        """Save or update emenda"""
        try:
            model = await self.session.get(EmendaPixModel, emenda.id)
            is_new = model is None
            
            if model:
                # Update
                self._update_model(model, emenda)
            else:
                # Create
                model = self._to_model(emenda)
                self.session.add(model)
            
            await self.session.commit()
            await self.session.refresh(model)
            
            # Registrar na blockchain (após commit bem-sucedido)
            try:
                from src.infrastructure.blockchain.tracker import get_blockchain_tracker
                blockchain = get_blockchain_tracker()
                
                if is_new:
                    # Registrar criação
                    blockchain.register_emenda_creation(
                        emenda_id=emenda.id,
                        emenda_data={
                            "numero_emenda": emenda.numero_emenda,
                            "ano": emenda.ano,
                            "autor_nome": emenda.autor_nome,
                            "destinatario_nome": emenda.destinatario_nome,
                            "valor_aprovado": emenda.valor_aprovado,
                            "plano_trabalho": emenda.plano_trabalho or []
                        }
                    )
                else:
                    # Registrar atualização de execução
                    blockchain.register_execution_update(
                        emenda_id=emenda.id,
                        execution_data={
                            "valor_pago": emenda.valor_pago,
                            "percentual_executado": emenda.percentual_executado,
                            "status_execucao": emenda.status_execucao,
                            "metas_concluidas": emenda.metas_concluidas
                        }
                    )
            except Exception as blockchain_error:
                # Não falhar se blockchain falhar (pode não estar configurado)
                import structlog
                logger = structlog.get_logger()
                logger.warning("blockchain_registration_failed", error=str(blockchain_error))
                
        except Exception as e:
            await self.session.rollback()
            raise
    
    async def delete(self, id: str) -> None:
        """Delete emenda"""
        model = await self.session.get(EmendaPixModel, id)
        if model:
            await self.session.delete(model)
            await self.session.commit()
    
    def _to_entity(self, model: EmendaPixModel) -> EmendaPix:
        """Convert model to entity"""
        from datetime import datetime
        return EmendaPix(
            id=str(model.id),
            numero_emenda=model.numero_emenda,
            ano=model.ano,
            tipo=model.tipo,
            autor_nome=model.autor_nome,
            autor_partido=model.autor_partido,
            autor_uf=model.autor_uf,
            destinatario_tipo=model.destinatario_tipo,
            destinatario_nome=model.destinatario_nome,
            destinatario_uf=model.destinatario_uf,
            destinatario_cnpj=model.destinatario_cnpj,
            valor_aprovado=model.valor_aprovado,
            valor_empenhado=model.valor_empenhado or 0.0,
            valor_liquidado=model.valor_liquidado or 0.0,
            valor_pago=model.valor_pago or 0.0,
            objetivo=model.objetivo,
            area=model.area,
            descricao_detalhada=model.descricao_detalhada,
            status_execucao=model.status_execucao,
            percentual_executado=model.percentual_executado or 0.0,
            data_inicio=model.data_inicio,
            data_prevista_conclusao=model.data_prevista_conclusao,
            data_real_conclusao=model.data_real_conclusao,
            plano_trabalho=model.plano_trabalho,
            numero_metas=model.numero_metas or 0,
            metas_concluidas=model.metas_concluidas or 0,
            alertas=model.alertas,
            analise_ia=model.analise_ia,
            risco_desvio=model.risco_desvio,
            tem_noticias=model.tem_noticias or False,
            noticias_relacionadas=model.noticias_relacionadas,
            documentos_comprobatórios=model.documentos_comprobatórios,
            fotos_georreferenciadas=model.fotos_georreferenciadas,
            validacao_geofencing=model.validacao_geofencing,
            processo_sei=model.processo_sei,
            link_portal_transparencia=model.link_portal_transparencia,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_sync=model.last_sync
        )
    
    def _to_model(self, entity: EmendaPix) -> EmendaPixModel:
        """Convert entity to model"""
        return EmendaPixModel(
            id=entity.id,
            numero_emenda=entity.numero_emenda,
            ano=entity.ano,
            tipo=entity.tipo,
            autor_nome=entity.autor_nome,
            autor_partido=entity.autor_partido,
            autor_uf=entity.autor_uf,
            destinatario_tipo=entity.destinatario_tipo,
            destinatario_nome=entity.destinatario_nome,
            destinatario_uf=entity.destinatario_uf,
            destinatario_cnpj=entity.destinatario_cnpj,
            valor_aprovado=entity.valor_aprovado,
            valor_empenhado=entity.valor_empenhado,
            valor_liquidado=entity.valor_liquidado,
            valor_pago=entity.valor_pago,
            objetivo=entity.objetivo,
            area=entity.area,
            descricao_detalhada=entity.descricao_detalhada,
            status_execucao=entity.status_execucao,
            percentual_executado=entity.percentual_executado,
            data_inicio=entity.data_inicio,
            data_prevista_conclusao=entity.data_prevista_conclusao,
            data_real_conclusao=entity.data_real_conclusao,
            plano_trabalho=entity.plano_trabalho,
            numero_metas=entity.numero_metas,
            metas_concluidas=entity.metas_concluidas,
            alertas=entity.alertas,
            analise_ia=entity.analise_ia,
            risco_desvio=entity.risco_desvio,
            tem_noticias=entity.tem_noticias,
            noticias_relacionadas=entity.noticias_relacionadas,
            documentos_comprobatórios=entity.documentos_comprobatórios,
            fotos_georreferenciadas=entity.fotos_georreferenciadas,
            validacao_geofencing=entity.validacao_geofencing,
            processo_sei=entity.processo_sei,
            link_portal_transparencia=entity.link_portal_transparencia
        )
    
    def _update_model(self, model: EmendaPixModel, entity: EmendaPix) -> None:
        """Update model from entity"""
        model.numero_emenda = entity.numero_emenda
        model.ano = entity.ano
        model.tipo = entity.tipo
        model.autor_nome = entity.autor_nome
        model.autor_partido = entity.autor_partido
        model.autor_uf = entity.autor_uf
        model.destinatario_tipo = entity.destinatario_tipo
        model.destinatario_nome = entity.destinatario_nome
        model.destinatario_uf = entity.destinatario_uf
        model.destinatario_cnpj = entity.destinatario_cnpj
        model.valor_aprovado = entity.valor_aprovado
        model.valor_empenhado = entity.valor_empenhado
        model.valor_liquidado = entity.valor_liquidado
        model.valor_pago = entity.valor_pago
        model.objetivo = entity.objetivo
        model.area = entity.area
        model.descricao_detalhada = entity.descricao_detalhada
        model.status_execucao = entity.status_execucao
        model.percentual_executado = entity.percentual_executado
        model.data_inicio = entity.data_inicio
        model.data_prevista_conclusao = entity.data_prevista_conclusao
        model.data_real_conclusao = entity.data_real_conclusao
        model.plano_trabalho = entity.plano_trabalho
        model.numero_metas = entity.numero_metas
        model.metas_concluidas = entity.metas_concluidas
        model.alertas = entity.alertas
        model.analise_ia = entity.analise_ia
        model.risco_desvio = entity.risco_desvio
        model.tem_noticias = entity.tem_noticias
        model.noticias_relacionadas = entity.noticias_relacionadas
        model.documentos_comprobatórios = entity.documentos_comprobatórios
        model.fotos_georreferenciadas = entity.fotos_georreferenciadas
        model.validacao_geofencing = entity.validacao_geofencing
        model.processo_sei = entity.processo_sei
        model.link_portal_transparencia = entity.link_portal_transparencia

