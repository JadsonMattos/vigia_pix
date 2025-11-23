#!/bin/bash

# Script de Teste do Dashboard Principal de Legislações
# Valida todas as funcionalidades mencionadas no guia

echo "🧪 =========================================="
echo "   TESTE DO DASHBOARD PRINCIPAL"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs
API_URL="http://localhost:8000/api/v1/legislation"
FRONTEND_URL="http://localhost:3000/dashboard"

# Contador
PASSED=0
FAILED=0

# Função para testar endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_field=$3
    
    echo -n "Testando: $name... "
    
    response=$(curl -s "$url" 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$response" | grep -q "$expected_field"; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
        return 1
    fi
}

# Função para verificar se serviço está rodando
check_service() {
    local service=$1
    local url=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service está rodando${NC}"
        return 0
    else
        echo -e "${RED}❌ $service NÃO está rodando${NC}"
        return 1
    fi
}

echo "📋 FASE 1: Verificação de Serviços"
echo "=========================================="
echo ""

check_service "Backend API" "$API_URL/"
check_service "Frontend" "$FRONTEND_URL"

echo ""
echo "📋 FASE 2: Teste de API Endpoints"
echo "=========================================="
echo ""

# Teste 1: Listar legislações
test_endpoint "GET /api/v1/legislation/" "$API_URL/" "items"

# Teste 2: Verificar total de legislações
echo -n "Testando: Total de legislações... "
total=$(curl -s "$API_URL/" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null)
if [ "$total" -gt 0 ]; then
    echo -e "${GREEN}✅ PASSOU (Total: $total)${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Nenhuma legislação encontrada${NC}"
    ((FAILED++))
fi

# Teste 3: Paginação
test_endpoint "Paginação (limit=2)" "$API_URL/?limit=2" "items"

# Teste 4: Buscar legislação por ID
echo -n "Testando: Buscar legislação por ID... "
first_id=$(curl -s "$API_URL/?limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)
if [ -n "$first_id" ]; then
    if curl -s "$API_URL/$first_id" | grep -q "title\|id"; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠️  Não foi possível obter ID${NC}"
    ((FAILED++))
fi

echo ""
echo "📋 FASE 3: Teste de Sincronização"
echo "=========================================="
echo ""

# Teste de sincronização
echo -n "Testando: POST /legislation/sync... "
SYNC_RESPONSE=$(curl -s -X POST "$API_URL/sync?days=7" 2>/dev/null)
if echo "$SYNC_RESPONSE" | grep -q "count\|message"; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
    
    # Verificar resposta
    COUNT=$(echo "$SYNC_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('count', 0))" 2>/dev/null)
    echo "   Sincronizadas: $COUNT legislação(ões)"
else
    echo -e "${RED}❌ FALHOU${NC}"
    echo "   Resposta: ${SYNC_RESPONSE:0:200}..."
    ((FAILED++))
fi

echo ""
echo "📋 FASE 4: Validação de Dados"
echo "=========================================="
echo ""

# Verificar se há legislações em tramitação
echo -n "Verificando: Legislações em tramitação... "
TRAMITACAO=$(curl -s "$API_URL/" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(sum(1 for l in items if 'tramitacao' in l.get('status', '').lower()))" 2>/dev/null)
if [ "$TRAMITACAO" -gt 0 ]; then
    echo -e "${GREEN}✅ PASSOU ($TRAMITACAO em tramitação)${NC}"
    ((PASSED++))
else
    echo -e "${BLUE}ℹ️  Nenhuma em tramitação (pode ser normal)${NC}"
fi

# Verificar estrutura das legislações
echo -n "Verificando: Estrutura das legislações... "
HAS_TITLE=$(curl -s "$API_URL/?limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print('OK' if items and items[0].get('title') else 'VAZIO')" 2>/dev/null)
if [ "$HAS_TITLE" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FALHOU${NC}"
    ((FAILED++))
fi

echo ""
echo "📋 FASE 5: Validação de Funcionalidades do Frontend"
echo "=========================================="
echo ""
echo "⚠️  Testes manuais necessários no navegador:"
echo ""
echo "1. Acesse: ${BLUE}$FRONTEND_URL${NC}"
echo ""
echo "2. Verifique Estatísticas (4 cards):"
echo "   [ ] Total de Legislações > 0"
echo "   [ ] Em Tramitação (pode ser 0)"
echo "   [ ] Manifestações (inicia em 0)"
echo "   [ ] Taxa de Engajamento calculada"
echo ""
echo "3. Teste Botão '🔄 Sincronizar Legislações':"
echo "   [ ] Botão está visível no topo"
echo "   [ ] Ao clicar, muda para '⏳ Sincronizando...'"
echo "   [ ] Botão fica desabilitado durante sincronização"
echo "   [ ] Após sincronização, alert aparece com contagem"
echo "   [ ] Filtros são limpos após sincronização"
echo "   [ ] Dados são recarregados"
echo ""
echo "4. Teste Filtros:"
echo "   [ ] Busca: Digite texto → deve filtrar"
echo "   [ ] Status: Selecione 'Em Tramitação' → deve filtrar"
echo "   [ ] Data: Selecione 'Últimos 30 dias' → deve filtrar"
echo "   [ ] Limpar: Clique em '🔄 Limpar Filtros' → deve resetar"
echo ""
echo "5. Verifique Lista de Legislações:"
echo "   [ ] Lista é exibida"
echo "   [ ] Cards mostram título, autor, data"
echo "   [ ] Botão 'Ver Detalhes' funciona"
echo "   [ ] Botão '📢 Enviar Mensagem' funciona"
echo ""
echo "6. Teste Paginação:"
echo "   [ ] Botões 'Anterior' e 'Próxima' funcionam"
echo "   [ ] Número da página exibido"
echo ""

echo ""
echo "📊 RESUMO DOS TESTES AUTOMATIZADOS"
echo "=========================================="
echo -e "${GREEN}✅ Passou: $PASSED${NC}"
echo -e "${RED}❌ Falhou: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 Todos os testes automatizados passaram!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Alguns testes falharam. Verifique acima.${NC}"
    exit 1
fi

