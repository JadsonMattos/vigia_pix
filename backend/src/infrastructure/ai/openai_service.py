"""OpenAI service implementation"""
from typing import Optional
import os
import structlog
from src.domain.value_objects.complexity_level import ComplexityLevel

logger = structlog.get_logger()

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")


class OpenAIService:
    """OpenAI service for text simplification"""
    
    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    def _get_prompt(self, text: str, level: ComplexityLevel) -> str:
        """Generate prompt for simplification"""
        level_instructions = {
            ComplexityLevel.BASIC: """
Você é um especialista em simplificação de textos legislativos brasileiros para pessoas com baixa escolaridade.

REGRAS OBRIGATÓRIAS:
1. Frases MUITO curtas: máximo 8-10 palavras por frase
2. Palavras simples: máximo 5-6 letras, evite palavras difíceis
3. Use exemplos práticos do dia a dia do brasileiro
4. NUNCA use termos jurídicos sem explicar de forma simples
5. Use linguagem coloquial, como se estivesse explicando para um amigo
6. Quebre textos longos em parágrafos curtos
7. Use números e listas quando possível
8. Evite: "portanto", "contudo", "entretanto" - use "mas", "porém"
9. Substitua termos técnicos:
   - "legislação" → "lei"
   - "promulgar" → "aprovar"
   - "vigência" → "quando começa a valer"
   - "revogar" → "cancelar"

EXEMPLO DE TOM:
❌ Ruim: "A presente lei estabelece diretrizes para a promoção da igualdade"
✅ Bom: "Esta lei quer que todos sejam tratados igual. Sem diferença."

IMPORTANTE: Responda APENAS com o texto simplificado, sem explicações adicionais.
            """,
            ComplexityLevel.INTERMEDIATE: """
Você é um especialista em simplificação de textos legislativos brasileiros para pessoas com ensino médio.

REGRAS:
1. Frases médias: máximo 15-20 palavras por frase
2. Palavras comuns: máximo 8-10 letras, evite jargões desnecessários
3. Use exemplos práticos e contextuais
4. Explique termos técnicos quando aparecerem pela primeira vez
5. Mantenha tom profissional mas acessível
6. Estrutura clara com parágrafos bem definidos
7. Use conectivos simples: "porque", "mas", "então"
8. Mantenha a estrutura lógica do texto original

EXEMPLO DE TOM:
❌ Ruim: "A legislação promulgada estabelece diretrizes..."
✅ Bom: "A lei aprovada define regras sobre..."

IMPORTANTE: Responda APENAS com o texto simplificado, sem explicações adicionais.
            """,
            ComplexityLevel.ADVANCED: """
Você é um especialista em simplificação de textos legislativos brasileiros mantendo precisão técnica.

REGRAS:
1. Frases claras e diretas: evite períodos muito longos
2. Mantenha termos técnicos quando necessário, mas explique brevemente
3. Estrutura lógica e bem organizada
4. Linguagem profissional e precisa
5. Mantenha a essência jurídica do texto
6. Use conectivos apropriados
7. Organize em seções claras quando o texto for longo

OBJETIVO: Tornar o texto mais legível sem perder precisão técnica.

IMPORTANTE: Responda APENAS com o texto simplificado, sem explicações adicionais.
            """
        }
        
        return f"""{level_instructions[level]}

TEXTO ORIGINAL PARA SIMPLIFICAR:
{text}

TEXTO SIMPLIFICADO:"""
    
    async def simplify(self, text: str, level: ComplexityLevel) -> str:
        """
        Simplify text using OpenAI
        
        Args:
            text: Text to simplify
            level: Complexity level
            
        Returns:
            Simplified text
        """
        try:
            prompt = self._get_prompt(text, level)
            
            logger.info(
                "openai_simplification_start",
                text_length=len(text),
                level=level.value,
                model=self.model
            )
            
            # Adjust max_tokens based on level
            max_tokens_map = {
                ComplexityLevel.BASIC: 1500,      # Shorter for basic
                ComplexityLevel.INTERMEDIATE: 2000,  # Medium
                ComplexityLevel.ADVANCED: 2500     # Longer for advanced
            }
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em simplificação de textos legislativos brasileiros. Sempre responda APENAS com o texto simplificado, sem explicações adicionais, sem prefixos, sem comentários. Apenas o texto simplificado."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=max_tokens_map.get(level, 2000)
            )
            
            simplified = response.choices[0].message.content.strip()
            
            logger.info(
                "openai_simplification_complete",
                original_length=len(text),
                simplified_length=len(simplified),
                level=level.value,
                tokens_used=response.usage.total_tokens
            )
            
            return simplified
            
        except Exception as e:
            logger.error(
                "openai_simplification_error",
                error=str(e),
                level=level.value
            )
            raise


