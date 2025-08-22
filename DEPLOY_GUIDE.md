# 🚀 Guia de Deploy - Sistema IA Médica

## 📋 Pré-requisitos

- Conta no [EasyPanel](https://easypanel.io) (para backend)
- Conta no [Vercel](https://vercel.com) (para frontend)
- Git instalado
- Contas no GitHub/GitLab (para repositórios)

## 🎯 Passo a Passo Completo

### 1️⃣ Preparar Repositórios

#### Backend Repository
```bash
# Navegar para pasta backend
cd backend

# Inicializar git
git init

# Adicionar arquivos
git add .

# Primeiro commit
git commit -m "🚀 Initial backend setup for EasyPanel deploy"

# Conectar com repositório remoto (GitHub/GitLab)
git remote add origin https://github.com/seu-usuario/sistema-ia-medica-backend.git
git push -u origin main
```

#### Frontend Repository  
```bash
# Navegar para pasta frontend
cd frontend

# Inicializar git
git init

# Adicionar arquivos
git add .

# Primeiro commit
git commit -m "🚀 Initial frontend setup for Vercel deploy"

# Conectar com repositório remoto
git remote add origin https://github.com/seu-usuario/sistema-ia-medica-frontend.git
git push -u origin main
```

### 2️⃣ Deploy Backend (EasyPanel)

#### A. Acessar EasyPanel
1. Login em [easypanel.io](https://easypanel.io)
2. Criar novo projeto ou usar existente

#### B. Criar Serviço Docker
1. **Criar novo serviço** → Selecionar "**Docker**"
2. **Nome**: `sistema-ia-medica-api`
3. **Repositório Git**: URL do seu repositório backend
4. **Branch**: `main`

#### C. Configurações do Build
```
Build Context: .
Dockerfile Path: ./Dockerfile
```

#### D. Configurações do Runtime
```
Container Port: 8000
```

#### E. Variáveis de Ambiente
```
PORT=8000
```

#### F. Deploy
1. Clicar "**Deploy**"
2. Aguardar build (2-5 minutos)
3. Anotar URL gerada (ex: `https://sistema-ia-medica-api.easypanel.app`)

#### G. Testar Backend
```bash
# Testar health check
curl https://sua-url-backend.easypanel.app/health

# Deve retornar:
{
  "status": "healthy",
  "timestamp": "2024-...",
  "version": "1.0.3",
  "environment": "production",
  "modelo_ia": "Carregado e funcional"
}
```

### 3️⃣ Deploy Frontend (Vercel)

#### A. Acessar Vercel
1. Login em [vercel.com](https://vercel.com)
2. Dashboard principal

#### B. Importar Projeto
1. **"Add New Project"** → **"Import Git Repository"**
2. Conectar GitHub/GitLab se necessário
3. Selecionar repositório frontend

#### C. Configurações do Projeto
```
Framework Preset: Next.js
Root Directory: . (deixar vazio se frontend está na raiz)
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

#### D. Variáveis de Ambiente
```
NEXT_PUBLIC_API_URL = https://sua-url-backend.easypanel.app
```

#### E. Deploy
1. Clicar "**Deploy**"
2. Aguardar build (2-4 minutos)
3. Anotar URL gerada (ex: `https://sistema-ia-medica.vercel.app`)

### 4️⃣ Configurar CORS (IMPORTANTE!)

#### No arquivo backend/main.py, atualizar:
```python
# CORS configurado para producao
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://*.vercel.app",
    "https://sistema-ia-medica.vercel.app",  # Sua URL real do Vercel
    "https://seu-dominio-personalizado.com"  # Se tiver domínio próprio
]
```

#### Fazer push das alterações:
```bash
cd backend
git add .
git commit -m "🔧 Update CORS for production frontend URL"
git push
```

EasyPanel fará redeploy automático.

### 5️⃣ Testes Finais

#### A. Testar Backend
```bash
# Health check
curl https://sua-url-backend.easypanel.app/health

# Documentação API
# Abrir no navegador: https://sua-url-backend.easypanel.app/docs
```

#### B. Testar Frontend
1. Abrir URL do Vercel no navegador
2. Preencher formulário com dados de teste
3. Verificar se análise funciona

#### C. Testar Integração
1. No frontend, usar dados de exemplo
2. Verificar se chamadas API funcionam
3. Confirmar visualização de resultados

## 🔧 Configurações Avançadas

### Custom Domain (Opcional)

#### EasyPanel (Backend)
1. **Settings** → **Domains**
2. Adicionar domínio personalizado
3. Configurar DNS: `CNAME api.seudominio.com → seu-app.easypanel.app`
4. SSL automático ativado

#### Vercel (Frontend)  
1. **Project Settings** → **Domains**
2. Adicionar domínio personalizado
3. Configurar DNS conforme instruções Vercel
4. SSL automático ativado

### Monitoring

#### Backend (EasyPanel)
- **Logs**: Seção "Logs" no dashboard
- **Metrics**: CPU, RAM, Network usage
- **Health Checks**: Configurar alertas

#### Frontend (Vercel)
- **Analytics**: Vercel Analytics (grátis)
- **Function Logs**: Para debugging
- **Performance**: Core Web Vitals

## 🐛 Troubleshooting

### Backend não inicia
```bash
# Verificar logs no EasyPanel
# Problemas comuns:
# 1. requirements.txt - dependências faltando
# 2. Port binding - verificar se está usando PORT env var
# 3. Dockerfile syntax
```

### Frontend não conecta com Backend
```bash
# 1. Verificar NEXT_PUBLIC_API_URL
# 2. Verificar CORS no backend
# 3. Network tab no DevTools do browser
```

### CORS Errors
```python
# No backend, verificar:
ALLOWED_ORIGINS = [
    "https://seu-frontend.vercel.app"  # URL exata do frontend
]
```

## 📱 URLs Finais

Após deploy bem-sucedido, você terá:

- **Backend API**: `https://sistema-ia-medica-api.easypanel.app`
- **Frontend**: `https://sistema-ia-medica.vercel.app`
- **API Docs**: `https://sistema-ia-medica-api.easypanel.app/docs`

## 💡 Próximos Passos

1. **Domínios personalizados** (api.seudominio.com, app.seudominio.com)
2. **Monitoring avançado** (Sentry, LogRocket)
3. **CI/CD Pipeline** (GitHub Actions)
4. **Backup de dados** (se implementar banco de dados)
5. **Rate limiting** para API
6. **Cache strategies** (Redis)

---

🎉 **Deploy concluído com sucesso!** 

Seu sistema de IA médica está agora rodando em produção com infraestrutura profissional.