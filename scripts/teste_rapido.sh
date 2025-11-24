#!/bin/bash
# Script de teste RÁPIDO com timeouts

echo "⚡ Teste Rápido do Sistema (com timeouts)"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar containers
echo "1. Verificando containers..."
if docker ps | grep -q "vigiapix"; then
    echo -e "${GREEN}✅ Containers rodando${NC}"
else
    echo -e "${RED}❌ Containers não estão rodando${NC}"
    echo "   Execute: docker-compose up -d"
    exit 1
fi

# Testar health check (timeout 2s)
echo ""
echo "2. Testando health check (timeout 2s)..."
HEALTH=$(timeout 2 curl -s --max-time 2 http://localhost:8000/health 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$HEALTH" ]; then
    echo -e "${GREEN}✅ Backend respondendo${NC}"
else
    echo -e "${YELLOW}⚠️  Backend não respondeu (pode estar iniciando)${NC}"
fi

# Testar listagem (timeout 3s)
echo ""
echo "3. Testando listagem de emendas (timeout 3s)..."
EMENDAS=$(timeout 3 curl -s --max-time 3 "http://localhost:8000/api/v1/emenda-pix/?limit=1" 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$EMENDAS" ]; then
    COUNT=$(echo "$EMENDAS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('items', [])))" 2>/dev/null || echo "0")
    if [ "$COUNT" -gt "0" ]; then
        echo -e "${GREEN}✅ $COUNT emenda(s) encontrada(s)${NC}"
        
        # Obter ID
        EMENDA_ID=$(echo "$EMENDAS" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)
        
        if [ -n "$EMENDA_ID" ]; then
            # Testar Trust Score (timeout 3s)
            echo ""
            echo "4. Testando Trust Score (timeout 3s)..."
            TRUST=$(timeout 3 curl -s --max-time 3 "http://localhost:8000/api/v1/emenda-pix/$EMENDA_ID/trust-score" 2>/dev/null)
            if [ $? -eq 0 ] && [ -n "$TRUST" ]; then
                SCORE=$(echo "$TRUST" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('trust_score', 0))" 2>/dev/null || echo "0")
                if [ "$SCORE" != "0" ]; then
                    echo -e "${GREEN}✅ Trust Score: $SCORE/100${NC}"
                else
                    echo -e "${YELLOW}⚠️  Trust Score não calculado${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  Timeout ou erro no Trust Score${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Nenhuma emenda encontrada${NC}"
        echo "   Execute: docker-compose exec backend python scripts/seed_emenda_pix_data.py"
    fi
else
    echo -e "${YELLOW}⚠️  Timeout ou erro na listagem${NC}"
fi

# Resumo
echo ""
echo "📋 Resumo:"
echo "  - Containers: $(docker ps | grep -c vigiapix) rodando"
echo "  - Backend: http://localhost:8000/api/docs"
echo "  - Frontend: http://localhost:3000"
echo ""
echo -e "${GREEN}✅ Teste rápido concluído!${NC}"

