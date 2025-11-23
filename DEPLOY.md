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

### Passo 1: Preparar o Repositório

1. Certifique-se de que o arquivo `render.yaml` está na raiz do projeto (mesmo que seja um monorepo)
2. O arquivo já está configurado para PostgreSQL e Redis gratuitos
3. **Importante**: O `render.yaml` tem `rootDir: backend`, então o Render vai usar apenas a pasta `backend/` do repositório

### Passo 2: Deploy no Render

1. Acesse [render.com](https://render.com)
2. Faça login com GitHub
3. Clique em "New +" → "Blueprint"
4. Conecte seu repositório GitHub
5. Render detectará automaticamente o `render.yaml` na raiz
6. Render criará automaticamente:
   - Web Service (backend FastAPI)
   - PostgreSQL Database
   - Redis Instance

### Passo 3: Configurar Variáveis de Ambiente

No Render Dashboard, vá em "Environment" e adicione:

```
OPENAI_API_KEY=sk-sua-chave-aqui
```

**Importante**: Você precisa de uma chave da OpenAI. Obtenha em [platform.openai.com](https://platform.openai.com)

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

### Frontend não conecta ao backend
- Verifique `NEXT_PUBLIC_API_URL` no Vercel
- Confirme que o backend está rodando (não em sleep)
- Verifique CORS no backend (já configurado)

### Erro de build
- Verifique os logs de build
- Confirme que todas as dependências estão em `requirements.txt` e `package.json`
- Verifique se o Python/Node.js está na versão correta

## 📚 Recursos

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

---

**Desenvolvido com ❤️ pela equipe Devs de Impacto**

