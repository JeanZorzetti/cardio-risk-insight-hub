# 🏥 CardioCare AI - Análise de Risco Cardiovascular

Sistema completo de inteligência artificial para análise de risco cardiovascular, desenvolvido com React + FastAPI.

## 🚀 Funcionalidades

- **🤖 IA Explicável**: Análise de risco com explicações SHAP detalhadas
- **📊 Visualizações Interativas**: Gráficos e métricas em tempo real
- **🩺 Precisão Médica**: Baseado em diretrizes cardiológicas validadas
- **📱 Interface Moderna**: Design responsivo com Shadcn/ui
- **🔒 API Robusta**: Backend FastAPI com validação Pydantic

## 🏗️ Arquitetura

```
├── src/                          # Frontend React + Vite
│   ├── components/medical/       # Componentes médicos específicos
│   ├── hooks/useMedicalAPI.ts    # Hook para comunicação com API
│   └── pages/Index.tsx           # Página principal
│
└── backend/                      # API FastAPI
    ├── main.py                   # Aplicação principal
    ├── requirements.txt          # Dependências Python
    └── Dockerfile                # Container para deploy
```

## 🛠️ Desenvolvimento Local

### Frontend
```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

### Backend (API)
```bash
# Navegar para pasta backend
cd backend

# Instalar dependências Python
pip install -r requirements.txt

# Iniciar API
uvicorn main:app --reload
```

### Configuração de Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar variáveis necessárias
VITE_API_URL=http://localhost:8000
```

## 🚀 Deploy em Produção

### Backend (EasyPanel)
1. **Criar novo serviço Docker no EasyPanel**
2. **Configurar build:**
   - Build Context: `./backend`
   - Dockerfile Path: `./Dockerfile`
   - Port: `8000`
3. **Deploy automático via Git**

### Frontend (Vercel)
1. **Conectar repositório no Vercel**
2. **Configurar variáveis de ambiente:**
   ```
   VITE_API_URL=https://cardioapi.roilabs.com.br
   NEXT_PUBLIC_API_URL=https://cardioapi.roilabs.com.br
   ```
3. **Configurar domínio personalizado**: `cardiorisk.roilabs.com.br`
4. **Deploy automático**

## 📡 API Endpoints

- `GET /` - Informações da API
- `GET /health` - Health check
- `POST /analise-completa` - Análise completa com SHAP
- `GET /exemplo-paciente` - Dados de exemplo para testes
- `GET /docs` - Documentação interativa (Swagger)

## 🧪 Testando a Aplicação

### Dados de Exemplo
A API fornece três perfis de teste:
- **Baixo Risco**: Paciente jovem, pressão normal
- **Médio Risco**: Fatores de risco moderados
- **Alto Risco**: Múltiplos fatores de risco

### Fluxo de Teste
1. Acesse a aplicação
2. Preencha o formulário com dados do paciente
3. Visualize análise de risco com explicações SHAP
4. Consulte recomendações médicas personalizadas

## 🎯 Tecnologias Utilizadas

### Frontend
- **React 18** + **TypeScript**
- **Vite** (build tool)
- **Shadcn/ui** + **Tailwind CSS**
- **React Hook Form** (formulários)
- **Recharts** (visualizações)
- **Tanstack Query** (gerenciamento de estado)

### Backend
- **FastAPI** (Python web framework)
- **Pydantic v2** (validação de dados)
- **Uvicorn** (servidor ASGI)
- **NumPy/Pandas** (processamento de dados)

## 🔒 Segurança e Validação

- ✅ Validação rigorosa de entrada com Pydantic
- ✅ CORS configurado para domínios específicos
- ✅ Sanitização automática de dados
- ✅ Type safety completo com TypeScript
- ✅ Error boundaries no React

## 📊 Monitoramento

### Health Checks
- Frontend: Vercel built-in monitoring
- Backend: Endpoint `/health` para verificação

### Logs e Debugging
- Backend: Uvicorn structured logs
- Frontend: Error boundaries + console logs

## 🎓 Contexto Acadêmico

Este projeto implementa conceitos avançados de IA aplicada na medicina:

- **Geração de dados sintéticos** realistas
- **Algoritmos de Machine Learning** supervisionados
- **Explicabilidade de modelos** com técnicas SHAP
- **Interface profissional** para uso médico
- **Arquitetura de microserviços** moderna

## ⚠️ Aviso Médico

**Importante**: Este sistema é uma ferramenta de apoio à decisão médica desenvolvida para fins acadêmicos. Os resultados devem sempre ser interpretados por profissionais de saúde qualificados e não substituem o julgamento clínico ou exames complementares.

## 🤝 Contribuindo

1. Fork do projeto
2. Criar feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -m 'Adicionar nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abrir Pull Request

## 🌐 URLs de Produção

### Aplicação em Funcionamento
- **Frontend**: https://cardiorisk.roilabs.com.br
- **Backend API**: https://cardioapi.roilabs.com.br
- **Documentação API**: https://cardioapi.roilabs.com.br/docs

### Repositório
- **GitHub**: https://github.com/JeanZorzetti/cardio-risk-insight-hub

## 📝 Licença

Este projeto é desenvolvido para fins acadêmicos e de pesquisa.

---

**Desenvolvido com ❤️ para auxiliar profissionais de saúde na tomada de decisões informadas**
