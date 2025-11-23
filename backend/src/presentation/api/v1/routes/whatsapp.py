"""WhatsApp webhook routes"""
from fastapi import APIRouter, Request, HTTPException, Form, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.infrastructure.persistence.postgres.database import get_db
from src.infrastructure.persistence.postgres.legislation_repository_impl import PostgresLegislationRepository
from src.application.use_cases.legislation import GetLegislationUseCase, SimplifyLegislationUseCase
from src.domain.value_objects.complexity_level import ComplexityLevel

logger = structlog.get_logger()
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


class WhatsAppMessage(BaseModel):
    """WhatsApp message model"""
    From: str
    Body: str
    MessageSid: str = ""


class WhatsAppResponse(BaseModel):
    """WhatsApp response model"""
    message: str


class SimulateMessageRequest(BaseModel):
    """Request model for simulating WhatsApp message"""
    From: str
    Body: str


def extract_pl_number(text: str) -> Optional[str]:
    """Extract PL number from text"""
    import re
    # Patterns: "PL 1234", "PL1234", "1234/2024", etc.
    patterns = [
        r'PL\s*(\d+)',
        r'(\d+)/\d{4}',
        r'projeto\s+(\d+)',
        r'(\d{4,6})',  # Just numbers (4-6 digits)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


async def process_whatsapp_message(
    from_number: str, 
    message_body: str,
    session: AsyncSession
) -> str:
    """
    Process WhatsApp message and return response
    
    Args:
        from_number: Sender's phone number
        message_body: Message content
        session: Database session
        
    Returns:
        Response message
    """
    message_body = message_body.strip()
    
    logger.info("whatsapp_message_received", from_number=from_number, body=message_body)
    
    # Check if it's a help command
    help_commands = ["ajuda", "help", "oi", "olá", "ola", "start", "inicio"]
    if message_body.lower() in help_commands:
        response = """🤖 *Voz Cidadã*

Envie o número de um Projeto de Lei para receber uma explicação simplificada.

Exemplos:
• PL 1234
• PL 1234/2024
• 1234

Ou digite "ajuda" para ver esta mensagem novamente."""
        return response
    
    # Extract PL number
    pl_number = extract_pl_number(message_body)
    
    if not pl_number:
        response = """❌ Não consegui identificar o número do PL.

Por favor, envie no formato:
• PL 1234
• PL 1234/2024
• 1234

Digite "ajuda" para mais informações."""
        return response
    
    # Get repository
    repository = PostgresLegislationRepository(session)
    
    # Try to find by external_id (PL number)
    legislation = await repository.find_by_external_id(pl_number)
    
    if not legislation:
        response = f"""❌ PL {pl_number} não encontrado no nosso banco de dados.

Tente sincronizar as legislações primeiro ou verifique o número.

Para sincronizar, acesse:
http://localhost:8000/api/v1/legislation/sync?days=30"""
        return response
    
    # Simplify text
    simplify_use_case = SimplifyLegislationUseCase(repository)
    simplified = await simplify_use_case.execute(
        legislation_id=legislation.id,
        level=ComplexityLevel.INTERMEDIATE
    )
    
    # Format response (limit to 1500 chars for WhatsApp)
    max_length = 1200
    simplified_text = simplified[:max_length]
    if len(simplified) > max_length:
        simplified_text += "..."
    
    # Format response
    response = f"""📋 *{legislation.title}*

{simplified_text}

🔗 Ver mais: http://localhost:3000/legislation/{legislation.id}"""
    
    return response


@router.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(""),
    session: AsyncSession = Depends(get_db)
):
    """
    WhatsApp webhook endpoint (Twilio format)
    
    Receives messages from WhatsApp and responds with simplified legislation
    
    Format: Form Data with fields:
    - From: Sender's phone number
    - Body: Message content
    - MessageSid: Message ID (optional)
    """
    try:
        response = await process_whatsapp_message(From, Body, session)
        return {"message": response}
    except Exception as e:
        logger.error("whatsapp_webhook_error", error=str(e), from_number=From)
        return {
            "message": "❌ Ocorreu um erro ao processar sua mensagem. Tente novamente mais tarde."
        }


@router.post("/simulate")
async def simulate_whatsapp_message(
    request: SimulateMessageRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Simulate WhatsApp message for testing
    
    Useful for development and demo when Twilio is not configured
    
    Example:
    ```json
    {
        "From": "whatsapp:+5511999999999",
        "Body": "PL 1234"
    }
    ```
    """
    try:
        response = await process_whatsapp_message(request.From, request.Body, session)
        return {
            "status": "success",
            "response": response,
            "from": request.From,
            "body": request.Body
        }
    except Exception as e:
        logger.error("simulate_whatsapp_error", error=str(e), from_number=request.From)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_whatsapp():
    """Test endpoint for WhatsApp integration"""
    return {
        "status": "ok",
        "message": "WhatsApp webhook is ready",
        "endpoints": {
            "webhook": "/api/v1/whatsapp/webhook",
            "simulate": "/api/v1/whatsapp/simulate",
            "test": "/api/v1/whatsapp/test"
        },
        "usage": {
            "webhook": "POST with Form data (From, Body, MessageSid)",
            "simulate": "POST with JSON {From: string, Body: string}"
        },
        "example_simulate": {
            "From": "whatsapp:+5511999999999",
            "Body": "PL 1234"
        }
    }
