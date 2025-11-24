# 🔗 VigiaPix - Transparência Radical

> O Portal da Transparência diz o valor. Nós mostramos a obra.

VigiaPix é uma plataforma inovadora que integra dados financeiros, políticos e físicos em um único "Trust Score" auditado por Inteligência Artificial, permitindo que cidadãos verifiquem se os recursos públicos das emendas parlamentares foram aplicados corretamente.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Problema](#problema)
- [Solução](#solução)
- [Tecnologias](#tecnologias)
- [Equipe](#equipe)
- [Instalação](#instalação)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Licença](#licença)

## 🎯 Sobre o Projeto

VigiaPix foi desenvolvido durante o **Hackathon Devs de Impacto 2025** com o objetivo de aumentar a transparência na aplicação de recursos públicos. O sistema integra três fontes de dados:

1. **Portal da Transparência** (Fonte Financeira) - Dados automáticos do SIAFI
2. **Gabinete Parlamentar** (Fonte Política) - Justificativas e objetos detalhados
3. **Executor** (Fonte Física) - Fotos, relatórios e progresso das obras

Através de Inteligência Artificial (OpenAI GPT), o sistema gera um **Trust Score** que avalia a integridade de cada emenda parlamentar.

## ❌ Problema

O sistema atual de transparência pública apresenta três grandes lacunas:

1. **Dados Isolados**: O Portal da Transparência mostra o PIX saindo, mas não conecta com a Nota Fiscal do município
2. **Objetos Genéricos**: "Custeio de Saúde" pode ser qualquer coisa. Sem detalhamento, não há fiscalização real
3. **Volume Impossível**: Humanos não conseguem auditar milhares de notas fiscais manualmente

## ✅ Solução: Triangulação

VigiaPix não substitui o Portal da Transparência. Ele o enriquece conectando duas novas pontas:

### Fonte 1: Portal (Financeiro)
- Valor empenhado
- Data de pagamento
- Deputado responsável
- Status no SIAFI

### Fonte 2: Gabinete (Político)
- Objeto detalhado da emenda
- Justificativa de impacto social
- Público-alvo beneficiado

### Fonte 3: Executor (Físico)
- Fotos georreferenciadas da obra
- Progresso físico (%)
- Relatórios de execução
- Notas fiscais

### Trust Score (IA)
O sistema utiliza **OpenAI GPT** para cruzar os três dados e gerar uma pontuação de 0 a 100, indicando o nível de confiança na aplicação correta dos recursos.

## 🛠️ Tecnologias

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **IA**: OpenAI GPT (simulado para demo)
- **Design**: Font Awesome Icons, Google Fonts (Inter)
- **Arquitetura**: Aplicação web estática (sem backend necessário para demo)

## 👥 Equipe

Este projeto foi desenvolvido pela equipe **VigiaPix** durante o Hackathon Devs de Impacto 2025:

- **Tech Lead / Backend Core**: Desenvolvimento da arquitetura e integrações
- **IA/ML Engineer**: Implementação de análise com IA e NLP
- **Frontend Lead**: Desenvolvimento da interface e componentes
- **Full Stack / DevOps**: Configuração de infraestrutura
- **Backend / Data Engineer**: Integração de dados e APIs externas

## 🚀 Instalação

### Pré-requisitos

- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Servidor web local (opcional, para desenvolvimento)

### Instalação Local

1. **Clone o repositório**:
```bash
git clone https://github.com/seu-usuario/vigiapix.git
cd vigiapix
```

2. **Abra o projeto**:

**Opção A - Servidor Local (Recomendado)**:
```bash
# Python 3
python -m http.server 8000

# Node.js
npx http-server

# PHP
php -S localhost:8000
```

**Opção B - Abrir Diretamente**:
- Abra `index.html` no navegador (algumas funcionalidades podem não funcionar devido a políticas CORS)

3. **Acesse no navegador**:
```
http://localhost:8000
```

## 📖 Uso

### Para Cidadãos

1. Acesse a página inicial (`index.html`)
2. Clique em **"Transparência Pública"** para conversar com o assistente IA
3. Clique em **"Acessar Sistema"** para ver o painel de monitoramento
4. Visualize as emendas parlamentares e seus Trust Scores
5. Clique em qualquer emenda para ver o dossiê completo

### Para Parlamentares

1. Acesse **"Área Gabinete"** no menu lateral
2. Selecione uma emenda do Portal da Transparência
3. Preencha o objeto detalhado e justificativa
4. O sistema calculará automaticamente o Trust Score

### Para Executores (Municípios)

1. Acesse **"Área Executor"** no menu lateral
2. Selecione uma emenda empenhada
3. Informe o progresso físico, fotos e relatório
4. O sistema atualizará o Trust Score com as evidências físicas

## 📁 Estrutura do Projeto

```
vigiapix/
├── index.html          # Landing page
├── app.html            # Aplicação principal
├── style.css           # Estilos globais
├── app.js              # Lógica da aplicação
├── openai.js           # Simulação de IA (OpenAI)
├── data.js             # Dados de exemplo
├── logo.jpeg           # Logo do projeto
└── README.md           # Este arquivo
```

## 🔧 Configuração

### Variáveis de Ambiente

Para produção, você precisará configurar:

- `OPENAI_API_KEY`: Chave da API OpenAI (para integração real)
- `DATABASE_URL`: URL do banco de dados (se houver backend)

**Nota**: A versão atual é uma demo com simulação de IA. Para integração real com OpenAI, é necessário implementar um backend.

## 🎨 Funcionalidades

- ✅ Painel de monitoramento unificado
- ✅ Trust Score calculado por IA
- ✅ Interface para parlamentares adicionarem justificativas
- ✅ Interface para executores enviarem evidências físicas
- ✅ Assistente de transparência pública (chat simulado)
- ✅ Visualização de dossiê completo por emenda
- ✅ Design responsivo e moderno

## 📝 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

### Código Aberto

Este é um projeto de código aberto desenvolvido para o Hackathon Devs de Impacto 2025. Contribuições são bem-vindas!

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Contato

Para dúvidas ou sugestões sobre o projeto, entre em contato através do assistente de transparência pública na página inicial.

---

**Desenvolvido com ❤️ pela equipe VigiaPix - Hackathon Devs de Impacto 2025**

