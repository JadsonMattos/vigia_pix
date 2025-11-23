"""Emenda Pix routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict

from src.infrastructure.persistence.postgres.database import get_db
from src.infrastructure.persistence.postgres.emenda_pix_repository_impl import PostgresEmendaPixRepository
from src.application.use_cases.emenda_pix import (
    GetEmendaPixUseCase,
    ListEmendasPixUseCase,
    AnalyzeEmendaPixIAUseCase
)
from src.application.use_cases.emenda_pix.calculate_trust_score import CalculateTrustScoreUseCase
from src.application.use_cases.emenda_pix.sync_emendas_portal import SyncEmendasPortalUseCase
from src.application.use_cases.emenda_pix.sync_ceis_data import SyncCEISDataUseCase
from src.application.use_cases.emenda_pix.fetch_news import FetchEmendaNewsUseCase
from src.application.use_cases.emenda_pix.register_blockchain import RegisterBlockchainUseCase
from src.application.use_cases.emenda_pix.compare_emendas import CompareEmendasUseCase
from src.application.use_cases.emenda_pix.validate_geofencing import ValidateGeofencingUseCase
from src.application.use_cases.emenda_pix.upload_photo import UploadPhotoUseCase
from src.application.dto.emenda_pix_dto import EmendaPixDTO, EmendaPixListResponse

router = APIRouter(prefix="/emenda-pix", tags=["emenda-pix"])


def get_emenda_pix_repository(
    session: AsyncSession = Depends(get_db)
) -> PostgresEmendaPixRepository:
    """Dependency for emenda pix repository"""
    return PostgresEmendaPixRepository(session)


def get_get_emenda_use_case(
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
) -> GetEmendaPixUseCase:
    """Dependency for get emenda use case"""
    return GetEmendaPixUseCase(repository)


def get_list_emendas_use_case(
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
) -> ListEmendasPixUseCase:
    """Dependency for list emendas use case"""
    return ListEmendasPixUseCase(repository)


@router.get("/", response_model=EmendaPixListResponse)
async def list_emendas(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    autor_nome: Optional[str] = Query(None),
    destinatario_uf: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    status_execucao: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None, description="Tipo de emenda: 'individual' ou 'bancada'"),
    use_case: ListEmendasPixUseCase = Depends(get_list_emendas_use_case)
):
    """
    List Emendas Pix with pagination and filters
    
    - **limit**: Maximum number of results (1-1000)
    - **offset**: Number of results to skip
    - **autor_nome**: Filter by author name (partial match)
    - **destinatario_uf**: Filter by recipient state (UF)
    - **area**: Filter by area (saude, educacao, infraestrutura, etc.)
    - **status_execucao**: Filter by execution status
    - **tipo**: Filter by emenda type ('individual' or 'bancada')
    """
    emendas = await use_case.execute(
        limit=limit,
        offset=offset,
        autor_nome=autor_nome,
        destinatario_uf=destinatario_uf,
        area=area,
        status_execucao=status_execucao,
        tipo=tipo
    )
    
    return EmendaPixListResponse(
        items=[EmendaPixDTO.model_validate(e) for e in emendas],
        total=len(emendas),
        limit=limit,
        offset=offset
    )


@router.get("/{emenda_id}", response_model=EmendaPixDTO)
async def get_emenda(
    emenda_id: str,
    use_case: GetEmendaPixUseCase = Depends(get_get_emenda_use_case)
):
    """
    Get Emenda Pix by ID
    
    - **emenda_id**: ID of the emenda
    """
    emenda = await use_case.execute(emenda_id)
    if not emenda:
        raise HTTPException(status_code=404, detail="Emenda not found")
    return EmendaPixDTO.model_validate(emenda)


@router.post("/{emenda_id}/analyze-invoice")
async def analyze_invoice(
    emenda_id: str,
    xml_content: str = Query(..., description="Conteúdo XML da nota fiscal"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Analisa nota fiscal XML e compara com objetivo da emenda
    
    - **emenda_id**: ID da emenda
    - **xml_content**: Conteúdo XML da nota fiscal (NFe)
    
    **NLP para Notas Fiscais**:
    - Extrai itens da nota fiscal
    - Compara semanticamente com objetivo da emenda
    - Detecta inconsistências
    
    Returns:
        dict com análise da nota fiscal
    """
    from src.infrastructure.ai.invoice_analyzer import InvoiceAnalyzer
    
    emenda = await repository.find_by_id(emenda_id)
    
    if not emenda:
        raise HTTPException(status_code=404, detail="Emenda não encontrada")
    
    analyzer = InvoiceAnalyzer()
    result = analyzer.analyze_invoice_xml(
        xml_content=xml_content,
        emenda_objetivo=emenda.objetivo or ""
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Erro ao analisar nota fiscal")
        )
    
    return result


@router.post("/{emenda_id}/analyze")
async def analyze_emenda(
    emenda_id: str,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Analyze Emenda Pix with AI
    
    - **emenda_id**: ID of the emenda to analyze
    
    This endpoint uses AI to:
    - Calculate execution percentage
    - Detect delays
    - Generate alerts
    - Calculate risk of deviation
    - Generate recommendations
    - Analyze invoices (if available)
    """
    use_case = AnalyzeEmendaPixIAUseCase(repository)
    
    try:
        emenda = await use_case.execute(emenda_id)
        return EmendaPixDTO.model_validate(emenda)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing emenda: {str(e)}")


@router.get("/autor/{autor_nome}", response_model=EmendaPixListResponse)
async def get_emendas_by_autor(
    autor_nome: str,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Get all Emendas Pix by author name
    
    - **autor_nome**: Name of the author (deputado)
    """
    emendas = await repository.find_by_autor(autor_nome)
    
    return EmendaPixListResponse(
        items=[EmendaPixDTO.model_validate(e) for e in emendas],
        total=len(emendas),
        limit=len(emendas),
        offset=0
    )


@router.get("/destinatario/{destinatario_nome}", response_model=EmendaPixListResponse)
async def get_emendas_by_destinatario(
    destinatario_nome: str,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Get all Emendas Pix by recipient name
    
    - **destinatario_nome**: Name of the recipient (município, estado, órgão)
    """
    emendas = await repository.find_by_destinatario(destinatario_nome)
    
    return EmendaPixListResponse(
        items=[EmendaPixDTO.model_validate(e) for e in emendas],
        total=len(emendas),
        limit=len(emendas),
        offset=0
    )


@router.post("/sync")
async def sync_emendas_portal(
    ano: Optional[int] = Query(None, description="Ano das emendas (padrão: ano atual)"),
    codigo_ibge: Optional[str] = Query(None, description="Código IBGE do município (opcional)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de emendas a sincronizar"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Sincroniza emendas Pix do Portal da Transparência
    
    - **ano**: Ano das emendas (padrão: ano atual)
    - **codigo_ibge**: Código IBGE do município (opcional)
    - **limit**: Limite de emendas a sincronizar (1-1000)
    
    Nota: Esta funcionalidade está preparada para integração com dados reais.
    Para a demo, pode retornar dados simulados se a API não estiver disponível.
    """
    use_case = SyncEmendasPortalUseCase(repository)
    
    try:
        result = await use_case.execute(
            ano=ano,
            codigo_ibge=codigo_ibge,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao sincronizar emendas: {str(e)}"
        )


@router.post("/{emenda_id}/sync-ceis")
async def sync_ceis_data(
    emenda_id: str,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Sincroniza dados do CEIS e processos eletrônicos para uma emenda específica
    
    - **emenda_id**: ID da emenda
    
    Esta funcionalidade:
    - Busca plano de trabalho do processo SEI
    - Atualiza status das metas
    - Busca entregas e documentos comprobatórios
    - Verifica se empresa destinatária está no CEIS
    
    Nota: Requer que a emenda tenha um processo SEI vinculado.
    """
    use_case = SyncCEISDataUseCase(repository)
    
    try:
        result = await use_case.execute(emenda_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao sincronizar dados do CEIS: {str(e)}"
        )


@router.post("/sync-ceis/all")
async def sync_all_ceis_data(
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Sincroniza dados do CEIS para todas as emendas que possuem processo SEI
    
    Esta funcionalidade processa todas as emendas em lote, atualizando:
    - Planos de trabalho
    - Status das metas
    - Entregas e documentos
    - Verificação de empresas no CEIS
    """
    use_case = SyncCEISDataUseCase(repository)
    
    try:
        result = await use_case.sync_all_emendas_with_ceis()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao sincronizar dados do CEIS: {str(e)}"
        )


@router.post("/{emenda_id}/fetch-news")
async def fetch_emenda_news(
    emenda_id: str,
    limit: int = Query(10, ge=1, le=50, description="Limite de notícias a buscar"),
    analyze_sentiment: bool = Query(True, description="Analisar sentimento das notícias"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Busca notícias relacionadas a uma emenda e analisa sentimentos
    
    - **emenda_id**: ID da emenda
    - **limit**: Limite de notícias (1-50)
    - **analyze_sentiment**: Se deve analisar sentimento (padrão: true)
    
    Esta funcionalidade:
    - Busca notícias relacionadas à emenda
    - Analisa sentimento de cada notícia (positivo, negativo, neutro)
    - Calcula sentimento geral
    - Atualiza emenda com notícias encontradas
    """
    use_case = FetchEmendaNewsUseCase(repository)
    
    try:
        result = await use_case.execute(
            emenda_id=emenda_id,
            limit=limit,
            analyze_sentiment=analyze_sentiment
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar notícias: {str(e)}"
        )


@router.post("/fetch-news/all")
async def fetch_all_emendas_news(
    limit_per_emenda: int = Query(5, ge=1, le=20, description="Limite de notícias por emenda"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Busca notícias para todas as emendas
    
    - **limit_per_emenda**: Limite de notícias por emenda (1-20)
    
    Esta funcionalidade processa todas as emendas em lote, buscando e analisando
    notícias relacionadas a cada uma.
    """
    use_case = FetchEmendaNewsUseCase(repository)
    
    try:
        result = await use_case.fetch_all_emendas_news(limit_per_emenda=limit_per_emenda)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar notícias: {str(e)}"
        )


@router.post("/{emenda_id}/register-blockchain")
async def register_emenda_blockchain(
    emenda_id: str,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Registra uma emenda na blockchain (rastreabilidade imutável)
    
    - **emenda_id**: ID da emenda
    
    Esta funcionalidade registra a criação da emenda na blockchain,
    garantindo rastreabilidade imutável e transparência total.
    """
    use_case = RegisterBlockchainUseCase(repository)
    
    try:
        emenda = await repository.find_by_id(emenda_id)
        if not emenda:
            raise HTTPException(status_code=404, detail="Emenda não encontrada")
        
        result = await use_case.register_emenda_creation(emenda)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao registrar na blockchain: {str(e)}"
        )


@router.post("/{emenda_id}/blockchain/execution")
async def register_execution_blockchain(
    emenda_id: str,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Registra atualização de execução na blockchain
    
    - **emenda_id**: ID da emenda
    
    Registra mudanças na execução da emenda na blockchain,
    garantindo que nenhuma alteração possa ser feita sem ser detectada.
    """
    use_case = RegisterBlockchainUseCase(repository)
    
    try:
        emenda = await repository.find_by_id(emenda_id)
        if not emenda:
            raise HTTPException(status_code=404, detail="Emenda não encontrada")
        
        result = await use_case.register_execution_update(emenda)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao registrar execução: {str(e)}"
        )


@router.get("/{emenda_id}/blockchain/audit")
async def get_blockchain_audit(
    emenda_id: str,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Obtém trilha de auditoria completa de uma emenda na blockchain
    
    - **emenda_id**: ID da emenda
    
    Retorna histórico completo de todas as transações relacionadas à emenda,
    garantindo transparência total e auditabilidade.
    """
    use_case = RegisterBlockchainUseCase(repository)
    
    try:
        result = await use_case.get_audit_trail(emenda_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter trilha de auditoria: {str(e)}"
        )


@router.get("/blockchain/verify")
async def verify_blockchain_integrity(
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Verifica integridade da cadeia de blocos
    
    Verifica se todos os blocos estão íntegros e se a cadeia não foi
    comprometida. Retorna status da verificação.
    """
    use_case = RegisterBlockchainUseCase(repository)
    
    try:
        result = await use_case.verify_integrity()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar integridade: {str(e)}"
        )


@router.post("/check-delays")
async def check_delayed_emendas(
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository),
    session: AsyncSession = Depends(get_db)
):
    """
    Verifica emendas atrasadas e envia notificações
    
    Esta funcionalidade verifica todas as emendas e identifica aquelas
    que estão atrasadas, enviando notificações para usuários cadastrados.
    """
    from src.application.use_cases.emenda_pix.monitor_status_changes import MonitorStatusChangesUseCase
    from src.infrastructure.persistence.postgres.user_preferences_repository_impl import PostgresUserPreferencesRepository
    
    try:
        preferences_repo = PostgresUserPreferencesRepository(session)
        use_case = MonitorStatusChangesUseCase(repository, preferences_repo)
        
        result = await use_case.check_and_notify_delays()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar atrasos: {str(e)}"
        )


@router.get("/{emenda_id}/compare")
async def compare_emendas(
    emenda_id: str,
    area: Optional[str] = Query(None, description="Área temática para filtrar"),
    valor_range: Optional[float] = Query(None, ge=0, le=100, description="Faixa de valor (% de variação)"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Compara emenda com outras similares
    
    - **emenda_id**: ID da emenda a comparar
    - **area**: Área temática (opcional)
    - **valor_range**: Faixa de valor em percentual (opcional)
    
    Retorna análise comparativa com emendas similares.
    """
    use_case = CompareEmendasUseCase(repository)
    
    try:
        result = await use_case.compare_similar_emendas(
            emenda_id=emenda_id,
            area=area,
            valor_range=valor_range
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao comparar emendas: {str(e)}"
        )


@router.get("/benchmark/deputado")
async def benchmark_by_deputado(
    autor: Optional[str] = Query(None, description="Nome do deputado (opcional)"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Gera benchmarking de execução por deputado
    
    - **autor**: Nome do deputado (opcional, se não informado busca todos)
    
    Retorna métricas de execução agrupadas por deputado.
    """
    use_case = CompareEmendasUseCase(repository)
    
    try:
        result = await use_case.benchmark_by_deputado(autor_nome=autor)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar benchmarking: {str(e)}"
        )


@router.get("/benchmark/municipio")
async def benchmark_by_municipio(
    municipio: Optional[str] = Query(None, description="Nome do município (opcional)"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Gera benchmarking de execução por município
    
    - **municipio**: Nome do município (opcional, se não informado busca todos)
    
    Retorna métricas de execução agrupadas por município.
    """
    use_case = CompareEmendasUseCase(repository)
    
    try:
        result = await use_case.benchmark_by_municipio(municipio=municipio)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar benchmarking: {str(e)}"
        )


@router.get("/patterns-anomalies")
async def identify_patterns_anomalies(
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Identifica padrões e anomalias nas emendas
    
    Retorna análise de padrões (baixa execução, atrasos) e anomalias
    (valores muito altos, execução muito rápida).
    """
    use_case = CompareEmendasUseCase(repository)
    
    try:
        result = await use_case.identify_patterns_and_anomalies()
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao identificar padrões: {str(e)}"
        )


@router.post("/{emenda_id}/share")
async def generate_share_link(
    emenda_id: str,
    platform: Optional[str] = Query(None, description="Plataforma: twitter, facebook, whatsapp"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Gera link de compartilhamento para emenda
    
    - **emenda_id**: ID da emenda
    - **platform**: Plataforma de compartilhamento (opcional)
    
    Retorna link de compartilhamento e metadados para redes sociais.
    """
    use_case = ShareEmendaUseCase(repository)
    
    try:
        result = await use_case.generate_share_link(emenda_id, platform)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar link: {str(e)}"
        )


@router.get("/{emenda_id}/share/preview")
async def get_share_preview(
    emenda_id: str,
    platform: str = Query("default", description="Plataforma: twitter, facebook, whatsapp, default"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Obtém preview formatado para compartilhamento em redes sociais
    
    - **emenda_id**: ID da emenda
    - **platform**: Plataforma (twitter, facebook, whatsapp, default)
    
    Retorna texto e metadados formatados para a plataforma específica.
    """
    use_case = ShareEmendaUseCase(repository)
    
    try:
        result = await use_case.get_share_preview(emenda_id, platform)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter preview: {str(e)}"
        )


@router.get("/{emenda_id}/history")
async def get_emenda_history(
    emenda_id: str,
    limit: int = Query(50, ge=1, le=200, description="Limite de registros"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Obtém histórico completo de execução da emenda
    
    - **emenda_id**: ID da emenda
    - **limit**: Limite de registros (1-200)
    
    Retorna timeline completa de mudanças de status e execução.
    """
    use_case = TrackHistoryUseCase(repository)
    
    try:
        result = await use_case.get_history(emenda_id, limit)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter histórico: {str(e)}"
        )


@router.get("/{emenda_id}/trust-score")
async def get_trust_score(
    emenda_id: str,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Calcula Trust Score (Índice de Integridade) da emenda
    
    - **emenda_id**: ID da emenda
    
    Retorna Trust Score (0-100) baseado em:
    - Execução conforme plano (30%)
    - Tempo de execução (20%)
    - Documentação completa (20%)
    - Análise de IA - risco de desvio (20%)
    - Histórico de mudanças (10%)
    
    Conceito de Triangulação de Dados:
    - Fonte Financeira (Portal da Transparência)
    - Fonte Política (Dados da Emenda)
    - Fonte Física (Documentos/Fotos - roadmap)
    """
    use_case = CalculateTrustScoreUseCase()
    get_use_case = GetEmendaPixUseCase(repository)
    
    try:
        emenda = await get_use_case.execute(emenda_id)
        if not emenda:
            raise HTTPException(status_code=404, detail="Emenda não encontrada")
        
        result = use_case.calculate(emenda)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular Trust Score: {str(e)}"
        )


@router.post("/{emenda_id}/validate-geofencing")
async def validate_geofencing(
    emenda_id: str,
    foto_data: dict,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Valida geofencing de foto/documento comprobatório
    
    - **emenda_id**: ID da emenda
    - **foto_data**: Dados da foto com coordenadas GPS
        {
            "latitude": -23.5505,
            "longitude": -46.6333,
            "url": "https://...",
            "tipo": "foto_obra" | "nota_fiscal" | "documento"
        }
    
    **Conceito de Triangulação de Dados - Fonte Física**:
    Valida se foto/documento está dentro do geofence esperado
    baseado na localização do destinatário da emenda.
    
    Returns:
        dict com resultado da validação (valid, distance_km, etc.)
    """
    validate_use_case = ValidateGeofencingUseCase()
    get_use_case = GetEmendaPixUseCase(repository)
    
    try:
        emenda = await get_use_case.execute(emenda_id)
        if not emenda:
            raise HTTPException(status_code=404, detail="Emenda não encontrada")
        
        result = validate_use_case.validate(emenda, foto_data)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "Erro na validação"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao validar geofencing: {str(e)}"
        )


@router.post("/{emenda_id}/validate-geofencing/batch")
async def validate_geofencing_batch(
    emenda_id: str,
    fotos: List[dict],
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Valida geofencing de múltiplas fotos/documentos
    
    - **emenda_id**: ID da emenda
    - **fotos**: Lista de fotos com coordenadas GPS
    
    Returns:
        dict com resultados de todas as validações
    """
    validate_use_case = ValidateGeofencingUseCase()
    get_use_case = GetEmendaPixUseCase(repository)
    
    try:
        emenda = await get_use_case.execute(emenda_id)
        if not emenda:
            raise HTTPException(status_code=404, detail="Emenda não encontrada")
        
        result = validate_use_case.validate_multiple(emenda, fotos)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao validar geofencing: {str(e)}"
        )



@router.post("/{emenda_id}/upload-photo")
async def upload_photo(
    emenda_id: str,
    photo_file: Optional[UploadFile] = File(None, description="Arquivo da foto (opcional)"),
    photo_url: Optional[str] = Query(None, description="URL da foto após upload (se não enviar arquivo)"),
    photo_path: Optional[str] = Query(None, description="Caminho local da foto (para EXIF)"),
    tipo: str = Query("foto_obra", description="Tipo da foto (foto_obra, nota_fiscal, documento)"),
    latitude: Optional[float] = Query(None, description="Latitude GPS (se já conhecida)"),
    longitude: Optional[float] = Query(None, description="Longitude GPS (se já conhecida)"),
    validate_location: bool = Query(True, description="Validar geofencing"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Faz upload de foto com validação de geofencing
    
    - **emenda_id**: ID da emenda
    - **photo_file**: Arquivo da foto (opcional, pode enviar arquivo ou URL)
    - **photo_url**: URL da foto (se não enviar arquivo)
    - **photo_path**: Caminho local da foto (opcional, para extrair EXIF)
    - **tipo**: Tipo da foto (foto_obra, nota_fiscal, documento)
    - **latitude**: Latitude GPS (se já conhecida)
    - **longitude**: Longitude GPS (se já conhecida)
    - **validate_location**: Se deve validar geofencing
    
    **Geofencing com EXIF**:
    - Extrai coordenadas GPS do EXIF da foto
    - Valida se foto foi tirada no município correto
    - Retorna resultado da validação
    
    Returns:
        dict com resultado do upload e validação
    """
    from src.infrastructure.storage.file_storage import FileStorage
    
    upload_use_case = UploadPhotoUseCase(repository)
    storage = FileStorage()
    
    # Se arquivo foi enviado, fazer upload primeiro
    final_photo_url = photo_url
    final_photo_path = photo_path
    
    if photo_file:
        file_content = await photo_file.read()
        upload_result = await storage.upload_file(
            file_content=file_content,
            filename=photo_file.filename or "photo.jpg",
            content_type=photo_file.content_type
        )
        
        if not upload_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=upload_result.get("message", "Erro ao fazer upload do arquivo")
            )
        
        final_photo_url = upload_result["url"]
        final_photo_path = upload_result["path"]
    
    if not final_photo_url:
        raise HTTPException(
            status_code=400,
            detail="É necessário fornecer photo_file ou photo_url"
        )
    
    photo_data = None
    if latitude and longitude:
        photo_data = {
            "tipo": tipo,
            "latitude": latitude,
            "longitude": longitude
        }
    elif tipo:
        photo_data = {"tipo": tipo}
    
    result = await upload_use_case.execute(
        emenda_id=emenda_id,
        photo_url=final_photo_url,
        photo_path=final_photo_path,
        photo_data=photo_data,
        validate_location=validate_location
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Erro ao fazer upload da foto")
        )
    
    return result


@router.get("/{emenda_id}/photos/exif/{foto_id}")
async def get_photo_exif(
    emenda_id: str,
    foto_id: str,
    photo_path: str = Query(..., description="Caminho da foto para extrair EXIF"),
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Extrai metadados EXIF de uma foto
    
    - **emenda_id**: ID da emenda
    - **foto_id**: ID da foto
    - **photo_path**: Caminho da foto
    
    Returns:
        dict com metadados EXIF (GPS, câmera, data, etc.)
    """
    from src.infrastructure.validation.geofencing import GeofencingValidator
    
    validator = GeofencingValidator()
    result = validator.extract_exif_metadata(photo_path)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Erro ao extrair metadados EXIF")
        )
    
    return result


@router.post("/{emenda_id}/analyze-invoice")
async def analyze_invoice(
    emenda_id: str,
    xml_content: Optional[str] = None,
    xml_url: Optional[str] = None,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Analisa nota fiscal (XML) e compara com objetivo da emenda
    
    - **emenda_id**: ID da emenda
    - **xml_content**: Conteúdo XML da nota fiscal (opcional)
    - **xml_url**: URL do XML da nota fiscal (opcional)
    
    **NLP para Notas Fiscais**:
    - Extrai itens da nota fiscal
    - Compara semanticamente com objetivo da emenda
    - Detecta inconsistências
    
    Returns:
        dict com análise da nota fiscal
    """
    from src.infrastructure.ai.invoice_analyzer import InvoiceAnalyzer
    from src.application.use_cases.emenda_pix import GetEmendaPixUseCase
    
    get_use_case = GetEmendaPixUseCase(repository)
    analyzer = InvoiceAnalyzer()
    
    try:
        emenda = await get_use_case.execute(emenda_id)
        if not emenda:
            raise HTTPException(status_code=404, detail="Emenda não encontrada")
        
        if not emenda.objetivo:
            raise HTTPException(
                status_code=400,
                detail="Emenda não possui objetivo definido para comparação"
            )
        
        # Obter XML
        xml_final = xml_content
        if not xml_final and xml_url:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(xml_url)
                    if response.status_code == 200:
                        xml_final = response.text
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erro ao buscar XML da URL: {str(e)}"
                )
        
        if not xml_final:
            raise HTTPException(
                status_code=400,
                detail="É necessário fornecer xml_content ou xml_url"
            )
        
        # Analisar
        result = analyzer.analyze_invoice_xml(xml_final, emenda.objetivo)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Erro ao analisar nota fiscal")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao analisar nota fiscal: {str(e)}"
        )


@router.post("/{emenda_id}/sync-plano-acao")
async def sync_plano_acao(
    emenda_id: str,
    repository: PostgresEmendaPixRepository = Depends(get_emenda_pix_repository)
):
    """
    Sincroniza Plano de Ação do Transferegov.br
    
    - **emenda_id**: ID da emenda
    
    Busca o plano de ação correspondente no Transferegov.br usando
    o código da emenda formatado.
    
    **Integração Vigia Pix**:
    - Conecta dados financeiros (Portal) com execução (Transferegov)
    - Permite análise de anomalias cruzadas
    """
    from src.application.use_cases.emenda_pix import GetEmendaPixUseCase
    from src.infrastructure.external.transferegov_client import TransferegovClient
    
    get_use_case = GetEmendaPixUseCase(repository)
    transferegov_client = TransferegovClient()
    
    try:
        emenda = await get_use_case.execute(emenda_id)
        if not emenda:
            raise HTTPException(status_code=404, detail="Emenda não encontrada")
        
        if not emenda.numero_emenda:
            raise HTTPException(
                status_code=400,
                detail="Emenda não possui número para buscar plano de ação"
            )
        
        # Formatar código da emenda
        codigo_emenda = f"{emenda.ano}-{emenda.numero_emenda}"
        
        # Buscar plano de ação
        plano_acao = await transferegov_client.get_plano_acao(codigo_emenda)
        
        if not plano_acao:
            return {
                "success": False,
                "message": "Plano de ação não encontrado no Transferegov.br",
                "codigo_emenda": codigo_emenda
            }
        
        # Atualizar emenda com dados do plano (se necessário)
        # Por enquanto, apenas retornar os dados
        
        return {
            "success": True,
            "plano_acao": plano_acao,
            "codigo_emenda": codigo_emenda,
            "is_mock": plano_acao.get("is_mock", False),
            "message": "Plano de ação sincronizado com sucesso" + (" (dados fictícios para demonstração)" if plano_acao.get("is_mock") else "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao sincronizar plano de ação: {str(e)}"
        )
