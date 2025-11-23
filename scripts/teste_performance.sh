#!/bin/bash

# Script de Teste - Performance
# Mede tempos de resposta das APIs

echo "🧪 =========================================="
echo "   TESTE DE PERFORMANCE"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs
API_EMENDA="http://localhost:8000/api/v1/emenda-pix"
API_LEGISLATION="http://localhost:8000/api/v1/legislation"

echo "📋 Teste de Tempo de Resposta das APIs"
echo "=========================================="
echo ""

# Função para medir tempo
measure_time() {
    local url=$1
    local name=$2
    
    echo -n "Testando: $name... "
    
    start_time=$(date +%s%N)
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    end_time=$(date +%s%N)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        duration_ms=$(( (end_time - start_time) / 1000000 ))
        duration_s=$(echo "scale=2; $duration_ms / 1000" | bc)
        
        if (( duration_ms < 1000 )); then
            echo -e "${GREEN}✅ ${duration_ms}ms${NC}"
        elif (( duration_ms < 3000 )); then
            echo -e "${YELLOW}⚠️  ${duration_s}s${NC}"
        else
            echo -e "${RED}❌ ${duration_s}s (lento)${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Erro HTTP $http_code${NC}"
        return 1
    fi
}

# Teste 1: Listar emendas
measure_time "$API_EMENDA/?limit=10" "GET /emenda-pix (10 itens)"

# Teste 2: Listar legislações
measure_time "$API_LEGISLATION/?limit=10" "GET /legislation (10 itens)"

# Teste 3: Obter emenda específica
EMENDA_ID=$(curl -s "$API_EMENDA/?limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)
if [ -n "$EMENDA_ID" ]; then
    measure_time "$API_EMENDA/$EMENDA_ID" "GET /emenda-pix/{id}"
fi

# Teste 4: Análise com IA
if [ -n "$EMENDA_ID" ]; then
    echo -n "Testando: POST /emenda-pix/{id}/analyze... "
    start_time=$(date +%s%N)
    response=$(curl -s -X POST -w "\n%{http_code}" "$API_EMENDA/$EMENDA_ID/analyze" 2>/dev/null)
    end_time=$(date +%s%N)
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        duration_ms=$(( (end_time - start_time) / 1000000 ))
        duration_s=$(echo "scale=2; $duration_ms / 1000" | bc)
        
        if (( duration_ms < 5000 )); then
            echo -e "${GREEN}✅ ${duration_s}s${NC}"
        elif (( duration_ms < 10000 )); then
            echo -e "${YELLOW}⚠️  ${duration_s}s${NC}"
        else
            echo -e "${RED}❌ ${duration_s}s (muito lento)${NC}"
        fi
    else
        echo -e "${RED}❌ Erro HTTP $http_code${NC}"
    fi
fi

echo ""
echo "📋 Recomendações"
echo "=========================================="
echo ""
echo "✅ Tempos aceitáveis:"
echo "  - Listagem: < 1s"
echo "  - Detalhes: < 1s"
echo "  - Análise IA: < 10s"
echo ""
echo "⚠️  Se algum teste estiver lento:"
echo "  - Verifique conexão com banco de dados"
echo "  - Verifique se há índices nas tabelas"
echo "  - Verifique se cache está funcionando"
echo "  - Verifique logs do backend para erros"

