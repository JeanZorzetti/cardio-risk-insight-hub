# Sistema IA Médica - Análise de Risco Cardiovascular

Sistema completo de inteligência artificial para análise de risco cardiovascular, composto por:
- **Backend**: API REST em FastAPI com algoritmos de ML
- **Frontend**: Interface web em Next.js/React
- **Deploy**: Backend no EasyPanel (Docker) e Frontend no Vercel

## 🏗️ Arquitetura

```
├── backend/                    # API REST (FastAPI)
│   ├── main.py                # Aplicação principal
│   ├── requirements.txt       # Dependências Python
│   ├── Dockerfile            # Container Docker
│   └── docker-compose.yml    # Orquestração local
│
├── frontend/                  # Interface Web (Next.js)
│   ├── app/                  # App Router do Next.js 14
│   ├── components/           # Componentes React
│   ├── types/               # Tipos TypeScript
│   ├── utils/               # Utilitários (API calls)
│   ├── package.json         # Dependências Node.js
│   └── vercel.json          # Configuração Vercel
│
└── datasets/                 # Dados originais do projeto acadêmico
    ├── dataset_medico_ia.csv
    └── dataset_final_com_clusters.csv
```

## 🚀 Deploy Instructions

### Backend (EasyPanel)

1. **Preparar repositório:**
   ```bash
   cd backend
   git init
   git add .
   git commit -m "Initial backend commit"
   ```

2. **No EasyPanel:**
   - Criar novo serviço "Docker"
   - Conectar repositório Git
   - Configurar build path: `/backend`
   - Dockerfile path: `./Dockerfile`
   - Porta do container: `8000`
   - Variáveis de ambiente:
     ```
     PORT=8000
     ```

3. **Domain/SSL:**
   - Configurar domínio personalizado
   - Ativar SSL automático

### Frontend (Vercel)

1. **Preparar repositório:**
   ```bash
   cd frontend
   git init
   git add .
   git commit -m "Initial frontend commit"
   ```

2. **No Vercel:**
   - Importar repositório Git
   - Framework: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

3. **Variáveis de ambiente:**
   ```
   NEXT_PUBLIC_API_URL=https://seu-backend.easypanel.app
   ```

## 🛠️ Desenvolvimento Local

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker (Backend)
```bash
cd backend
docker build -t sistema-ia-medica-api .
docker run -p 8000:8000 sistema-ia-medica-api
```

## 📡 API Endpoints

- `GET /` - Informações da API
- `GET /health` - Health check
- `POST /predicao` - Predição simples
- `POST /analise-completa` - Análise completa com SHAP
- `GET /exemplo-paciente` - Dados de exemplo
- `GET /docs` - Documentação Swagger

## 🔧 Configurações de Produção

### Backend
- **CORS**: Configurado para domínios específicos
- **Validation**: Pydantic v2 para validação robusta
- **Error Handling**: Tratamento completo de erros
- **Health Checks**: Endpoint para monitoramento

### Frontend
- **TypeScript**: Tipagem completa
- **Form Validation**: React Hook Form
- **Charts**: Recharts para visualizações
- **Responsive**: Design mobile-first
- **Error Boundaries**: Tratamento de erros

## 🎯 Funcionalidades

### IA/ML
- ✅ Análise de risco cardiovascular
- ✅ Algoritmos de classificação (Naive Bayes, Random Forest)
- ✅ Explicabilidade SHAP
- ✅ Validação médica dos resultados
- ✅ Recomendações personalizadas

### Interface
- ✅ Formulário médico completo
- ✅ Visualizações interativas (gráficos)
- ✅ Dashboard de resultados
- ✅ Design responsivo
- ✅ Feedback em tempo real

## 🔒 Segurança

- Validação rigorosa de entrada
- CORS configurado adequadamente
- Sanitização de dados
- Rate limiting (recomendado para produção)
- HTTPS obrigatório em produção

## 📊 Monitoramento

### Health Checks
- Backend: `GET /health`
- Frontend: Vercel built-in monitoring

### Logs
- Backend: Uvicorn logs
- Frontend: Vercel function logs

## 🧪 Testes

### Testar API localmente:
```bash
curl http://localhost:8000/health
```

### Testar formulário:
Usar dados de exemplo disponíveis em `/exemplo-paciente`

## 📝 Notas de Deploy

1. **Backend primeiro**: Deploy do backend antes do frontend
2. **URLs**: Atualizar `NEXT_PUBLIC_API_URL` com URL real do backend
3. **CORS**: Adicionar domínio do frontend na lista de origins permitidas
4. **Certificados**: SSL automático em ambas as plataformas
5. **Scaling**: EasyPanel suporta auto-scaling, Vercel serverless por padrão

## 🎓 Contexto Acadêmico

Este projeto implementa conceitos de IA aplicada na medicina, incluindo:
- Geração de dados sintéticos realistas
- Pré-processamento de dados médicos
- Algoritmos de machine learning supervisionados e não-supervisionados
- Explicabilidade de modelos (SHAP)
- Interface profissional para uso médico

---

**Desenvolvido para fins acadêmicos - Sempre consulte profissionais de saúde qualificados**