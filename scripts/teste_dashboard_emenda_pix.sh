#!/bin/bash

# Script de Teste do Dashboard de Emenda Pix
# Valida todas as funcionalidades mencionadas no guia

echo "🧪 =========================================="
echo "   TESTE DO DASHBOARD EMENDA PIX"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs
API_URL="http://localhost:8000/api/v1/emenda-pix"
FRONTEND_URL="http://localhost:3000/emenda-pix"

# Contador de testes
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

# Teste 1: Listar emendas
test_endpoint "GET /api/v1/emenda-pix/" "$API_URL/" "items"

# Teste 2: Verificar total de emendas
echo -n "Testando: Total de emendas (deve ser 5)... "
total=$(curl -s "$API_URL/" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null)
if [ "$total" = "5" ]; then
    echo -e "${GREEN}✅ PASSOU (Total: $total)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FALHOU (Total: $total, esperado: 5)${NC}"
    ((FAILED++))
fi

# Teste 3: Filtro por status
test_endpoint "Filtro por status=atrasada" "$API_URL/?status_execucao=atrasada" "items"

# Teste 4: Filtro por área
test_endpoint "Filtro por area=saude" "$API_URL/?area=saude" "items"

# Teste 5: Filtro por UF
test_endpoint "Filtro por destinatario_uf=MT" "$API_URL/?destinatario_uf=MT" "items"

# Teste 6: Paginação
test_endpoint "Paginação (limit=2)" "$API_URL/?limit=2" "items"

# Teste 7: Buscar emenda por ID
echo -n "Testando: Buscar emenda por ID... "
first_id=$(curl -s "$API_URL/?limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)
if [ -n "$first_id" ]; then
    if curl -s "$API_URL/$first_id" | grep -q "numero_emenda"; then
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
echo "📋 FASE 3: Validação de Dados"
echo "=========================================="
echo ""

# Verificar se há emendas com diferentes status
echo -n "Verificando: Emendas com status 'atrasada'... "
atrasadas=$(curl -s "$API_URL/?status_execucao=atrasada" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('items', [])))" 2>/dev/null)
if [ "$atrasadas" -gt 0 ]; then
    echo -e "${GREEN}✅ PASSOU ($atrasadas emendas atrasadas)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FALHOU (Nenhuma emenda atrasada encontrada)${NC}"
    ((FAILED++))
fi

# Verificar se há emendas para Cuiabá
echo -n "Verificando: Emendas para Cuiabá... "
cuiaba=$(curl -s "$API_URL/" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(sum(1 for e in items if 'Cuiabá' in e.get('destinatario_nome', '')))" 2>/dev/null)
if [ "$cuiaba" -gt 0 ]; then
    echo -e "${GREEN}✅ PASSOU ($cuiaba emenda(s) para Cuiabá)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FALHOU (Nenhuma emenda para Cuiabá)${NC}"
    ((FAILED++))
fi

# Verificar se há emendas com alertas
echo -n "Verificando: Emendas com alertas... "
com_alertas=$(curl -s "$API_URL/" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(sum(1 for e in items if e.get('alertas') and len(e.get('alertas', [])) > 0))" 2>/dev/null)
echo -e "${BLUE}ℹ️  $com_alertas emenda(s) com alertas${NC}"

echo ""
echo "📋 FASE 4: Validação de Funcionalidades do Frontend"
echo "=========================================="
echo ""
echo "⚠️  Testes manuais necessários no navegador:"
echo ""
echo "1. Acesse: ${BLUE}$FRONTEND_URL${NC}"
echo ""
echo "2. Verifique Estatísticas:"
echo "   [ ] Total de Emendas = 5"
echo "   [ ] Valor Total > 0"
echo "   [ ] Emendas Atrasadas > 0"
echo "   [ ] Taxa Execução Média calculada"
echo ""
echo "3. Teste Filtros:"
echo "   [ ] Busca: Digite 'Cuiabá' → deve filtrar"
echo "   [ ] Status: Selecione 'Atrasada' → deve mostrar apenas atrasadas"
echo "   [ ] Área: Selecione 'Saúde' → deve filtrar"
echo "   [ ] UF: Selecione 'MT' → deve filtrar"
echo "   [ ] Limpar: Clique em '🔄 Limpar' → deve resetar"
echo ""
echo "4. Verifique Cards de Emendas:"
echo "   [ ] Número da emenda visível"
echo "   [ ] Autor e destinatário visíveis"
echo "   [ ] Valor formatado (R$)"
echo "   [ ] Barra de progresso funcionando"
echo "   [ ] Status com cor correta"
echo "   [ ] Indicador de alertas (se houver)"
echo ""
echo "5. Teste Paginação:"
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

