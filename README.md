# 🚀 VigiaPix

> **Fiscalização Inteligente de Emendas Pix com Inteligência Artificial**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

## 📖 Descrição

**VigiaPix** é um sistema especializado em rastreamento e transparência de Emendas Pix, utilizando Inteligência Artificial para transformar cada cidadão em um fiscal inteligente dos recursos públicos.

O sistema integra dados financeiros, políticos e físicos de múltiplas fontes (Portal da Transparência, Transferegov.br, CEIS) em um único "Trust Score" auditado por Inteligência Artificial, promovendo transparência radical e controle social sobre a execução de emendas parlamentares.

### 🎯 Principais Funcionalidades

- **🔍 Rastreamento Completo**: Acompanhamento de execução em tempo real com valores, metas, progresso e riscos
- **🤖 IA Proativa**: Análise automática com OpenAI, detecção de riscos e alertas inteligentes
- **📊 Transparência Total**: Mostra valores, metas, progresso e riscos de forma clara e acessível
- **🔗 Triangulação de Dados**: Integra Portal (financeiro), Gabinete (político) e Executor (físico)
- **🏆 Placar de Transparência**: Ranking e métricas por município e parlamentar
- **📜 Legislações Simplificadas**: Simplificação de textos legislativos com IA
- **💬 Bot WhatsApp**: Interação via WhatsApp para consulta de legislações
- **🗺️ Mapa Interativo**: Visualização geográfica das emendas com geocodificação

## 👥 Membros da Equipe

**Devs de Impacto - Hackathon 2025**

- **Tech Lead / Backend Core**: Desenvolvimento da arquitetura backend e integrações
- **IA/ML Engineer**: Implementação de análise com IA e NLP
- **Frontend Lead**: Desenvolvimento da interface Next.js e componentes React
- **Full Stack / DevOps**: Configuração de infraestrutura e CI/CD
- **Backend / Data Engineer**: Integração de dados e APIs externas

## 🛠️ Tecnologias

### Backend
- **Python 3.11+** com FastAPI
- **PostgreSQL** (banco de dados)
- **Redis** (cache)
- **OpenAI API** (análise e classificação com IA)

### Frontend
- **Next.js 14+** (App Router) com TypeScript
- **Tailwind CSS** (estilização)
- **React Query** (data fetching)
- **PWA** (Progressive Web App)

### Integrações
- Portal da Transparência
- Transferegov.br
- OpenStreetMap (geocodificação)
- OpenAI (análise de dados)

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 18+
- Docker e Docker Compose (opcional)
- PostgreSQL 14+ (se não usar Docker)
- Redis (se não usar Docker)

## 🚀 Instalação e Configuração

### Opção 1: Docker (Recomendado)

```bash
# Clone o repositório
git clone <repo-url>
cd vigia_pix

# Inicie os serviços
docker-compose up -d

# O backend estará disponível em http://localhost:8000
# O frontend estará disponível em http://localhost:3000
```

### Opção 2: Instalação Local

#### Backend

```bash
cd backend

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações:
# - DATABASE_URL
# - REDIS_URL
# - OPENAI_API_KEY

# Execute as migrações (se houver)
# alembic upgrade head

# Inicie o servidor
uvicorn src.main:app --reload
```

#### Frontend

```bash
cd frontend

# Instale as dependências
npm install

# Configure as variáveis de ambiente
cp .env.example .env.local
# Edite .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Inicie o servidor de desenvolvimento
npm run dev
```

### Variáveis de Ambiente

#### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/voz_cidada
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
DEBUG=true
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

## 🚀 Deploy

Para fazer deploy gratuito do projeto, consulte o guia completo em [DEPLOY.md](./DEPLOY.md).

**Resumo rápido:**
- **Frontend**: Deploy no [Vercel](https://vercel.com) (gratuito)
- **Backend**: Deploy no [Render.com](https://render.com) (gratuito)
- PostgreSQL e Redis incluídos no free tier do Render

## 💻 Uso

### Acessando a Aplicação

1. **Landing Page**: http://localhost:3000
   - Apresentação do projeto
   - Cards de funcionalidades
   - Links para todas as páginas

2. **Dashboard**: http://localhost:3000/dashboard
   - Visualização de legislações
   - Filtros e busca
   - Estatísticas agregadas

3. **Emenda Pix**: http://localhost:3000/emenda-pix
   - Lista de emendas
   - Filtros por status, área, UF
   - Detalhes de cada emenda

4. **Placar de Transparência**: http://localhost:3000/placar-transparencia
   - Busca por município ou parlamentar
   - Estatísticas agregadas
   - Visualização de alertas

5. **Triangulação**: http://localhost:3000/triangulacao
   - Painel Integrado (cidadão)
   - Área Gabinete (parlamentar)
   - Área Executor (município)

6. **WhatsApp Simulator**: http://localhost:3000/whatsapp-simulator
   - Teste do bot WhatsApp
   - Consulta de legislações

### Funcionalidades Principais

#### Rastreamento de Emendas
- Visualize todas as emendas com filtros avançados
- Acompanhe valores (aprovado, empenhado, liquidado, pago)
- Veja progresso de execução em tempo real
- Receba alertas de anomalias detectadas pela IA

#### Triangulação de Dados
- **Fonte Portal**: Dados financeiros automáticos
- **Fonte Gabinete**: Input do parlamentar (objeto, justificativa)
- **Fonte Executor**: Prestação de contas física (fotos, relatório)
- **Trust Score**: Cálculo automático baseado nas 3 fontes

#### Análise com IA
- Categorização automática de gastos
- Extração de objeto principal e localização
- Detecção de anomalias cruzadas
- Geração de pareceres explicáveis

## 🧪 Testes

### Backend
```bash
cd backend
pytest
pytest --cov=src --cov-report=html
```

### Frontend
```bash
cd frontend
npm test
npm run test:coverage
npm run test:e2e
```

## 📁 Estrutura do Projeto

```
dev_impacto/
├── backend/                 # Backend Python/FastAPI
│   ├── src/
│   │   ├── domain/         # Domain Layer (DDD)
│   │   ├── application/    # Application Layer
│   │   ├── infrastructure/ # Infrastructure Layer
│   │   └── presentation/   # Presentation Layer
│   ├── tests/
│   └── requirements.txt
│
├── frontend/                # Frontend Next.js
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── features/      # Feature-based organization
│   │   ├── shared/        # Código compartilhado
│   │   └── core/          # Core functionality
│   ├── public/
│   └── package.json
│
├── docker-compose.yml      # Configuração Docker
└── README.md              # Este arquivo
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- Siga os princípios SOLID
- Escreva testes para novas features
- Mantenha cobertura de testes > 70%
- Use TypeScript strict mode
- Siga as convenções de nomenclatura do projeto

## 📝 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

### Licença MIT

```
MIT License

Copyright (c) 2025 Devs de Impacto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Agradecimentos

- Dados Abertos da Câmara dos Deputados
- Dados Abertos do Senado Federal
- Transferegov.br
- OpenStreetMap
- OpenAI
- Comunidade open source

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Desenvolvido com ❤️ pela equipe Devs de Impacto - Hackathon 2025**
