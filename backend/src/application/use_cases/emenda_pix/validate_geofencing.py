"""
Use case para validar geofencing de fotos/documentos
Conceito de Triangulação de Dados - Fonte Física
"""
from typing import Dict, List, Optional
import structlog
from datetime import datetime

from src.domain.entities.emenda_pix import EmendaPix

logger = structlog.get_logger()


class ValidateGeofencingUseCase:
    """Valida geofencing de fotos/documentos comprobatórios"""
    
    def validate(self, emenda: EmendaPix, foto_data: Dict) -> Dict:
        """
        Valida se foto/documento está dentro do geofence esperado
        
        Args:
            emenda: Emenda Pix
            foto_data: Dados da foto com coordenadas GPS
        
        Returns:
            dict com resultado da validação
        """
        try:
            # Extrair coordenadas da foto
            latitude = foto_data.get('latitude')
            longitude = foto_data.get('longitude')
            
            if not latitude or not longitude:
                return {
                    "success": False,
                    "valid": False,
                    "message": "Foto não contém coordenadas GPS",
                    "reason": "missing_coordinates"
                }
            
            # Obter coordenadas esperadas do destinatário
            expected_location = self._get_expected_location(emenda)
            
            if not expected_location:
                return {
                    "success": False,
                    "valid": False,
                    "message": "Não foi possível determinar localização esperada",
                    "reason": "missing_expected_location"
                }
            
            # Calcular distância (Haversine)
            distance_km = self._calculate_distance(
                latitude, longitude,
                expected_location['latitude'], expected_location['longitude']
            )
            
            # Raio de tolerância (em km) - pode ser configurável
            tolerance_radius_km = 10.0  # 10km de raio
            
            is_valid = distance_km <= tolerance_radius_km
            
            result = {
                "success": True,
                "valid": is_valid,
                "distance_km": round(distance_km, 2),
                "tolerance_radius_km": tolerance_radius_km,
                "foto_location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "expected_location": expected_location,
                "message": (
                    f"Foto {'dentro' if is_valid else 'fora'} do geofence esperado. "
                    f"Distância: {distance_km:.2f}km"
                )
            }
            
            logger.info(
                "geofencing_validated",
                emenda_id=emenda.id,
                valid=is_valid,
                distance_km=distance_km
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "geofencing_validation_error",
                emenda_id=emenda.id,
                error=str(e)
            )
            return {
                "success": False,
                "valid": False,
                "message": f"Erro ao validar geofencing: {str(e)}"
            }
    
    def _get_expected_location(self, emenda: EmendaPix) -> Optional[Dict]:
        """
        Obtém localização esperada baseada no destinatário
        
        TODO: Integrar com API de geocodificação ou banco de coordenadas
        Por enquanto, retorna None (será implementado com dados reais)
        """
        # Placeholder - em produção, buscaria coordenadas do município/estado
        # Exemplo: API do IBGE, Google Geocoding, etc.
        
        # Por enquanto, retorna None para indicar que precisa de implementação
        return None
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula distância entre duas coordenadas usando fórmula de Haversine
        
        Returns:
            Distância em quilômetros
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Raio da Terra em km
        R = 6371.0
        
        # Converter para radianos
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Diferenças
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Fórmula de Haversine
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        
        return distance
    
    def validate_multiple(self, emenda: EmendaPix, fotos: List[Dict]) -> Dict:
        """
        Valida múltiplas fotos/documentos
        
        Returns:
            dict com resultados de todas as validações
        """
        results = []
        valid_count = 0
        
        for foto in fotos:
            result = self.validate(emenda, foto)
            results.append({
                "foto_id": foto.get('id', 'unknown'),
                **result
            })
            if result.get('valid'):
                valid_count += 1
        
        return {
            "success": True,
            "total": len(fotos),
            "valid": valid_count,
            "invalid": len(fotos) - valid_count,
            "results": results,
            "overall_valid": valid_count == len(fotos) and len(fotos) > 0
        }

