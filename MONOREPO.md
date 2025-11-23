# 📦 Monorepo - VigiaPix

## ✅ Sim, funciona perfeitamente!

Você pode colocar **backend e frontend no mesmo repositório** sem problemas. As configurações já estão preparadas para isso.

## 🏗️ Estrutura do Monorepo

```
dev_impacto/                    # Repositório único
├── backend/                    # Backend FastAPI
│   ├── src/
│   ├── requirements.txt
│   └── ...
├── frontend/                   # Frontend Next.js
│   ├── src/
│   ├── package.json
│   └── ...
├── render.yaml                 # Configuração Render (usa apenas backend/)
├── docker-compose.yml
└── README.md
```

## 🚀 Como Funciona o Deploy

### Render.com (Backend)
- **Configuração**: `render.yaml` na raiz com `rootDir: backend`
- **O que acontece**: Render olha apenas para `backend/`
- **Resultado**: Backend deployado corretamente, ignora `frontend/`

### Vercel (Frontend)
- **Configuração**: `Root Directory: frontend` (você configura no dashboard)
- **O que acontece**: Vercel olha apenas para `frontend/`
- **Resultado**: Frontend deployado corretamente, ignora `backend/`

## ✅ Vantagens do Monorepo

1. **Código unificado**: Tudo em um lugar
2. **Versionamento sincronizado**: Backend e frontend na mesma versão
3. **Facilita desenvolvimento**: Clone uma vez, tem tudo
4. **CI/CD simplificado**: Um repositório para gerenciar

## 📋 Checklist para Deploy

- [x] `render.yaml` na raiz com `rootDir: backend`
- [x] `frontend/vercel.json` configurado
- [x] `.gitignore` configurado para ignorar arquivos desnecessários
- [ ] Repositório no GitHub
- [ ] Deploy no Render (vai usar apenas `backend/`)
- [ ] Deploy no Vercel (configure `Root Directory: frontend`)

## 🎯 Resumo

**Não há problema algum em ter tudo no mesmo repositório!** Cada serviço de deploy vai olhar apenas para sua pasta específica. Isso é uma prática muito comum e recomendada para projetos full-stack.

---

**Desenvolvido com ❤️ pela equipe Devs de Impacto**

