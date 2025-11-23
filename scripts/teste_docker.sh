#!/bin/bash
# Script de teste completo com Docker

echo "🐳 Testando sistema com Docker"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose não encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker encontrado${NC}"
echo ""

# Verificar se containers estão rodando
if ! docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Containers não estão rodando. Iniciando...${NC}"
    docker-compose up -d
    echo "⏳ Aguardando inicialização (15 segundos)..."
    sleep 15
fi

# Testar health checks (com timeout)
echo "1. Testando health checks..."
BACKEND_OK=$(timeout 3 curl -s --max-time 2 http://localhost:8000/health 2>/dev/null | grep -q "healthy" && echo "OK" || echo "FAIL")
FRONTEND_OK=$(timeout 3 curl -s --max-time 2 http://localhost:3000 2>/dev/null | grep -q "html\|<!DOCTYPE" && echo "OK" || echo "FAIL")

if [ "$BACKEND_OK" = "OK" ]; then
    echo -e "${GREEN}✅ Backend OK${NC}"
else
    echo -e "${RED}❌ Backend falhou${NC}"
fi

if [ "$FRONTEND_OK" = "OK" ]; then
    echo -e "${GREEN}✅ Frontend OK${NC}"
else
    echo -e "${RED}❌ Frontend falhou${NC}"
fi

# Testar endpoints
echo ""
echo "2. Testando endpoints principais..."

# Listar emendas (com timeout)
EMENDAS=$(timeout 5 curl -s --max-time 3 http://localhost:8000/api/v1/emenda-pix/?limit=1 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$EMENDAS" ]; then
    COUNT=$(echo "$EMENDAS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('items', [])))" 2>/dev/null || echo "0")
    if [ "$COUNT" -gt "0" ]; then
        echo -e "${GREEN}✅ $COUNT emenda(s) encontrada(s)${NC}"
        
        # Obter ID da primeira emenda
        EMENDA_ID=$(echo "$EMENDAS" | python3 -c "import sys, json; items=json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')" 2>/dev/null)
        
        if [ -n "$EMENDA_ID" ]; then
            # Testar Trust Score (com timeout)
            echo ""
            echo "3. Testando Trust Score..."
            TRUST_SCORE=$(timeout 5 curl -s --max-time 3 "http://localhost:8000/api/v1/emenda-pix/$EMENDA_ID/trust-score" 2>/dev/null)
            if [ $? -eq 0 ]; then
                SCORE=$(echo "$TRUST_SCORE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('trust_score', 0))" 2>/dev/null || echo "0")
                if [ "$SCORE" != "0" ]; then
                    echo -e "${GREEN}✅ Trust Score: $SCORE/100${NC}"
                else
                    echo -e "${YELLOW}⚠️  Trust Score não calculado${NC}"
                fi
            else
                echo -e "${RED}❌ Erro ao calcular Trust Score${NC}"
            fi
            
            # Testar Análise IA (com timeout - pode demorar mais)
            echo ""
            echo "4. Testando Análise IA (pode demorar ~10s)..."
            ANALISE=$(timeout 15 curl -s --max-time 10 -X POST "http://localhost:8000/api/v1/emenda-pix/$EMENDA_ID/analyze" 2>/dev/null)
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Análise IA funcionando${NC}"
            else
                echo -e "${RED}❌ Erro na análise IA${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Nenhuma emenda encontrada - execute seeds:${NC}"
        echo "   docker-compose exec backend python scripts/seed_emenda_pix_data.py"
    fi
else
    echo -e "${RED}❌ Erro ao listar emendas${NC}"
fi

echo ""
echo -e "${GREEN}✅ Testes concluídos!${NC}"
echo ""
echo "📋 Acessos:"
echo "  - Backend API: http://localhost:8000/api/docs"
echo "  - Frontend: http://localhost:3000"
