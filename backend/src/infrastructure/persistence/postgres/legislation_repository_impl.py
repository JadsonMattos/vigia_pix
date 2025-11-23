"""PostgreSQL implementation of LegislationRepository"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.domain.entities.legislation import Legislation
from src.domain.repositories.legislation_repository import LegislationRepository
from src.infrastructure.persistence.postgres.models.legislation import LegislationModel


class PostgresLegislationRepository(LegislationRepository):
    """PostgreSQL implementation of LegislationRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, id: str) -> Optional[Legislation]:
        """Find legislation by ID"""
        result = await self.session.get(LegislationModel, id)
        return self._to_entity(result) if result else None
    
    async def find_by_external_id(self, external_id: str) -> Optional[Legislation]:
        """Find legislation by external ID"""
        stmt = select(LegislationModel).where(LegislationModel.external_id == external_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def find_all(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Legislation]:
        """Find all legislations"""
        stmt = select(LegislationModel).limit(limit).offset(offset).order_by(LegislationModel.created_at.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def save(self, legislation: Legislation) -> None:
        """Save or update legislation"""
        try:
            model = await self.session.get(LegislationModel, legislation.id)
            
            if model:
                # Update
                self._update_model(model, legislation)
            else:
                # Create
                model = self._to_model(legislation)
                self.session.add(model)
            
            await self.session.commit()
            await self.session.refresh(model)
        except Exception as e:
            # Rollback on error
            await self.session.rollback()
            raise
    
    async def delete(self, id: str) -> None:
        """Delete legislation"""
        model = await self.session.get(LegislationModel, id)
        if model:
            await self.session.delete(model)
            await self.session.commit()
    
    def _to_entity(self, model: LegislationModel) -> Legislation:
        """Convert model to entity"""
        return Legislation(
            id=str(model.id),
            external_id=model.external_id,
            title=model.title,
            content=model.content,
            author=model.author,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            simplified_content=model.simplified_content,
            complexity_score=model.complexity_score,
            impact_analysis=model.impact_analysis,
        )
    
    def _to_model(self, entity: Legislation) -> LegislationModel:
        """Convert entity to model"""
        return LegislationModel(
            id=entity.id,
            external_id=entity.external_id,
            title=entity.title,
            content=entity.content,
            author=entity.author,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            simplified_content=entity.simplified_content,
            complexity_score=entity.complexity_score,
            impact_analysis=entity.impact_analysis,
        )
    
    def _update_model(self, model: LegislationModel, entity: Legislation):
        """Update model with entity data"""
        model.external_id = entity.external_id
        model.title = entity.title
        model.content = entity.content
        model.author = entity.author
        model.status = entity.status
        model.updated_at = entity.updated_at
        model.simplified_content = entity.simplified_content
        model.complexity_score = entity.complexity_score
        model.impact_analysis = entity.impact_analysis



