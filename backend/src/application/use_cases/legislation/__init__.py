"""Legislation use cases"""
from src.application.use_cases.legislation.get_legislation import GetLegislationUseCase
from src.application.use_cases.legislation.list_legislations import ListLegislationsUseCase
from src.application.use_cases.legislation.sync_legislations import SyncLegislationsUseCase
from src.application.use_cases.legislation.simplify_legislation import SimplifyLegislationUseCase

__all__ = [
    "GetLegislationUseCase", 
    "ListLegislationsUseCase", 
    "SyncLegislationsUseCase",
    "SimplifyLegislationUseCase"
]

