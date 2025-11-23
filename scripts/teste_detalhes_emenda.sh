#!/bin/bash

# Script de Teste da Página de Detalhes da Emenda
# Valida todas as funcionalidades mencionadas no guia

echo "🧪 =========================================="
echo "   TESTE DA PÁGINA DE DETALHES DA EMENDA"
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

# Contador
PASSED=0
FAILED=0

# Função para testar campo
test_field() {
    local name=$1
    local field=$2
    local emenda_data=$3
    
    echo -n "Verificando: $name... "
    
    value=$(echo "$emenda_data" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('$field', 'N/A'))" 2>/dev/null)
    
    if [ "$value" != "N/A" ] && [ "$value" != "null" ] && [ -n "$value" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠️  Campo vazio ou não presente${NC}"
        ((FAILED++))
        return 1
    fi
}

# Obter ID de uma emenda
echo "📋 FASE 1: Obter Emenda para Teste"
echo "=========================================="
echo ""

FIRST_ID=$(curl -s "$API_URL/?limit=1" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)

if [ -z "$FIRST_ID" ]; then
    echo -e "${RED}❌ Não foi possível obter ID de emenda${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Emenda ID: $FIRST_ID${NC}"
echo ""

# Obter dados da emenda
EMENDA_DATA=$(curl -s "$API_URL/$FIRST_ID")

echo "📋 FASE 2: Validação de Campos"
echo "=========================================="
echo ""

# Valores e Execução
test_field "Valor Aprovado" "valor_aprovado" "$EMENDA_DATA"
test_field "Valor Pago" "valor_pago" "$EMENDA_DATA"
test_field "Valor Empenhado" "valor_empenhado" "$EMENDA_DATA"
test_field "Valor Liquidado" "valor_liquidado" "$EMENDA_DATA"
test_field "Percentual Executado" "percentual_executado" "$EMENDA_DATA"

# Informações
test_field "Autor Nome" "autor_nome" "$EMENDA_DATA"
test_field "Destinatário Nome" "destinatario_nome" "$EMENDA_DATA"
test_field "Destinatário UF" "destinatario_uf" "$EMENDA_DATA"

# Plano de Trabalho
echo -n "Verificando: Plano de Trabalho... "
PLANO=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); plano=d.get('plano_trabalho', []); print('OK' if plano and len(plano) > 0 else 'VAZIO')" 2>/dev/null)
if [ "$PLANO" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Plano de trabalho vazio${NC}"
    ((FAILED++))
fi

# Alertas
echo -n "Verificando: Alertas... "
ALERTAS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); alertas=d.get('alertas', []); print('OK' if alertas and len(alertas) > 0 else 'VAZIO')" 2>/dev/null)
if [ "$ALERTAS" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU (tem alertas)${NC}"
    ((PASSED++))
else
    echo -e "${BLUE}ℹ️  Sem alertas (normal se emenda não está atrasada)${NC}"
fi

# Análise IA
echo -n "Verificando: Análise IA... "
ANALISE=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); analise=d.get('analise_ia'); print('OK' if analise else 'VAZIO')" 2>/dev/null)
if [ "$ANALISE" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU (tem análise)${NC}"
    ((PASSED++))
else
    echo -e "${BLUE}ℹ️  Sem análise IA (execute análise primeiro)${NC}"
fi

# Notícias
echo -n "Verificando: Notícias... "
NOTICIAS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); noticias=d.get('noticias_relacionadas', []); print('OK' if noticias and len(noticias) > 0 else 'VAZIO')" 2>/dev/null)
if [ "$NOTICIAS" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU (tem notícias)${NC}"
    ((PASSED++))
else
    echo -e "${BLUE}ℹ️  Sem notícias (opcional)${NC}"
fi

# Datas
test_field "Data Início" "data_inicio" "$EMENDA_DATA"
test_field "Prazo Previsto" "data_prevista_conclusao" "$EMENDA_DATA"

# Links
echo -n "Verificando: Links (CEIS ou Portal)... "
LINKS=$(echo "$EMENDA_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); ceis=d.get('processo_sei'); portal=d.get('link_portal_transparencia'); print('OK' if ceis or portal else 'VAZIO')" 2>/dev/null)
if [ "$LINKS" = "OK" ]; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Sem links${NC}"
    ((FAILED++))
fi

echo ""
echo "📋 FASE 3: Teste de Análise IA"
echo "=========================================="
echo ""

echo -n "Testando: POST /analyze... "
ANALYZE_RESPONSE=$(curl -s -X POST "$API_URL/$FIRST_ID/analyze" 2>/dev/null)
if echo "$ANALYZE_RESPONSE" | grep -q "analise_ia\|numero_emenda"; then
    echo -e "${GREEN}✅ PASSOU${NC}"
    ((PASSED++))
    
    # Verificar se análise foi retornada na resposta
    echo -n "Verificando: Análise retornada na resposta... "
    ANALISE_RETORNADA=$(echo "$ANALYZE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); analise=d.get('analise_ia'); print('OK' if analise else 'VAZIO')" 2>/dev/null)
    if [ "$ANALISE_RETORNADA" = "OK" ]; then
        echo -e "${GREEN}✅ PASSOU${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Análise não retornada${NC}"
        ((FAILED++))
    fi
else
    echo -e "${RED}❌ FALHOU${NC}"
    echo "   Resposta: ${ANALYZE_RESPONSE:0:100}..."
    ((FAILED++))
fi

echo ""
echo "📋 FASE 4: Validação Visual (Manual)"
echo "=========================================="
echo ""
echo "⚠️  Testes manuais necessários no navegador:"
echo ""
echo "1. Acesse: ${BLUE}$FRONTEND_URL/$FIRST_ID${NC}"
echo ""
echo "2. Verifique Seção: Valores e Execução"
echo "   [ ] Valor Aprovado exibido"
echo "   [ ] Valor Pago exibido"
echo "   [ ] Valor Empenhado e Liquidado visíveis"
echo "   [ ] Barra de progresso mostra percentual"
echo "   [ ] Cores: vermelho (<50%), amarelo (50-80%), verde (>80%)"
echo ""
echo "3. Verifique Seção: Informações"
echo "   [ ] Autor completo (nome, partido, UF)"
echo "   [ ] Destinatário (nome, UF, tipo)"
echo "   [ ] Objetivo da emenda"
echo "   [ ] Descrição detalhada (se houver)"
echo "   [ ] Área da emenda"
echo ""
echo "4. Verifique Seção: Plano de Trabalho"
echo "   [ ] Lista todas as metas"
echo "   [ ] Mostra valor de cada meta"
echo "   [ ] Mostra prazo de cada meta"
echo "   [ ] Status de cada meta"
echo "   [ ] Contador de metas (X/Y concluídas)"
echo ""
echo "5. Verifique Seção: Alertas (se houver)"
echo "   [ ] Alertas são exibidos"
echo "   [ ] Severidade dos alertas (Alta, Média, Baixa)"
echo "   [ ] Mensagem do alerta é clara"
echo "   [ ] Data do alerta é exibida"
echo ""
echo "6. Verifique Seção: Análise com IA"
echo "   [ ] Score de Transparência (0-100%)"
echo "   [ ] Risco de Desvio (0-100%)"
echo "   [ ] Recomendações são exibidas (se houver)"
echo "   [ ] Barras de progresso para cada score"
echo ""
echo "7. Verifique Seção: Notícias Relacionadas"
echo "   [ ] Lista notícias (se houver)"
echo "   [ ] Título, fonte e data de cada notícia"
echo ""
echo "8. Verifique Seção: Links"
echo "   [ ] Link para CEIS (se houver processo)"
echo "   [ ] Link para Portal da Transparência (se houver)"
echo ""
echo "9. Verifique Seção: Datas Importantes"
echo "   [ ] Data de Início"
echo "   [ ] Prazo Previsto"
echo "   [ ] Data Real de Conclusão (se concluída)"
echo ""
echo "10. Teste Botão: Analisar com IA"
echo "    [ ] Clique em '🤖 Analisar com IA'"
echo "    [ ] Aguarde processamento"
echo "    [ ] Verifique se alertas aparecem"
echo "    [ ] Verifique se análise IA aparece"
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

