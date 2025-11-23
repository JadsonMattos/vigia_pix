#!/bin/bash
# Script de demonstração do Voz Cidadã
# Uso: ./scripts/demo.sh

set -e

API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

echo "🎬 DEMO: Voz Cidadã - Participação Legislativa Acessível"
echo "=================================================="
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Verificando saúde dos serviços...${NC}"
echo ""

# Health check
if curl -s "${API_URL}/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend está rodando${NC}"
else
    echo -e "${YELLOW}⚠️  Backend não está respondendo. Certifique-se de que está rodando.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}2. Testando WhatsApp Bot...${NC}"
echo ""

# Test WhatsApp
WHATSAPP_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/whatsapp/simulate" \
    -H "Content-Type: application/json" \
    -d '{"From": "whatsapp:+5511999999999", "Body": "PL 1234"}')

if echo "$WHATSAPP_RESPONSE" | grep -q "response"; then
    echo -e "${GREEN}✅ WhatsApp Bot está funcionando${NC}"
    echo "Resposta: $(echo $WHATSAPP_RESPONSE | jq -r '.response' | head -c 100)..."
else
    echo -e "${YELLOW}⚠️  WhatsApp Bot pode ter problemas${NC}"
fi

echo ""
echo -e "${BLUE}3. Testando API de Legislações...${NC}"
echo ""

# List legislations
LEGISLATIONS=$(curl -s "${API_URL}/api/v1/legislation?limit=5")
TOTAL=$(echo "$LEGISLATIONS" | jq -r '.total // 0')

if [ "$TOTAL" -gt 0 ]; then
    echo -e "${GREEN}✅ Encontradas $TOTAL legislações${NC}"
else
    echo -e "${YELLOW}⚠️  Nenhuma legislação encontrada. Execute a sincronização.${NC}"
    echo ""
    echo "Sincronizando legislações..."
    curl -s -X POST "${API_URL}/api/v1/legislation/sync?days=30" > /dev/null
    echo -e "${GREEN}✅ Sincronização iniciada${NC}"
fi

echo ""
echo -e "${BLUE}4. Testando Simplificação de Texto...${NC}"
echo ""

# Get first legislation
FIRST_ID=$(echo "$LEGISLATIONS" | jq -r '.items[0].id // empty')

if [ -n "$FIRST_ID" ]; then
    SIMPLIFY_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/legislation/${FIRST_ID}/simplify?level=basic")
    
    if echo "$SIMPLIFY_RESPONSE" | grep -q "simplified_text"; then
        echo -e "${GREEN}✅ Simplificação funcionando${NC}"
        ORIGINAL_LEN=$(echo "$SIMPLIFY_RESPONSE" | jq -r '.original_length // 0')
        SIMPLIFIED_LEN=$(echo "$SIMPLIFY_RESPONSE" | jq -r '.simplified_length // 0')
        REDUCTION=$(echo "$SIMPLIFY_RESPONSE" | jq -r '.reduction_percentage // 0')
        echo "   Original: ${ORIGINAL_LEN} caracteres"
        echo "   Simplificado: ${SIMPLIFIED_LEN} caracteres"
        echo "   Redução: ${REDUCTION}%"
    else
        echo -e "${YELLOW}⚠️  Simplificação pode ter problemas${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Nenhuma legislação para testar simplificação${NC}"
fi

echo ""
echo -e "${BLUE}5. URLs para Demo:${NC}"
echo ""
echo -e "${GREEN}Frontend:${NC}"
echo "  - Dashboard: ${FRONTEND_URL}/dashboard"
echo "  - Legislações: ${FRONTEND_URL}/legislation"
echo "  - WhatsApp Simulator: ${FRONTEND_URL}/whatsapp-simulator"
echo ""
echo -e "${GREEN}API:${NC}"
echo "  - Health: ${API_URL}/health"
echo "  - Docs: ${API_URL}/docs"
echo "  - WhatsApp Test: ${API_URL}/api/v1/whatsapp/test"
echo ""

echo -e "${BLUE}6. Script de Apresentação:${NC}"
echo ""
echo "1. Abra o WhatsApp Simulator: ${FRONTEND_URL}/whatsapp-simulator"
echo "2. Digite: 'PL 1234' ou qualquer número de PL"
echo "3. Veja a resposta simplificada"
echo "4. Acesse o Dashboard: ${FRONTEND_URL}/dashboard"
echo "5. Veja as estatísticas e legislações"
echo "6. Clique em uma legislação para ver detalhes"
echo "7. Teste a simplificação com diferentes níveis"
echo ""

echo -e "${GREEN}✅ Demo pronto!${NC}"
echo ""



