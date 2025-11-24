# 🚀 Guia de Deploy - VigiaPix

Este guia mostra como fazer deploy gratuito do VigiaPix usando serviços gratuitos.

## 📋 Opções de Deploy Gratuito

### Recomendação: Vercel (Frontend) + Render.com (Backend)

- **Frontend (Next.js)**: [Vercel](https://vercel.com) - Free tier excelente, feito pela equipe do Next.js
- **Backend (FastAPI)**: [Render.com](https://render.com) - Free tier com PostgreSQL e Redis incluídos

### ✅ Monorepo (Repositório Único)

**Sim, você pode colocar backend e frontend no mesmo repositório!** As configurações já estão preparadas para isso:

- **Render.com**: Configurado com `rootDir: backend` - vai usar apenas a pasta `backend/`
- **Vercel**: Você configura `Root Directory: frontend` - vai usar apenas a pasta `frontend/`

Cada serviço de deploy vai olhar apenas para sua pasta específica, então não há problema em ter tudo no mesmo repositório. Na verdade, isso é muito comum e facilita o gerenciamento do projeto!

## 🎯 Deploy do Frontend (Vercel)

### Passo 1: Preparar o Repositório

1. Certifique-se de que seu código está no GitHub (pode ser um monorepo com backend e frontend juntos)
2. O arquivo `frontend/vercel.json` já está configurado
3. **Importante**: Mesmo que backend e frontend estejam no mesmo repositório, o Vercel vai usar apenas a pasta `frontend/`

### Passo 2: Deploy no Vercel

1. Acesse [vercel.com](https://vercel.com)
2. Faça login com GitHub
3. Clique em "Add New Project"
4. Importe seu repositório
5. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (automático)
   - **Output Directory**: `.next` (automático)
   - **Install Command**: `npm install` (automático)

### Passo 3: Variáveis de Ambiente

No Vercel, vá em "Settings" → "Environment Variables" e adicione:

```
NEXT_PUBLIC_API_URL=https://vigiapix-backend.onrender.com
NEXT_PUBLIC_ENVIRONMENT=production
```

**Importante**: 
- Substitua `vigiapix-backend.onrender.com` pela URL real do seu backend no Render
- A URL será algo como `https://vigiapix-backend-xxxx.onrender.com`
- Você obterá essa URL após fazer o deploy do backend no Render

### Passo 4: Deploy

1. Clique em "Deploy"
2. Aguarde o build (2-3 minutos)
3. Seu frontend estará disponível em `https://seu-projeto.vercel.app`

## 🔧 Deploy do Backend (Render.com)

### 📊 Diferença: Docker Local vs Render

| Aspecto | Docker Local | Render (Produção) |
|---------|--------------|-------------------|
| **PostgreSQL** | Container Docker (`postgres:14-alpine`) | Serviço gerenciado (criar manualmente) |
| **Redis** | Container Docker (`redis:7-alpine`) | Serviço gerenciado (criado pelo `render.yaml`) |
| **Connection String** | `postgresql+asyncpg://postgres:postgres@postgres:5432/vigiapix` | Fornecida pelo Render (formato diferente) |
| **Configuração** | Automática via `docker-compose.yml` | Manual no Render Dashboard |
| **Banco de Dados** | Criado automaticamente | **Você precisa criar manualmente** (free tier = 1 banco) |

### 📊 Diferença: Docker Local vs Render

**Localmente (Docker Compose):**
- PostgreSQL e Redis rodam em containers Docker
- Connection string: `postgresql+asyncpg://postgres:postgres@postgres:5432/vigiapix`
- Tudo configurado automaticamente no `docker-compose.yml`

**No Render (Produção):**
- PostgreSQL e Redis são serviços gerenciados pelo Render
- Você precisa criar o banco manualmente (free tier permite apenas 1)
- Connection string vem do Render (formato diferente)
- Redis é criado automaticamente pelo `render.yaml`

### Passo 1: Configurar Banco de Dados PostgreSQL no Render

**⚠️ IMPORTANTE**: O Render free tier permite apenas **1 banco PostgreSQL ativo**. 

#### Opção A: Você JÁ TEM um banco PostgreSQL no Render (Recomendado)

1. Acesse [render.com](https://render.com) e faça login
2. No Dashboard, procure por **"PostgreSQL"** na lista de serviços
3. Clique no banco de dados existente
4. Vá na aba **"Connections"** ou **"Info"**
5. **Copie a Connection String** (Internal Database URL ou Connection String)
   - Você verá algo como: `postgres://usuario:senha@host:5432/database`
   - **IMPORTANTE**: Adicione `+asyncpg` após `postgresql`:
     - De: `postgres://...`
     - Para: `postgresql+asyncpg://...`
   - Exemplo completo: `postgresql+asyncpg://usuario:senha@dpg-xxxxx-a.oregon-postgres.render.com:5432/database`
6. **Pule para o Passo 2** (não precisa criar novo banco)

#### Opção B: Você NÃO TEM banco ou quer criar um novo

**⚠️ ATENÇÃO**: Se você já tem um banco, você precisa:
- **Deletar o banco antigo primeiro** (você perderá todos os dados!)
- Ou usar o banco existente (Opção A acima)

**Se decidir criar um novo:**

1. Acesse [render.com](https://render.com) e faça login
2. Se você já tem um banco:
   - Vá no banco existente → **"Settings"** → **"Delete"**
   - ⚠️ **CUIDADO**: Isso apagará todos os dados permanentemente!
3. Clique em **"New +"** → **"PostgreSQL"**
4. Configure:
   - **Name**: `vigiapix-db` (ou qualquer nome)
   - **Database**: `vigiapix`
   - **User**: Deixe o padrão ou escolha um nome
   - **Region**: `Oregon` (ou a região que você escolher)
   - **Plan**: `Free`
5. Clique em **"Create Database"**
6. Aguarde alguns minutos até o banco estar pronto
7. **Copie a Connection String**:
   - No dashboard do banco, vá em **"Connections"**
   - Você verá algo como: `postgres://usuario:senha@host:5432/database`
   - **IMPORTANTE**: Adicione `+asyncpg` após `postgresql`:
     - De: `postgres://...`
     - Para: `postgresql+asyncpg://...`
   - Exemplo completo: `postgresql+asyncpg://usuario:senha@dpg-xxxxx-a.oregon-postgres.render.com:5432/vigiapix`

### Passo 2: Preparar o Repositório

1. Certifique-se de que o arquivo `render.yaml` está na raiz do projeto
2. O arquivo já está configurado para Redis (criado automaticamente)
3. **Importante**: O `render.yaml` tem `rootDir: backend`, então o Render vai usar apenas a pasta `backend/`

### Passo 3: Deploy no Render

1. Acesse [render.com](https://render.com)
2. Clique em **"New +"** → **"Blueprint"**
3. Conecte seu repositório GitHub
4. Render detectará automaticamente o `render.yaml` na raiz
5. Render criará automaticamente:
   - Web Service (backend FastAPI)
   - Redis Instance
   - **NÃO criará PostgreSQL** (você já criou manualmente)

### Passo 4: Configurar Variáveis de Ambiente

No Render Dashboard, no serviço `vigiapix-backend`, vá em **"Environment"** e adicione:

```
OPENAI_API_KEY=sk-sua-chave-aqui
DATABASE_URL=postgresql+asyncpg://usuario:senha@host:porta/database
```

**Onde obter cada valor:**
- **OPENAI_API_KEY**: Obtenha em [platform.openai.com](https://platform.openai.com)
- **DATABASE_URL**: Use a connection string que você copiou no Passo 1 (com `+asyncpg`)

**⚠️ Formato da DATABASE_URL:**
- Deve começar com `postgresql+asyncpg://` (não apenas `postgres://`)
- Exemplo: `postgresql+asyncpg://vigiapix_user:senha123@dpg-xxxxx-a.oregon-postgres.render.com:5432/vigiapix`

### Passo 4: Deploy

1. Clique em "Apply" para iniciar o deploy
2. Aguarde o deploy (5-10 minutos)
   - O build pode demorar na primeira vez
   - Render instalará todas as dependências Python
3. Seu backend estará disponível em `https://vigiapix-backend-xxxx.onrender.com`
   - A URL exata será mostrada no dashboard do Render

### Passo 5: Atualizar Frontend

Após obter a URL do backend, atualize a variável `NEXT_PUBLIC_API_URL` no Vercel com a URL real do Render.

## 🔄 Alternativa: Railway.app

Se preferir usar Railway para o backend:

### Backend no Railway

1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Selecione seu repositório
5. Railway detectará automaticamente o Python
6. Configure:
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
7. Adicione PostgreSQL e Redis como plugins
8. Configure as variáveis de ambiente

## 📝 Variáveis de Ambiente Necessárias

### Backend (Render/Railway)

```env
DATABASE_URL=postgresql+asyncpg://... (fornecido automaticamente)
REDIS_URL=redis://... (fornecido automaticamente)
OPENAI_API_KEY=sk-... (você precisa fornecer)
ENVIRONMENT=production
DEBUG=false
PORT=8000 (ou $PORT fornecido pelo serviço)
```

### Frontend (Vercel)

```env
NEXT_PUBLIC_API_URL=https://seu-backend.onrender.com
NEXT_PUBLIC_ENVIRONMENT=production
```

## ⚠️ Limitações do Free Tier

### Vercel (Frontend)
- ✅ 100GB bandwidth/mês
- ✅ Deploys ilimitados
- ✅ SSL automático
- ⚠️ Sleep após 30 dias de inatividade (Hobby plan)

### Render.com (Backend)
- ✅ 750 horas/mês (suficiente para 24/7)
- ✅ PostgreSQL e Redis gratuitos
- ⚠️ **Apenas 1 banco PostgreSQL free tier por conta** (se já tiver um, use o existente)
- ⚠️ Sleep após 15 minutos de inatividade (pode ser acordado com requisição)
- ⚠️ Builds podem levar 5-10 minutos

### Railway.app (Alternativa)
- ✅ $5 crédito/mês (free tier)
- ✅ Sem sleep automático
- ⚠️ Créditos limitados

## 🚀 Deploy Rápido (Script)

Crie um script para facilitar:

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Iniciando deploy do VigiaPix..."

# 1. Verificar se está no diretório correto
if [ ! -f "render.yaml" ]; then
    echo "❌ Erro: render.yaml não encontrado. Execute na raiz do projeto."
    exit 1
fi

# 2. Verificar variáveis de ambiente
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Aviso: OPENAI_API_KEY não definida. Configure no Render Dashboard."
fi

echo "✅ Pronto para deploy!"
echo ""
echo "📋 Próximos passos:"
echo "1. Frontend: Vercel → Importar repositório → Root: frontend"
echo "2. Backend: Render → New Blueprint → Conectar repositório"
echo "3. Configure OPENAI_API_KEY no Render Dashboard"
echo "4. Atualize NEXT_PUBLIC_API_URL no Vercel com a URL do Render"
```

## 🔍 Verificação Pós-Deploy

### Testar Backend

```bash
curl https://seu-backend.onrender.com/api/v1/health
```

### Testar Frontend

1. Acesse `https://seu-projeto.vercel.app`
2. Verifique se a página carrega
3. Teste uma requisição ao backend

## 🐛 Troubleshooting

### Backend não inicia
- Verifique os logs no Render Dashboard
- Confirme que `DATABASE_URL` e `REDIS_URL` estão configurados
- Verifique se `OPENAI_API_KEY` está definida

### Erro de conexão com banco de dados
- **Verifique o formato da DATABASE_URL**: Deve começar com `postgresql+asyncpg://` (não `postgres://`)
- **Exemplo correto**: `postgresql+asyncpg://user:pass@host:5432/dbname`
- **Exemplo errado**: `postgres://user:pass@host:5432/dbname` ❌
- Confirme que o banco PostgreSQL está rodando no Render Dashboard
- Verifique se a connection string foi copiada corretamente (sem espaços extras)
- Se o banco está em sleep, faça uma requisição ou aguarde alguns segundos

### Frontend não conecta ao backend
- Verifique `NEXT_PUBLIC_API_URL` no Vercel
- Confirme que o backend está rodando (não em sleep)
- Verifique CORS no backend (já configurado)

### Erro de build
- Verifique os logs de build
- Confirme que todas as dependências estão em `requirements.txt` e `package.json`
- Verifique se o Python/Node.js está na versão correta

### "Cannot have more than one active free tier database"

**Erro**: `Error: cannot have more than one active free tier database`

**Causa**: Você já tem um banco PostgreSQL ativo no Render. O free tier permite apenas 1 banco.

**Soluções**:

#### ✅ Solução 1: Usar o banco existente (Recomendado)

1. No Render Dashboard, encontre seu banco PostgreSQL existente
2. Clique nele para abrir os detalhes
3. Vá em **"Connections"** ou **"Info"**
4. Copie a **Internal Database URL** ou **Connection String**
5. Converta para o formato correto:
   - Se começa com `postgres://`, mude para `postgresql+asyncpg://`
   - Exemplo: `postgres://user:pass@host:5432/db` → `postgresql+asyncpg://user:pass@host:5432/db`
6. Use essa connection string no `DATABASE_URL` do seu serviço backend

#### ⚠️ Solução 2: Deletar banco antigo (Cuidado!)

**ATENÇÃO**: Isso apagará todos os dados permanentemente!

1. No Render Dashboard, vá no banco PostgreSQL antigo
2. Clique em **"Settings"** → Role até o final
3. Clique em **"Delete Database"**
4. Confirme a exclusão
5. Aguarde alguns minutos
6. Agora você pode criar um novo banco seguindo o Passo 1 (Opção B)

**Quando usar cada solução:**
- **Use Solução 1** se o banco antigo não tem dados importantes ou você quer reutilizá-lo
- **Use Solução 2** apenas se você realmente precisa de um banco novo e não se importa em perder os dados do banco antigo

## 📚 Recursos

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

---

**Desenvolvido com ❤️ pela equipe Devs de Impacto**

