#!/bin/bash

# Script Interativo de Teste Manual - Voz Cidadã
# Este script guia você através de todos os testes

echo "🧪 =========================================="
echo "   TESTE MANUAL - VOZ CIDADÃ"
echo "   MVP Emenda Pix + Funcionalidades Existentes"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para verificar serviço
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

# Função para pausa
pause() {
    echo ""
    read -p "Pressione ENTER para continuar..."
    echo ""
}

echo "📋 FASE 1: Verificação de Pré-requisitos"
echo "=========================================="
echo ""

# Verificar serviços
echo "1. Verificando serviços..."
check_service "Backend" "http://localhost:8000/health"
check_service "Frontend" "http://localhost:3000"

echo ""
echo "2. Verificando dados no banco..."
docker compose exec backend python scripts/test_emenda_pix_api.py 2>/dev/null | tail -3

pause

echo ""
echo "📋 FASE 2: Teste do MVP Emenda Pix"
echo "=========================================="
echo ""

echo "🎯 TESTE 2.1: Dashboard de Emendas Pix"
echo "--------------------------------------"
echo ""
echo "1. Abra no navegador: ${BLUE}http://localhost:3000/emenda-pix${NC}"
echo ""
echo "Verifique:"
echo "  [ ] Página carrega sem erros"
echo "  [ ] Mostra 4 cards de estatísticas no topo"
echo "  [ ] Lista de emendas em cards (deve ter 5 emendas)"
echo "  [ ] Cada card mostra: número, autor, destinatário, valor, progresso"
echo ""
pause

echo ""
echo "🎯 TESTE 2.2: Filtros"
echo "--------------------------------------"
echo ""
echo "Teste cada filtro:"
echo "  1. Busca: Digite 'Cuiabá' → deve filtrar"
echo "  2. Status: Selecione 'Atrasada' → deve mostrar apenas atrasadas"
echo "  3. Área: Selecione 'Saúde' → deve filtrar"
echo "  4. UF: Selecione 'MT' → deve filtrar"
echo "  5. Limpar: Clique em '🔄 Limpar' → deve resetar"
echo ""
pause

echo ""
echo "🎯 TESTE 2.3: Página de Detalhes"
echo "--------------------------------------"
echo ""
echo "1. Clique em qualquer card de emenda"
echo ""
echo "Verifique na página de detalhes:"
echo "  [ ] Seção 'Valores e Execução' com todos os valores"
echo "  [ ] Barra de progresso funcionando"
echo "  [ ] Seção 'Informações' completa"
echo "  [ ] Seção 'Plano de Trabalho' (se houver)"
echo "  [ ] Seção 'Alertas' (se aplicável)"
echo "  [ ] Seção 'Análise IA' (se já analisada)"
echo "  [ ] Seção 'Notícias' (se houver)"
echo "  [ ] Links para CEIS e Portal da Transparência"
echo ""
pause

echo ""
echo "🎯 TESTE 2.4: Análise com IA"
echo "--------------------------------------"
echo ""
echo "1. Na página de detalhes, clique em '🤖 Analisar com IA'"
echo ""
echo "Verifique:"
echo "  [ ] Botão mostra '⏳ Analisando...' durante processo"
echo "  [ ] Após análise, alertas são gerados (se aplicável)"
echo "  [ ] Score de transparência aparece"
echo "  [ ] Risco de desvio é calculado"
echo "  [ ] Recomendações são exibidas"
echo "  [ ] Mensagem de sucesso aparece"
echo ""
echo "Teste com diferentes emendas:"
echo "  - Emenda atrasada → deve gerar alerta"
echo "  - Emenda com baixa execução → deve gerar alerta"
echo ""
pause

echo ""
echo "📋 FASE 3: Teste de Funcionalidades Existentes"
echo "=========================================="
echo ""

echo "🎯 TESTE 3.1: Dashboard Principal"
echo "--------------------------------------"
echo ""
echo "1. Acesse: ${BLUE}http://localhost:3000/dashboard${NC}"
echo ""
echo "Verifique:"
echo "  [ ] Estatísticas são exibidas"
echo "  [ ] Botão 'Sincronizar Legislações' funciona"
echo "  [ ] Filtros funcionam"
echo "  [ ] Lista de legislações aparece"
echo ""
pause

echo ""
echo "🎯 TESTE 3.2: Simplificação com IA"
echo "--------------------------------------"
echo ""
echo "1. Vá para uma legislação e clique em 'Ver Detalhes'"
echo "2. Selecione nível (Básico, Intermediário, Avançado)"
echo "3. Clique em '🤖 Simplificar com IA'"
echo ""
echo "Verifique:"
echo "  [ ] Simplificação é gerada"
echo "  [ ] Texto simplificado aparece"
echo "  [ ] Percentual de redução é mostrado"
echo ""
pause

echo ""
echo "📋 FASE 4: Validação do Tema e Dor"
echo "=========================================="
echo ""

echo "✅ Verifique se resolve a DOR: Falta de Transparência"
echo "  [ ] Cidadão vê PARA ONDE foi o dinheiro"
echo "  [ ] Cidadão vê QUANTO foi destinado"
echo "  [ ] Cidadão vê QUANTO foi executado"
echo "  [ ] Cidadão vê STATUS da execução"
echo "  [ ] Cidadão vê PLANO DE TRABALHO"
echo "  [ ] Cidadão vê ALERTAS quando há problemas"
echo ""
pause

echo ""
echo "✅ Verifique se resolve a DOR: Falta de Rastreabilidade"
echo "  [ ] Sistema mostra PROGRESSO REAL"
echo "  [ ] Sistema mostra METAS do plano"
echo "  [ ] Sistema mostra METAS CONCLUÍDAS"
echo "  [ ] Sistema mostra METAS ATRASADAS"
echo "  [ ] Sistema mostra LINKS para fontes"
echo ""
pause

echo ""
echo "✅ Verifique se resolve a DOR: Controle Social"
echo "  [ ] Cidadão pode FILTRAR (deputado, município, área)"
echo "  [ ] Cidadão pode BUSCAR emendas"
echo "  [ ] Sistema GERA ALERTAS proativos"
echo "  [ ] Sistema RECOMENDA AÇÕES"
echo "  [ ] Interface é ACESSÍVEL"
echo ""
pause

echo ""
echo "✅ Verifique USO DE IA (Critério do Hackathon)"
echo "  [ ] IA analisa execução automaticamente"
echo "  [ ] IA detecta atrasos"
echo "  [ ] IA calcula risco de desvio"
echo "  [ ] IA gera alertas proativos"
echo "  [ ] IA gera recomendações"
echo "  [ ] IA calcula score de transparência"
echo ""
pause

echo ""
echo "📋 FASE 5: Teste de Fluxos Completos"
echo "=========================================="
echo ""

echo "🎯 FLUXO 1: Cidadão Descobre Emenda Atrasada"
echo "--------------------------------------"
echo ""
echo "Passos:"
echo "  1. Acesse dashboard de Emenda Pix"
echo "  2. Filtre por 'Atrasada'"
echo "  3. Clique em uma emenda atrasada"
echo "  4. Veja alertas"
echo "  5. Clique em '🤖 Analisar com IA'"
echo "  6. Veja análise completa e recomendações"
echo ""
echo "Verifique se todo o fluxo funciona sem erros"
pause

echo ""
echo "🎯 FLUXO 2: Cidadão Acompanha Execução"
echo "--------------------------------------"
echo ""
echo "Passos:"
echo "  1. Acesse dashboard"
echo "  2. Busque por 'Cuiabá'"
echo "  3. Veja emendas do município"
echo "  4. Clique em uma emenda"
echo "  5. Veja plano de trabalho"
echo "  6. Verifique metas concluídas"
echo "  7. Veja percentual de execução"
echo ""
echo "Verifique se consegue acompanhar o progresso"
pause

echo ""
echo "📋 FASE 6: Teste de API (Swagger)"
echo "=========================================="
echo ""
echo "1. Acesse: ${BLUE}http://localhost:8000/api/docs${NC}"
echo ""
echo "Teste os endpoints:"
echo "  [ ] GET /api/v1/emenda-pix/ → Lista emendas"
echo "  [ ] GET /api/v1/emenda-pix/{id} → Detalhes"
echo "  [ ] POST /api/v1/emenda-pix/{id}/analyze → Análise IA"
echo ""
echo "Para cada endpoint:"
echo "  - Clique em 'Try it out'"
echo "  - Execute"
echo "  - Verifique resposta"
pause

echo ""
echo "📋 FASE 7: Teste de Responsividade"
echo "=========================================="
echo ""
echo "1. Abra o DevTools (F12)"
echo "2. Ative modo responsivo (Ctrl+Shift+M)"
echo "3. Teste em diferentes tamanhos:"
echo "   - Mobile (375px)"
echo "   - Tablet (768px)"
echo "   - Desktop (1920px)"
echo ""
echo "Verifique:"
echo "  [ ] Layout se adapta"
echo "  [ ] Cards são legíveis"
echo "  [ ] Botões são clicáveis"
echo "  [ ] Filtros são acessíveis"
pause

echo ""
echo "✅ =========================================="
echo "   TESTE CONCLUÍDO!"
echo "=========================================="
echo ""
echo "Documente qualquer problema encontrado no arquivo:"
echo "  ${BLUE}GUIA_TESTE_MANUAL_COMPLETO.md${NC}"
echo ""
echo "Resumo:"
echo "  - Funcionalidades testadas: ✅"
echo "  - Resolve tema do hackathon: ✅"
echo "  - Resolve dor percebida: ✅"
echo ""

