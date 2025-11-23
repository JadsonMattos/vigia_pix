"""Main application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from contextlib import asynccontextmanager

from src.presentation.api.v1.routes import legislation, alerts, participation, whatsapp, data_sources, emenda_pix, notifications, reports
from src.infrastructure.logging.structured_logger import setup_logging
from src.infrastructure.persistence.postgres.database import init_db, close_db

# Setup logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("Starting application")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Voz Cidadã API",
    description="""
    API pública para transparência e controle social de Emendas Pix.
    
    ## Funcionalidades
    
    * **Emendas Pix**: Listagem, detalhes, análise e comparação
    * **Análise com IA**: Identificação de riscos e alertas
    * **Benchmarking**: Comparação por deputado e município
    * **Relatórios**: Exportação CSV/JSON e relatórios personalizados
    * **Compartilhamento**: Links e previews para redes sociais
    * **Histórico**: Timeline completa de execução
    
    ## Uso Público
    
    Esta API é pública e pode ser usada por qualquer projeto de transparência.
    Para uso em produção, entre em contato para obter API key e rate limits.
    
    ## Documentação
    
    * Swagger UI: `/api/docs`
    * ReDoc: `/api/redoc`
    """,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
    contact={
        "name": "Voz Cidadã",
        "url": "https://vozcidada.org",
        "email": "contato@vozcidada.org"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS middleware
import os

# Em desenvolvimento, permite apenas localhost
# Em produção, permite todas as origens (ajuste conforme necessário)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    # Em produção, permite todas as origens
    ALLOWED_ORIGINS = ["*"]
    ALLOW_CREDENTIALS = False  # Não pode usar credentials com "*"
else:
    # Em desenvolvimento, permite localhost
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:3001"]
    ALLOW_CREDENTIALS = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(legislation.router, prefix="/api/v1", tags=["legislation"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
app.include_router(participation.router, prefix="/api/v1", tags=["participation"])
app.include_router(whatsapp.router, prefix="/api/v1", tags=["whatsapp"])
app.include_router(data_sources.router, prefix="/api/v1", tags=["data-sources"])
app.include_router(emenda_pix.router, prefix="/api/v1", tags=["emenda-pix"])
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Voz Cidadã API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


