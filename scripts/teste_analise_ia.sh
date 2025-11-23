#!/bin/bash

# Script de Teste da Análise com IA
# Valida todas as funcionalidades mencionadas no guia

echo "🧪 =========================================="
echo "   TESTE DA ANÁLISE COM IA"
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

# Contador
PASSED=0
FAILED=0

# Função para testar análise
test_analyze() {
    local emenda_id=$1
    local emenda_num=$2
    local expected_alerts=$3
    
    echo ""
    echo "📋 Testando: $emenda_num"
    echo "----------------------------------------"
    
    # Obter emenda antes da análise
    echo -n "  Obtendo emenda antes da análise... "
    BEFORE_DATA=$(curl -s "$API_URL/$emenda_id")
    if echo "$BEFORE_DATA" | grep -q "numero_emenda"; then
        echo -e "${GREEN}✅${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC}"
        ((FAILED++))
        return 1
    fi
    
    # Executar análise
    echo -n "  Executando análise (POST /analyze)... "
    ANALYZE_RESPONSE=$(curl -s -X POST "$API_URL/$emenda_id/analyze" 2>/dev/null)
    
    if echo "$ANALYZE_RESPONSE" | grep -q "analise_ia"; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        echo "     Resposta: ${ANALYZE_RESPONSE:0:200}..."
        ((FAILED++))
        return 1
    fi
    
    # Verificar análise retornada
    echo -n "  Verificando: Análise retornada... "
    ANALISE=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia'); print('OK' if a else 'VAZIO')" 2>/dev/null)
    if [ "$ANALISE" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    # Verificar score de transparência
    echo -n "  Verificando: Score de Transparência... "
    SCORE_TRANS=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); s=a.get('transparencia_score', -1); print('OK' if 0 <= s <= 1 else 'INVALIDO')" 2>/dev/null)
    if [ "$SCORE_TRANS" = "OK" ]; then
        TRANS_VALUE=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); print(f\"{a.get('transparencia_score', 0)*100:.1f}%\")" 2>/dev/null)
        echo -e "${GREEN}✅ PASSOU (${TRANS_VALUE})${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    # Verificar risco de desvio
    echo -n "  Verificando: Risco de Desvio... "
    RISCO=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); r=a.get('risco_desvio', -1); print('OK' if 0 <= r <= 1 else 'INVALIDO')" 2>/dev/null)
    if [ "$RISCO" = "OK" ]; then
        RISCO_VALUE=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); print(f\"{a.get('risco_desvio', 0)*100:.1f}%\")" 2>/dev/null)
        echo -e "${GREEN}✅ PASSOU (${RISCO_VALUE})${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
    
    # Verificar recomendações
    echo -n "  Verificando: Recomendações... "
    RECS=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); r=a.get('recomendacoes', []); print('OK' if r and len(r) > 0 else 'VAZIO')" 2>/dev/null)
    if [ "$RECS" = "OK" ]; then
        REC_COUNT=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia', {}); r=a.get('recomendacoes', []); print(len(r))" 2>/dev/null)
        echo -e "${GREEN}✅ PASSOU ($REC_COUNT recomendações)${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Sem recomendações${NC}"
    fi
    
    # Verificar alertas
    echo -n "  Verificando: Alertas gerados... "
    ALERTAS=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('alertas', []); print('OK' if a and len(a) > 0 else 'VAZIO')" 2>/dev/null)
    if [ "$ALERTAS" = "OK" ]; then
        ALERT_COUNT=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('alertas', []); print(len(a))" 2>/dev/null)
        echo -e "${GREEN}✅ PASSOU ($ALERT_COUNT alerta(s))${NC}"
        ((PASSED++))
        
        # Verificar tipos de alertas
        echo -n "    Tipos de alertas: "
        TIPOS=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('alertas', []); tipos=[al.get('tipo', '') for al in a]; print(', '.join(set(tipos)))" 2>/dev/null)
        echo -e "${BLUE}$TIPOS${NC}"
    else
        if [ "$expected_alerts" = "true" ]; then
            echo -e "${YELLOW}⚠️  Esperava alertas mas não foram gerados${NC}"
        else
            echo -e "${BLUE}ℹ️  Sem alertas (normal)${NC}"
        fi
    fi
    
    # Verificar se análise foi salva
    echo -n "  Verificando: Análise salva no banco... "
    sleep 1
    AFTER_DATA=$(curl -s "$API_URL/$emenda_id")
    ANALISE_SALVA=$(echo "$AFTER_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); a=d.get('analise_ia'); print('OK' if a else 'VAZIO')" 2>/dev/null)
    if [ "$ANALISE_SALVA" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FALHOU${NC}"
        ((FAILED++))
    fi
}

echo "📋 FASE 1: Obter Emendas para Teste"
echo "=========================================="
echo ""

# Obter lista de emendas
EMENDAS_DATA=$(curl -s "$API_URL/?limit=5")
EMENDA_IDS=$(echo "$EMENDAS_DATA" | python3 -c "
import sys, json
items = json.load(sys.stdin).get('items', [])
for e in items:
    print(f\"{e['id']}|{e['numero_emenda']}|{e['status_execucao']}|{e['percentual_executado']}\")
" 2>/dev/null)

if [ -z "$EMENDA_IDS" ]; then
    echo -e "${RED}❌ Não foi possível obter emendas${NC}"
    exit 1
fi

echo "Emendas encontradas:"
echo "$EMENDA_IDS" | while IFS='|' read -r id numero status percentual; do
    echo "  - $numero: $status ($percentual%)"
done
echo ""

echo "📋 FASE 2: Teste de Análise com IA"
echo "=========================================="
echo ""

# Testar com primeira emenda (geralmente atrasada)
FIRST_LINE=$(echo "$EMENDA_IDS" | head -1)
FIRST_ID=$(echo "$FIRST_LINE" | cut -d'|' -f1)
FIRST_NUM=$(echo "$FIRST_LINE" | cut -d'|' -f2)
FIRST_STATUS=$(echo "$FIRST_LINE" | cut -d'|' -f3)

test_analyze "$FIRST_ID" "$FIRST_NUM" "true"

echo ""
echo "📋 FASE 3: Teste com Diferentes Cenários"
echo "=========================================="
echo ""

# Testar com emenda concluída (se houver)
CONCLUIDA=$(echo "$EMENDA_IDS" | grep "concluida" | head -1)
if [ -n "$CONCLUIDA" ]; then
    CONCLUIDA_ID=$(echo "$CONCLUIDA" | cut -d'|' -f1)
    CONCLUIDA_NUM=$(echo "$CONCLUIDA" | cut -d'|' -f2)
    test_analyze "$CONCLUIDA_ID" "$CONCLUIDA_NUM (Concluída)" "false"
fi

# Testar com emenda em execução (se houver)
EM_EXEC=$(echo "$EMENDA_IDS" | grep "em_execucao" | head -1)
if [ -n "$EM_EXEC" ]; then
    EM_EXEC_ID=$(echo "$EM_EXEC" | cut -d'|' -f1)
    EM_EXEC_NUM=$(echo "$EM_EXEC" | cut -d'|' -f2)
    test_analyze "$EM_EXEC_ID" "$EM_EXEC_NUM (Em Execução)" "false"
fi

echo ""
echo "📋 FASE 4: Validação de Funcionalidades do Frontend"
echo "=========================================="
echo ""
echo "⚠️  Testes manuais necessários no navegador:"
echo ""
echo "1. Acesse: ${BLUE}http://localhost:3000/emenda-pix${NC}"
echo "   Clique em uma emenda"
echo ""
echo "2. Verifique Botão '🤖 Analisar com IA':"
echo "   [ ] Botão está visível no topo da página"
echo "   [ ] Ao clicar, muda para '⏳ Analisando...'"
echo "   [ ] Botão fica desabilitado durante análise"
echo "   [ ] Após análise, alert aparece: '✅ Análise com IA concluída!'"
echo ""
echo "3. Verifique Seção 'Análise com IA' (aparece após análise):"
echo "   [ ] Score de Transparência exibido (0-100%)"
echo "   [ ] Barra de progresso azul para transparência"
echo "   [ ] Risco de Desvio exibido (0-100%)"
echo "   [ ] Barra de progresso colorida para risco:"
echo "       - Vermelho se > 70%"
echo "       - Amarelo se 40-70%"
echo "       - Verde se < 40%"
echo "   [ ] Recomendações exibidas (lista com bullet points)"
echo ""
echo "4. Verifique Alertas (se gerados):"
echo "   [ ] Alertas aparecem após análise"
echo "   [ ] Severidade com cores (Alta/Média/Baixa)"
echo "   [ ] Mensagem clara"
echo "   [ ] Data do alerta"
echo ""
echo "5. Teste com Diferentes Emendas:"
echo "   [ ] Emenda atrasada → deve gerar alerta de atraso"
echo "   [ ] Emenda com baixa execução → deve gerar alerta"
echo "   [ ] Emenda com alto risco → deve gerar alerta de risco de desvio"
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

