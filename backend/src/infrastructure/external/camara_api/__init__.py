"""Câmara dos Deputados API integration"""
from src.infrastructure.external.camara_api.client import CamaraAPIClient
from src.infrastructure.external.camara_api.adapter import CamaraAPIAdapter

__all__ = ["CamaraAPIClient", "CamaraAPIAdapter"]



