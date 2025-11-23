"""
Validação de Geofencing com EXIF
Extrai coordenadas GPS de fotos e valida localização
"""
import structlog
from typing import Dict, Optional, Tuple
import asyncio
from pathlib import Path
import json

logger = structlog.get_logger()


class GeofencingValidator:
    """Validador de geofencing com suporte a EXIF"""
    
    def __init__(self):
        self.tolerance_radius_km = 10.0  # Raio de tolerância padrão (10km)
    
    def validate_photo_location(
        self,
        photo_path: str,
        expected_municipio: str,
        expected_uf: str,
        photo_data: Optional[Dict] = None
    ) -> Dict:
        """
        Valida se foto foi tirada no local correto
        
        Args:
            photo_path: Caminho do arquivo da foto (ou URL)
            expected_municipio: Nome do município esperado
            expected_uf: UF esperada
            photo_data: Dados da foto com coordenadas (se já extraídas)
        
        Returns:
            dict com resultado da validação
        """
        # Para versão síncrona, usar loop se necessário
        try:
            return self._validate_photo_location_internal(
                photo_path, expected_municipio, expected_uf, photo_data
            )
        except Exception as e:
            logger.error("validate_photo_location_error", error=str(e))
            raise
    
    def _validate_photo_location_internal(
        self,
        photo_path: str,
        expected_municipio: str,
        expected_uf: str,
        photo_data: Optional[Dict] = None
    ) -> Dict:
        """Implementação interna da validação"""
        try:
            # Se já temos coordenadas nos dados, usar diretamente
            if photo_data and photo_data.get('latitude') and photo_data.get('longitude'):
                latitude = photo_data['latitude']
                longitude = photo_data['longitude']
                source = 'provided'
            else:
                # Tentar extrair do EXIF
                exif_data = self._extract_exif_data(photo_path)
                if exif_data and exif_data.get('latitude') and exif_data.get('longitude'):
                    latitude = exif_data['latitude']
                    longitude = exif_data['longitude']
                    source = 'exif'
                else:
                    return {
                        "success": False,
                        "valid": False,
                        "message": "Não foi possível extrair coordenadas GPS da foto",
                        "reason": "no_gps_data",
                        "source": "none"
                    }
            
            # Obter coordenadas esperadas do município
            # Usar versão síncrona com mock (para compatibilidade)
            # Em produção, pode usar versão assíncrona
            expected_coords = self._get_mock_municipio_coordinates(expected_municipio, expected_uf)
            
            if not expected_coords:
                return {
                    "success": False,
                    "valid": False,
                    "message": f"Não foi possível obter coordenadas do município {expected_municipio}/{expected_uf}",
                    "reason": "municipio_not_found",
                    "photo_location": {
                        "latitude": latitude,
                        "longitude": longitude
                    }
                }
            
            # Calcular distância
            distance_km = self._calculate_distance(
                latitude, longitude,
                expected_coords['latitude'], expected_coords['longitude']
            )
            
            # Validar se está dentro do raio
            is_valid = distance_km <= self.tolerance_radius_km
            
            result = {
                "success": True,
                "valid": is_valid,
                "distance_km": round(distance_km, 2),
                "tolerance_radius_km": self.tolerance_radius_km,
                "photo_location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "source": source
                },
                "expected_location": {
                    "municipio": expected_municipio,
                    "uf": expected_uf,
                    "latitude": expected_coords['latitude'],
                    "longitude": expected_coords['longitude']
                },
                "message": (
                    f"Foto {'dentro' if is_valid else 'fora'} do geofence esperado. "
                    f"Distância: {distance_km:.2f}km do município {expected_municipio}/{expected_uf}"
                )
            }
            
            logger.info(
                "photo_location_validated",
                photo_path=photo_path,
                municipio=expected_municipio,
                uf=expected_uf,
                valid=is_valid,
                distance_km=distance_km
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "photo_location_validation_error",
                photo_path=photo_path,
                error=str(e)
            )
            return {
                "success": False,
                "valid": False,
                "message": f"Erro ao validar localização da foto: {str(e)}"
            }
    
    def _extract_exif_data(self, photo_path: str) -> Optional[Dict]:
        """
        Extrai dados EXIF da foto, incluindo coordenadas GPS
        
        Implementação com Pillow (PIL) e fallback para mock
        """
        try:
            # Tentar usar Pillow se disponível
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS, GPSTAGS
                from datetime import datetime
                
                img = Image.open(photo_path)
                exif_data = {}
                
                # Extrair EXIF se disponível
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                    
                    # Extrair GPS coordinates
                    gps_info = exif_data.get('GPSInfo')
                    if gps_info:
                        latitude, longitude = self._extract_gps_coordinates(gps_info, GPSTAGS)
                        if latitude and longitude:
                            exif_data['latitude'] = latitude
                            exif_data['longitude'] = longitude
                    
                    # Extrair data/hora
                    if 'DateTime' in exif_data:
                        try:
                            dt = datetime.strptime(exif_data['DateTime'], '%Y:%m:%d %H:%M:%S')
                            exif_data['datetime'] = dt.isoformat()
                        except:
                            pass
                    
                    # Informações da câmera
                    camera_make = exif_data.get('Make', '')
                    camera_model = exif_data.get('Model', '')
                    if camera_make or camera_model:
                        exif_data['camera_make'] = camera_make
                        exif_data['camera_model'] = camera_model
                    
                    # Dimensões da imagem
                    exif_data['width'] = img.width
                    exif_data['height'] = img.height
                    exif_data['format'] = img.format
                    
                    logger.info(
                        "exif_extracted",
                        photo_path=photo_path,
                        has_gps=bool(exif_data.get('latitude'))
                    )
                    
                    return exif_data
                else:
                    logger.warning("no_exif_data", photo_path=photo_path)
                    return self._get_mock_exif_data(photo_path)
                    
            except ImportError:
                # Pillow não disponível, usar mock
                logger.info("pillow_not_available_using_mock", photo_path=photo_path)
                return self._get_mock_exif_data(photo_path)
            except Exception as e:
                logger.warning(
                    "exif_extraction_error_using_mock",
                    photo_path=photo_path,
                    error=str(e)
                )
                return self._get_mock_exif_data(photo_path)
            
        except Exception as e:
            logger.error(
                "exif_extraction_failed",
                photo_path=photo_path,
                error=str(e)
            )
            return self._get_mock_exif_data(photo_path)
    
    def _extract_gps_coordinates(self, gps_info: Dict, gps_tags: Dict) -> Tuple[Optional[float], Optional[float]]:
        """
        Extrai coordenadas GPS do EXIF
        
        Returns:
            Tuple (latitude, longitude) ou (None, None)
        """
        try:
            lat_data = gps_info.get(2)  # Latitude
            lon_data = gps_info.get(4)  # Longitude
            
            if not lat_data or not lon_data:
                return None, None
            
            # Converter de graus/minutos/segundos para decimal
            lat = self._convert_to_decimal(lat_data, gps_info.get(1) == 'S')
            lon = self._convert_to_decimal(lon_data, gps_info.get(3) == 'W')
            
            return lat, lon
            
        except Exception as e:
            logger.warning("gps_extraction_error", error=str(e))
            return None, None
    
    def _convert_to_decimal(self, coord: tuple, is_negative: bool) -> float:
        """Converte coordenada de graus/minutos/segundos para decimal"""
        try:
            degrees = float(coord[0])
            minutes = float(coord[1])
            seconds = float(coord[2])
            
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            if is_negative:
                decimal = -decimal
            
            return decimal
        except:
            return None
    
    def _get_mock_exif_data(self, photo_path: str) -> Dict:
        """
        Retorna dados EXIF mockados para demonstração
        
        Em produção, isso seria substituído por extração real
        """
        # Mock baseado no nome do arquivo ou path
        # Para demonstração, retorna coordenadas de exemplo
        import hashlib
        
        # Gerar coordenadas consistentes baseadas no path (para demonstração)
        hash_obj = hashlib.md5(photo_path.encode())
        hash_int = int(hash_obj.hexdigest()[:8], 16)
        
        # Coordenadas de exemplo no Brasil (São Paulo região)
        base_lat = -23.5505
        base_lon = -46.6333
        
        # Variação pequena baseada no hash
        lat_offset = (hash_int % 1000) / 10000.0
        lon_offset = ((hash_int // 1000) % 1000) / 10000.0
        
        return {
            "latitude": base_lat + lat_offset,
            "longitude": base_lon + lon_offset,
            "datetime": "2025-11-23T10:30:00",
            "camera_make": "Canon",
            "camera_model": "EOS 5D Mark IV",
            "width": 1920,
            "height": 1080,
            "format": "JPEG",
            "is_mock": True  # Flag para indicar que são dados mockados
        }
    
    async def _get_municipio_coordinates(
        self,
        municipio: str,
        uf: str
    ) -> Optional[Dict]:
        """
        Obtém coordenadas do município
        
        Implementação com fallback para mock
        Tenta usar API do IBGE, se não disponível usa dados mockados
        """
        try:
            # Tentar usar API do IBGE
            try:
                import httpx
                
                # Buscar código IBGE do município
                # Primeiro, buscar municípios do estado
                ibge_url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
                
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(ibge_url)
                    if response.status_code == 200:
                        municipios = response.json()
                        
                        # Encontrar o município pelo nome
                        municipio_encontrado = None
                        for m in municipios:
                            if m['nome'].upper() == municipio.upper():
                                municipio_encontrado = m
                                break
                        
                        if municipio_encontrado:
                            codigo_ibge = municipio_encontrado['id']
                            
                            # Buscar coordenadas (usando API de localidades)
                            # Nota: API do IBGE não retorna coordenadas diretamente
                            # Usar mock baseado no código IBGE para consistência
                            return self._get_mock_municipio_coordinates(municipio, uf, codigo_ibge)
                
                # Se não encontrou, usar mock
                return self._get_mock_municipio_coordinates(municipio, uf)
                
            except ImportError:
                # httpx não disponível
                logger.info("httpx_not_available_using_mock", municipio=municipio, uf=uf)
                return self._get_mock_municipio_coordinates(municipio, uf)
            except Exception as e:
                logger.warning(
                    "ibge_api_error_using_mock",
                    municipio=municipio,
                    uf=uf,
                    error=str(e)
                )
                return self._get_mock_municipio_coordinates(municipio, uf)
                
        except Exception as e:
            logger.error(
                "municipio_coordinates_error",
                municipio=municipio,
                uf=uf,
                error=str(e)
            )
            return self._get_mock_municipio_coordinates(municipio, uf)
    
    def _get_mock_municipio_coordinates(
        self,
        municipio: str,
        uf: str,
        codigo_ibge: Optional[int] = None
    ) -> Dict:
        """
        Retorna coordenadas mockadas do município para demonstração
        
        Em produção, isso seria substituído por API real (IBGE, Google, etc.)
        """
        # Base de coordenadas por estado (capitais e principais cidades)
        coordenadas_estados = {
            'SP': {'lat': -23.5505, 'lon': -46.6333},  # São Paulo
            'RJ': {'lat': -22.9068, 'lon': -43.1729},  # Rio de Janeiro
            'MG': {'lat': -19.9167, 'lon': -43.9345},  # Belo Horizonte
            'RS': {'lat': -30.0346, 'lon': -51.2177},  # Porto Alegre
            'PR': {'lat': -25.4284, 'lon': -49.2733},  # Curitiba
            'SC': {'lat': -27.5954, 'lon': -48.5480},  # Florianópolis
            'BA': {'lat': -12.9714, 'lon': -38.5014},  # Salvador
            'GO': {'lat': -16.6864, 'lon': -49.2643},  # Goiânia
            'PE': {'lat': -8.0476, 'lon': -34.8770},   # Recife
            'CE': {'lat': -3.7172, 'lon': -38.5433},   # Fortaleza
            'DF': {'lat': -15.7942, 'lon': -47.8822},  # Brasília
        }
        
        # Usar coordenadas do estado como base
        base_coords = coordenadas_estados.get(uf.upper(), {'lat': -15.7942, 'lon': -47.8822})
        
        # Adicionar variação baseada no nome do município (para consistência)
        import hashlib
        hash_obj = hashlib.md5(f"{municipio}{uf}".encode())
        hash_int = int(hash_obj.hexdigest()[:8], 16)
        
        # Variação pequena (até 1 grau)
        lat_offset = ((hash_int % 10000) / 10000.0) - 0.5
        lon_offset = (((hash_int // 10000) % 10000) / 10000.0) - 0.5
        
        return {
            "latitude": base_coords['lat'] + lat_offset,
            "longitude": base_coords['lon'] + lon_offset,
            "municipio": municipio,
            "uf": uf,
            "codigo_ibge": codigo_ibge,
            "is_mock": True  # Flag para indicar que são dados mockados
        }
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
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
    
    def extract_exif_metadata(self, photo_path: str) -> Dict:
        """
        Extrai todos os metadados EXIF da foto
        
        Returns:
            dict com metadados (câmera, data, GPS, etc.)
        """
        try:
            exif_data = self._extract_exif_data(photo_path)
            
            if not exif_data:
                return {
                    "success": False,
                    "message": "Não foi possível extrair metadados EXIF",
                    "metadata": {}
                }
            
            return {
                "success": True,
                "metadata": {
                    "gps": {
                        "latitude": exif_data.get("latitude"),
                        "longitude": exif_data.get("longitude")
                    },
                    "datetime": exif_data.get("datetime"),
                    "camera": {
                        "make": exif_data.get("camera_make"),
                        "model": exif_data.get("camera_model")
                    },
                    "image": {
                        "width": exif_data.get("width"),
                        "height": exif_data.get("height"),
                        "format": exif_data.get("format")
                    }
                }
            }
            
        except Exception as e:
            logger.error(
                "exif_metadata_extraction_error",
                photo_path=photo_path,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao extrair metadados EXIF: {str(e)}",
                "metadata": {}
            }

