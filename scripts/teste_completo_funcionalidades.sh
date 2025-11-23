#!/bin/bash

# Script de Teste Completo - Todas as Funcionalidades
# Valida seções 2.2, 2.3 e 3 do guia

echo "🧪 =========================================="
echo "   TESTE COMPLETO DE FUNCIONALIDADES"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs
API_LEGISLATION="http://localhost:8000/api/v1/legislation"
API_EMENDA="http://localhost:8000/api/v1/emenda-pix"

# Contador
PASSED=0
FAILED=0

echo "📋 TESTE 2.2: Página de Detalhes da Legislação"
echo "=========================================="
echo ""

# Obter ID de uma legislação
LEGISLATION_ID=$(curl -s "$API_LEGISLATION/?limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)

if [ -z "$LEGISLATION_ID" ]; then
    echo -e "${RED}❌ Não foi possível obter ID de legislação${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Legislação ID: $LEGISLATION_ID${NC}"
echo ""

# Testar GET por ID
echo -n "Testando: GET /legislation/{id}... "
LEGISLATION_DATA=$(curl -s "$API_LEGISLATION/$LEGISLATION_ID")
if echo "$LEGISLATION_DATA" | grep -q "title\|id"; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FALHOU${NC}"
    ((FAILED++))
fi

# Verificar campos
echo -n "Verificando: Título presente... "
HAS_TITLE=$(echo "$LEGISLATION_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if d.get('title') else 'VAZIO')" 2>/dev/null)
if [ "$HAS_TITLE" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FALHOU${NC}"
    ((FAILED++))
fi

echo -n "Verificando: Autor presente... "
HAS_AUTHOR=$(echo "$LEGISLATION_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if d.get('author') else 'VAZIO')" 2>/dev/null)
if [ "$HAS_AUTHOR" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Autor pode estar vazio${NC}"
fi

echo -n "Verificando: Conteúdo presente... "
HAS_CONTENT=$(echo "$LEGISLATION_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if d.get('content') else 'VAZIO')" 2>/dev/null)
if [ "$HAS_CONTENT" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FALHOU${NC}"
    ((FAILED++))
fi

echo ""
echo "📋 TESTE 2.3: Simplificação com IA"
echo "=========================================="
echo ""

# Testar simplificação
echo -n "Testando: POST /legislation/{id}/simplify?level=basic... "
SIMPLIFY_RESPONSE=$(curl -s -X POST "$API_LEGISLATION/$LEGISLATION_ID/simplify?level=basic" 2>/dev/null)
if echo "$SIMPLIFY_RESPONSE" | grep -q "simplified_content\|title\|id"; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
    
    # Verificar se simplificação foi retornada
    echo -n "Verificando: Texto simplificado retornado... "
    HAS_SIMPLIFIED=$(echo "$SIMPLIFY_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if d.get('simplified_content') else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_SIMPLIFIED" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Simplificação não retornada${NC}"
    fi
else
    echo -e "${RED}❌ FALHOU${NC}"
    echo "   Resposta: ${SIMPLIFY_RESPONSE:0:200}..."
    ((FAILED++))
fi

# Testar diferentes níveis
for level in basic intermediate advanced; do
    echo -n "Testando: Nível $level... "
    LEVEL_RESPONSE=$(curl -s -X POST "$API_LEGISLATION/$LEGISLATION_ID/simplify?level=$level" 2>/dev/null)
    if echo "$LEVEL_RESPONSE" | grep -q "simplified_content\|title"; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
done

echo ""
echo "📋 TESTE 3: Verificação do Tema e Dor"
echo "=========================================="
echo ""

# Teste 3.1: Falta de Transparência (Emenda Pix)
echo "3.1 Resolve a Dor: Falta de Transparência"
echo "----------------------------------------"

EMENDA_ID=$(curl -s "$API_EMENDA/?limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)

if [ -n "$EMENDA_ID" ]; then
    EMENDA_DATA=$(curl -s "$API_EMENDA/$EMENDA_ID")
    
    echo -n "  Para onde foi o dinheiro (destinatário)... "
    HAS_DEST=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if d.get('destinatario_nome') else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_DEST" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    echo -n "  Quanto foi destinado (valores)... "
    HAS_VALOR=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if d.get('valor_aprovado') else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_VALOR" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    echo -n "  Quanto foi executado (percentual)... "
    HAS_PERCENT=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if d.get('percentual_executado') is not None else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_PERCENT" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    echo -n "  Status da execução... "
    HAS_STATUS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if d.get('status_execucao') else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_STATUS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    echo -n "  Plano de trabalho (metas)... "
    HAS_PLANO=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); plano=d.get('plano_trabalho', []); print('OK' if plano and len(plano) > 0 else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_PLANO" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Plano pode estar vazio${NC}"
    fi
    
    echo -n "  Alertas (quando há problemas)... "
    HAS_ALERTAS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('alertas', []); print('OK' if a and len(a) > 0 else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_ALERTAS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU (tem alertas)${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Sem alertas (pode ser normal)${NC}"
    fi
    
    echo -n "  Análise de risco de desvio... "
    HAS_RISCO=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); r=d.get('risco_desvio'); print('OK' if r is not None else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_RISCO" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Risco calculado após análise IA${NC}"
    fi
fi

echo ""
echo "3.2 Resolve a Dor: Falta de Rastreabilidade"
echo "----------------------------------------"

if [ -n "$EMENDA_ID" ]; then
    echo -n "  Progresso real da execução... "
    HAS_PROGRESS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print('OK' if d.get('percentual_executado') is not None and d.get('valor_pago') is not None else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_PROGRESS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    echo -n "  Metas do plano de trabalho... "
    if [ "$HAS_PLANO" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Plano pode estar vazio${NC}"
    fi
    
    echo -n "  Status das metas (concluídas/atrasadas)... "
    HAS_META_STATUS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); plano=d.get('plano_trabalho', []); print('OK' if plano and any(m.get('status') for m in plano) else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_META_STATUS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Status de metas pode estar vazio${NC}"
    fi
    
    echo -n "  Links para fontes (CEIS/Portal)... "
    HAS_LINKS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); ceis=d.get('processo_sei'); portal=d.get('link_portal_transparencia'); print('OK' if ceis or portal else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_LINKS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Links podem estar vazios${NC}"
    fi
fi

echo ""
echo "3.3 Resolve a Dor: Controle Social"
echo "----------------------------------------"

echo -n "  Filtros (deputado, município, área)... "
FILTER_TEST=$(curl -s "$API_EMENDA/?destinatario_uf=MT" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print('OK' if items else 'VAZIO')" 2>/dev/null)
if [ "$FILTER_TEST" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FALHOU${NC}"
    ((FAILED++))
fi

echo -n "  Busca de emendas específicas... "
SEARCH_TEST=$(curl -s "$API_EMENDA/?limit=5" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print('OK' if items and len(items) > 0 else 'VAZIO')" 2>/dev/null)
if [ "$SEARCH_TEST" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FALHOU${NC}"
    ((FAILED++))
fi

echo ""
echo "3.4 Uso de IA (Critério do Hackathon)"
echo "----------------------------------------"

if [ -n "$EMENDA_ID" ]; then
    # Executar análise IA
    ANALYZE_RESPONSE=$(curl -s -X POST "$API_EMENDA/$EMENDA_ID/analyze" 2>/dev/null)
    
    echo -n "  IA analisa automaticamente a execução... "
    HAS_ANALISE=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia'); print('OK' if a else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_ANALISE" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    echo -n "  IA detecta atrasos automaticamente... "
    HAS_ATRASO_ALERT=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('alertas', []); tipos=[al.get('tipo') for al in a]; print('OK' if 'atraso' in tipos else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_ATRASO_ALERT" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Sem alerta de atraso (pode ser normal)${NC}"
    fi
    
    echo -n "  IA calcula risco de desvio... "
    HAS_RISCO_CALC=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); r=a.get('risco_desvio'); print('OK' if r is not None else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_RISCO_CALC" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    echo -n "  IA gera alertas proativos... "
    HAS_ALERTAS_IA=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('alertas', []); print('OK' if a and len(a) > 0 else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_ALERTAS_IA" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Sem alertas (pode ser normal)${NC}"
    fi
    
    echo -n "  IA gera recomendações acionáveis... "
    HAS_RECS=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); r=a.get('recomendacoes', []); print('OK' if r and len(r) > 0 else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_RECS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Sem recomendações (pode ser normal)${NC}"
    fi
    
    echo -n "  IA calcula score de transparência... "
    HAS_TRANS_SCORE=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); s=a.get('transparencia_score'); print('OK' if s is not None else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_TRANS_SCORE" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
fi

echo ""
echo "📋 RESUMO DOS TESTES"
echo "=========================================="
echo -e "${GREEN}✅ Passou: $PASSED${NC}"
echo -e "${RED}❌ Falhou: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 Todos os testes passaram!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Alguns testes falharam. Verifique acima.${NC}"
    exit 1
fi

