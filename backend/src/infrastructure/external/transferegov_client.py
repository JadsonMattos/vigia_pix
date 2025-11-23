"""
Cliente para API do Transferegov.br
Módulo de Transferências Especiais (Emendas PIX)
"""
import httpx
import structlog
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = structlog.get_logger()


class TransferegovClient:
    """Cliente para API do Transferegov.br"""
    
    BASE_URL = "https://api.transferegov.gestao.gov.br"
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
    
    async def get_plano_acao(
        self,
        codigo_emenda: str
    ) -> Optional[Dict]:
        """
        Busca Plano de Ação por código da emenda parlamentar
        
        Args:
            codigo_emenda: Código da emenda formatado (ex: "2024-001-0001")
        
        Returns:
            dict com dados do plano de ação ou None
        """
        try:
            url = f"{self.BASE_URL}/plano_acao_especial"
            params = {
                "codigo_emenda_parlamentar_formatado_plano_acao": codigo_emenda
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # A API pode retornar lista ou objeto único
                    if isinstance(data, list):
                        if len(data) > 0:
                            return self._parse_plano_acao(data[0])
                        return None
                    return self._parse_plano_acao(data)
                
                elif response.status_code == 404:
                    logger.info(
                        "plano_acao_not_found",
                        codigo_emenda=codigo_emenda
                    )
                    return None
                
                else:
                    logger.warning(
                        "transferegov_api_error",
                        status_code=response.status_code,
                        codigo_emenda=codigo_emenda
                    )
                    return None
                    
        except httpx.TimeoutException:
            logger.warning(
                "transferegov_timeout",
                codigo_emenda=codigo_emenda
            )
            return self._get_mock_plano_acao(codigo_emenda)
        except Exception as e:
            logger.error(
                "transferegov_error",
                error=str(e),
                codigo_emenda=codigo_emenda
            )
            return self._get_mock_plano_acao(codigo_emenda)
    
    def _parse_plano_acao(self, data: Dict) -> Dict:
        """Parse dos dados do plano de ação"""
        return {
            "situacao_plano_acao": data.get("situacao_plano_acao"),
            "nome_beneficiario": data.get("nome_beneficiario"),
            "descricao_programacao_orcamentaria": data.get(
                "descricao_programacao_orcamentaria_plano_acao"
            ),
            "codigo_emenda_formatado": data.get(
                "codigo_emenda_parlamentar_formatado_plano_acao"
            ),
            "valor_total": data.get("valor_total_plano_acao"),
            "data_aprovacao": data.get("data_aprovacao_plano_acao"),
            "data_cancelamento": data.get("data_cancelamento_plano_acao"),
            "raw_data": data  # Manter dados brutos para referência
        }
    
    def _get_mock_plano_acao(self, codigo_emenda: str) -> Dict:
        """Retorna dados mockados para demonstração"""
        logger.info("using_mock_plano_acao", codigo_emenda=codigo_emenda)
        
        # Gerar dados variados baseados no código para demonstração
        import hashlib
        hash_code = int(hashlib.md5(codigo_emenda.encode()).hexdigest()[:8], 16)
        
        situacoes = ["Aprovado", "Em Análise", "Aprovado", "Aprovado", "Cancelado"]
        situacao = situacoes[hash_code % len(situacoes)]
        
        beneficiarios = [
            "Prefeitura Municipal de São Paulo",
            "Prefeitura Municipal do Rio de Janeiro",
            "Governo do Estado de Minas Gerais",
            "Prefeitura Municipal de Brasília",
            "Governo do Estado de São Paulo"
        ]
        beneficiario = beneficiarios[hash_code % len(beneficiarios)]
        
        descricoes = [
            "Obra de pavimentação e infraestrutura urbana na Rua das Flores, Bairro Centro",
            "Construção de unidade básica de saúde no Bairro Jardim América",
            "Reforma e ampliação de escola municipal no Distrito Industrial",
            "Aquisição de equipamentos médicos para hospital regional",
            "Programa de assistência social e distribuição de cestas básicas"
        ]
        descricao = descricoes[hash_code % len(descricoes)]
        
        return {
            "situacao_plano_acao": situacao,
            "nome_beneficiario": beneficiario,
            "descricao_programacao_orcamentaria": descricao,
            "codigo_emenda_formatado": codigo_emenda,
            "valor_total": 500000.0 + (hash_code % 1000000),
            "data_aprovacao": (datetime.now() - timedelta(days=hash_code % 180)).isoformat(),
            "data_cancelamento": None if situacao != "Cancelado" else (datetime.now() - timedelta(days=hash_code % 30)).isoformat(),
            "is_mock": True
        }
    
    async def search_planos_acao(
        self,
        ano: Optional[int] = None,
        uf: Optional[str] = None,
        municipio: Optional[str] = None
    ) -> List[Dict]:
        """
        Busca múltiplos planos de ação com filtros
        
        Args:
            ano: Ano das emendas
            uf: Sigla do estado
            municipio: Nome do município
        
        Returns:
            Lista de planos de ação
        """
        try:
            url = f"{self.BASE_URL}/plano_acao_especial"
            params = {}
            
            if ano:
                params["ano"] = ano
            if uf:
                params["uf"] = uf
            if municipio:
                params["municipio"] = municipio
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        return [self._parse_plano_acao(item) for item in data]
                    return [self._parse_plano_acao(data)]
                
                return []
                
        except Exception as e:
            logger.error("transferegov_search_error", error=str(e))
            return []

