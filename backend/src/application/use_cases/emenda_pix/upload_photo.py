"""
Use case para upload de foto com validação de geofencing
"""
from typing import Dict, Optional
import structlog
from datetime import datetime
import uuid

from src.domain.entities.emenda_pix import EmendaPix
from src.domain.repositories.emenda_pix_repository import EmendaPixRepository
from src.infrastructure.validation.geofencing import GeofencingValidator

logger = structlog.get_logger()


class UploadPhotoUseCase:
    """Upload de foto com validação de geofencing"""
    
    def __init__(
        self,
        repository: EmendaPixRepository,
        geofencing_validator: Optional[GeofencingValidator] = None
    ):
        self.repository = repository
        self.validator = geofencing_validator or GeofencingValidator()
    
    async def execute(
        self,
        emenda_id: str,
        photo_url: str,
        photo_path: Optional[str] = None,
        photo_data: Optional[Dict] = None,
        validate_location: bool = True
    ) -> Dict:
        """
        Faz upload de foto e valida geofencing
        
        Args:
            emenda_id: ID da emenda
            photo_url: URL da foto (após upload)
            photo_path: Caminho local da foto (para extrair EXIF)
            photo_data: Dados da foto (coordenadas, tipo, etc.)
            validate_location: Se deve validar localização
        
        Returns:
            dict com resultado do upload e validação
        """
        try:
            # Buscar emenda
            from src.application.use_cases.emenda_pix import GetEmendaPixUseCase
            get_use_case = GetEmendaPixUseCase(self.repository)
            emenda = await get_use_case.execute(emenda_id)
            
            if not emenda:
                return {
                    "success": False,
                    "message": "Emenda não encontrada"
                }
            
            # Preparar dados da foto
            foto_id = str(uuid.uuid4())
            foto_data = {
                "id": foto_id,
                "url": photo_url,
                "tipo": photo_data.get("tipo", "foto_obra") if photo_data else "foto_obra",
                "data_upload": datetime.now().isoformat(),
                "latitude": None,
                "longitude": None,
                "validacao_geofencing": None
            }
            
            # Extrair coordenadas se disponíveis
            if photo_data and photo_data.get("latitude") and photo_data.get("longitude"):
                foto_data["latitude"] = photo_data["latitude"]
                foto_data["longitude"] = photo_data["longitude"]
            elif photo_path:
                # Tentar extrair do EXIF
                exif_result = self.validator.extract_exif_metadata(photo_path)
                if exif_result.get("success") and exif_result.get("metadata", {}).get("gps"):
                    gps = exif_result["metadata"]["gps"]
                    foto_data["latitude"] = gps.get("latitude")
                    foto_data["longitude"] = gps.get("longitude")
            
            # Validar geofencing se solicitado
            if validate_location and foto_data.get("latitude") and foto_data.get("longitude"):
                # Usar validação síncrona (com fallback interno para mock)
                validation_result = self.validator.validate_photo_location(
                    photo_path=photo_path or photo_url,
                    expected_municipio=emenda.destinatario_nome,
                    expected_uf=emenda.destinatario_uf or "",
                    photo_data={
                        "latitude": foto_data["latitude"],
                        "longitude": foto_data["longitude"]
                    }
                )
                
                foto_data["validacao_geofencing"] = validation_result.get("valid", False)
                
                if not validation_result.get("success"):
                    logger.warning(
                        "geofencing_validation_failed",
                        emenda_id=emenda_id,
                        foto_id=foto_id,
                        reason=validation_result.get("reason")
                    )
            elif validate_location:
                # Não foi possível validar (sem coordenadas)
                foto_data["validacao_geofencing"] = None
                logger.warning(
                    "geofencing_validation_skipped",
                    emenda_id=emenda_id,
                    foto_id=foto_id,
                    reason="no_coordinates"
                )
            
            # Adicionar foto à emenda
            if not emenda.fotos_georreferenciadas:
                emenda.fotos_georreferenciadas = []
            
            emenda.fotos_georreferenciadas.append(foto_data)
            
            # Atualizar status de validação geral
            if foto_data.get("validacao_geofencing") is not None:
                # Se todas as fotos estão validadas e válidas
                todas_validas = all(
                    f.get("validacao_geofencing") is True
                    for f in emenda.fotos_georreferenciadas
                    if f.get("validacao_geofencing") is not None
                )
                emenda.validacao_geofencing = todas_validas if len(emenda.fotos_georreferenciadas) > 0 else None
            
            # Salvar emenda
            await self.repository.save(emenda)
            
            logger.info(
                "photo_uploaded",
                emenda_id=emenda_id,
                foto_id=foto_id,
                validacao_geofencing=foto_data.get("validacao_geofencing")
            )
            
            return {
                "success": True,
                "foto_id": foto_id,
                "foto_data": foto_data,
                "validacao_geofencing": foto_data.get("validacao_geofencing"),
                "message": "Foto enviada com sucesso"
            }
            
        except Exception as e:
            logger.error(
                "photo_upload_error",
                emenda_id=emenda_id,
                error=str(e)
            )
            return {
                "success": False,
                "message": f"Erro ao fazer upload da foto: {str(e)}"
            }

