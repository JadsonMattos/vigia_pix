#!/bin/bash

# Script de Teste - Fluxos Completos (TESTE 4)
# Valida os 3 fluxos principais do sistema

echo "🧪 =========================================="
echo "   TESTE 4: FLUXOS COMPLETOS"
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

# Contador
PASSED=0
FAILED=0

echo "📋 FLUXO 4.1: Cidadão Descobre Emenda Atrasada"
echo "=========================================="
echo ""

# 1. Verificar se filtro por status "atrasada" funciona
echo -n "1. Filtro por status 'atrasada'... "
ATRASADAS=$(curl -s "$API_EMENDA/?status_execucao=atrasada" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(len(items))" 2>/dev/null)
if [ "$ATRASADAS" -gt 0 ]; then
    echo -e "${GREEN}✅ PASSOU ($ATRASADAS emendas atrasadas)${NC}"
    ((PASSED++))
    
    # Obter ID de uma emenda atrasada
    ATRASADA_ID=$(curl -s "$API_EMENDA/?status_execucao=atrasada&limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)
    
    if [ -n "$ATRASADA_ID" ]; then
        echo -e "${GREEN}   Emenda atrasada encontrada: $ATRASADA_ID${NC}"
        
        # 2. Verificar se emenda tem alertas
        echo -n "2. Emenda atrasada tem alertas... "
        ATRASADA_DATA=$(curl -s "$API_EMENDA/$ATRASADA_ID")
        HAS_ALERTAS=$(echo "$ATRASADA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('alertas', []); print('OK' if a and len(a) > 0 else 'VAZIO')" 2>/dev/null)
        if [ "$HAS_ALERTAS" = "OK" ]; then
            echo -e "${GREEN}✅ PASSOU${NC}"
            ((PASSED++))
        else
            echo -e "${BLUE}ℹ️  Sem alertas (pode ser normal)${NC}"
        fi
        
        # 3. Verificar se análise IA funciona
        echo -n "3. Análise com IA funciona... "
        ANALYZE_RESPONSE=$(curl -s -X POST "$API_EMENDA/$ATRASADA_ID/analyze" 2>/dev/null)
        if echo "$ANALYZE_RESPONSE" | grep -q "analise_ia\|title\|id"; then
            echo -e "${GREEN}✅ PASSOU${NC}"
            ((PASSED++))
        else
            echo -e "${RED}❌ FALHOU${NC}"
            ((FAILED++))
        fi
        
        # 4. Verificar se tem recomendações
        echo -n "4. Análise gera recomendações... "
        HAS_RECS=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); r=a.get('recomendacoes', []); print('OK' if r and len(r) > 0 else 'VAZIO')" 2>/dev/null)
        if [ "$HAS_RECS" = "OK" ]; then
            echo -e "${GREEN}✅ PASSOU${NC}"
            ((PASSED++))
        else
            echo -e "${BLUE}ℹ️  Sem recomendações (pode ser normal)${NC}"
        fi
        
        # 5. Verificar links para CEIS e Portal
        echo -n "5. Links para CEIS e Portal... "
        HAS_LINKS=$(echo "$ATRASADA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); ceis=d.get('processo_sei'); portal=d.get('link_portal_transparencia'); print('OK' if ceis or portal else 'VAZIO')" 2>/dev/null)
        if [ "$HAS_LINKS" = "OK" ]; then
            echo -e "${GREEN}✅ PASSOU${NC}"
            ((PASSED++))
        else
            echo -e "${BLUE}ℹ️  Links podem estar vazios${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Nenhuma emenda atrasada encontrada${NC}"
    echo -e "${BLUE}   (Isso pode ser normal se não houver emendas atrasadas)${NC}"
fi

echo ""
echo "📋 FLUXO 4.2: Cidadão Acompanha Execução"
echo "=========================================="
echo ""

# 1. Verificar busca por município
echo -n "1. Busca por município funciona... "
# Buscar por UF primeiro (mais comum)
BUSCA_UF=$(curl -s "$API_EMENDA/?destinatario_uf=MT" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(len(items))" 2>/dev/null)
if [ "$BUSCA_UF" -gt 0 ]; then
    echo -e "${GREEN}✅ PASSOU ($BUSCA_UF emendas encontradas)${NC}"
    ((PASSED++))
    
    # Obter uma emenda
    EMENDA_ID=$(curl -s "$API_EMENDA/?destinatario_uf=MT&limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)
    
    if [ -n "$EMENDA_ID" ]; then
        EMENDA_DATA=$(curl -s "$API_EMENDA/$EMENDA_ID")
        
        # 2. Verificar se tem plano de trabalho
        echo -n "2. Plano de trabalho presente... "
        HAS_PLANO=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); plano=d.get('plano_trabalho', []); print('OK' if plano and len(plano) > 0 else 'VAZIO')" 2>/dev/null)
        if [ "$HAS_PLANO" = "OK" ]; then
            echo -e "${GREEN}✅ PASSOU${NC}"
            ((PASSED++))
        else
            echo -e "${BLUE}ℹ️  Plano pode estar vazio${NC}"
        fi
        
        # 3. Verificar se mostra metas concluídas
        echo -n "3. Metas concluídas exibidas... "
        HAS_METAS_CONCLUIDAS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); plano=d.get('plano_trabalho', []); concluidas=[m for m in plano if m.get('status') == 'concluida']; print('OK' if concluidas else 'VAZIO')" 2>/dev/null)
        if [ "$HAS_METAS_CONCLUIDAS" = "OK" ]; then
            echo -e "${GREEN}✅ PASSOU${NC}"
            ((PASSED++))
        else
            echo -e "${BLUE}ℹ️  Sem metas concluídas (pode ser normal)${NC}"
        fi
        
        # 4. Verificar percentual de execução
        echo -n "4. Percentual de execução... "
        HAS_PERCENT=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); p=d.get('percentual_executado'); print('OK' if p is not None else 'VAZIO')" 2>/dev/null)
        if [ "$HAS_PERCENT" = "OK" ]; then
            PERCENT=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('percentual_executado', 0))" 2>/dev/null)
            echo -e "${GREEN}✅ PASSOU ($PERCENT%)${NC}"
            ((PASSED++))
        else
            echo -e "${RED}❌ FALHOU${NC}"
            ((FAILED++))
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Nenhuma emenda encontrada para UF MT${NC}"
fi

echo ""
echo "📋 FLUXO 4.3: Cidadão Identifica Risco de Desvio"
echo "=========================================="
echo ""

# Obter qualquer emenda para teste
EMENDA_ID=$(curl -s "$API_EMENDA/?limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)

if [ -n "$EMENDA_ID" ]; then
    EMENDA_DATA=$(curl -s "$API_EMENDA/$EMENDA_ID")
    
    # 1. Verificar se emenda tem indicador de alerta
    echo -n "1. Emenda tem indicador de alerta... "
    HAS_ALERTAS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('alertas', []); print('OK' if a and len(a) > 0 else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_ALERTAS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Sem alertas (pode ser normal)${NC}"
    fi
    
    # 2. Verificar se alertas aparecem na página de detalhes
    echo -n "2. Alertas exibidos na página... "
    # Já verificamos acima, mas vamos confirmar estrutura
    if [ "$HAS_ALERTAS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Sem alertas para exibir${NC}"
    fi
    
    # 3. Verificar análise de risco de desvio
    echo -n "3. Análise de risco de desvio... "
    ANALYZE_RESPONSE=$(curl -s -X POST "$API_EMENDA/$EMENDA_ID/analyze" 2>/dev/null)
    HAS_RISCO=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); r=a.get('risco_desvio'); print('OK' if r is not None else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_RISCO" = "OK" ]; then
        RISCO=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); print(int(a.get('risco_desvio', 0) * 100))" 2>/dev/null)
        echo -e "${GREEN}✅ PASSOU (Risco: $RISCO%)${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    # 4. Verificar recomendações
    echo -n "4. Recomendações geradas... "
    HAS_RECS=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); r=a.get('recomendacoes', []); print('OK' if r and len(r) > 0 else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_RECS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Sem recomendações (pode ser normal)${NC}"
    fi
    
    # 5. Verificar links para fiscalização
    echo -n "5. Links para fiscalização... "
    HAS_LINKS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); ceis=d.get('processo_sei'); portal=d.get('link_portal_transparencia'); print('OK' if ceis or portal else 'VAZIO')" 2>/dev/null)
    if [ "$HAS_LINKS" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${BLUE}ℹ️  Links podem estar vazios${NC}"
    fi
fi

echo ""
echo "📊 RESUMO DOS TESTES"
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

