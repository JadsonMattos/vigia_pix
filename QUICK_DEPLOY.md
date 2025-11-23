# ⚡ Deploy Rápido - VigiaPix

## 🚀 Deploy em 5 minutos

### 1️⃣ Backend no Render.com (3 minutos)

1. Acesse [render.com](https://render.com) e faça login com GitHub
2. Clique em "New +" → "Blueprint"
3. Conecte seu repositório
4. Render detectará `render.yaml` automaticamente
5. Adicione variável de ambiente:
   - `OPENAI_API_KEY` (opcional - sistema funciona sem ela)
6. Clique em "Apply" e aguarde o deploy

**URL do backend**: `https://vigiapix-backend-xxxx.onrender.com`

### 2️⃣ Frontend no Vercel (2 minutos)

1. Acesse [vercel.com](https://vercel.com) e faça login com GitHub
2. Clique em "Add New Project"
3. Importe seu repositório
4. Configure:
   - **Root Directory**: `frontend` ⚠️ IMPORTANTE
5. Adicione variável de ambiente:
   - `NEXT_PUBLIC_API_URL` = URL do backend do Render
6. Clique em "Deploy"

**URL do frontend**: `https://seu-projeto.vercel.app`

## ✅ Pronto!

Seu VigiaPix estará no ar e acessível publicamente!

## 📖 Guia completo

Para mais detalhes, consulte [DEPLOY.md](./DEPLOY.md)
