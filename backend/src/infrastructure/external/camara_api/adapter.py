"""Adapter to convert Câmara API data to domain entities"""
from datetime import datetime
from typing import Optional
from src.domain.entities.legislation import Legislation


class CamaraAPIAdapter:
    """Adapter to convert Câmara API responses to domain entities"""
    
    @staticmethod
    def to_legislation(proposal_data: dict, text: Optional[str] = None) -> Legislation:
        """
        Convert Câmara API proposal to Legislation entity
        
        Args:
            proposal_data: Proposal data from API
            text: Optional text content
            
        Returns:
            Legislation entity
        """
        # Parse dates
        data_apresentacao = proposal_data.get("dataApresentacao", "")
        try:
            created_at = datetime.fromisoformat(data_apresentacao.replace("Z", "+00:00"))
        except:
            created_at = datetime.utcnow()
        
        # Get status
        status_sigla = proposal_data.get("statusProposicao", {}).get("sigla", "DESCONHECIDO")
        
        # Get author - autores should be fetched from separate endpoint
        autor_nome = "Desconhecido"
        autores = proposal_data.get("autores", [])
        
        if autores and len(autores) > 0:
            # Get the first author (proponente=1 if available, otherwise first)
            autor = None
            for a in autores:
                if isinstance(a, dict) and a.get("proponente") == 1:
                    autor = a
                    break
            if not autor:
                autor = autores[0]
            
            if isinstance(autor, dict):
                # The API returns "nome" field directly
                autor_nome = autor.get("nome", "Desconhecido")
            elif isinstance(autor, str):
                autor_nome = autor
        
        # Use text if provided, otherwise use ementa
        content = text or proposal_data.get("ementa", "")
        
        return Legislation(
            id="",  # Will be generated
            external_id=str(proposal_data.get("id", "")),
            title=proposal_data.get("ementa", "Sem título"),
            content=content,
            author=autor_nome,
            status=status_sigla,
            created_at=created_at,
            updated_at=datetime.utcnow(),
        )



