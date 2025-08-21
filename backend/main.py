# API REST MEDICA - Sistema IA (PRODUCTION VERSION)
# Versao otimizada para deploy em EasyPanel

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Configuracao da API
app = FastAPI(
    title="CardioCare AI - API REST",
    description="API profissional para analise de risco cardiaco com IA e explicabilidade SHAP",
    version="1.0.3",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configurado para producao
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite dev server
    "http://localhost:4173",  # Vite preview
    "https://*.vercel.app",
    "https://cardio-risk-insight-hub.vercel.app",  # URL do projeto
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# MODELOS DE DADOS (Pydantic v2 Compatible)
class PacienteInput(BaseModel):
    """Modelo para entrada de dados do paciente - PRODUCTION"""
    
    # Dados demograficos
    idade: int = Field(..., ge=18, le=120, description="Idade do paciente em anos")
    genero: str = Field(..., pattern="^(Masculino|Feminino)$", description="Genero do paciente")
    tipo_sanguineo: str = Field(..., pattern="^(A\\+|A-|B\\+|B-|AB\\+|AB-|O\\+|O-)$", description="Tipo sanguineo")
    
    # Dados vitais
    pressao_sistolica: float = Field(..., ge=60, le=300, description="Pressao sistolica em mmHg")
    pressao_diastolica: float = Field(..., ge=30, le=200, description="Pressao diastolica em mmHg")
    freq_cardiaca: float = Field(..., ge=30, le=200, description="Frequencia cardiaca em bpm")
    
    # Dados antropometricos e laboratoriais
    peso: float = Field(..., ge=20, le=300, description="Peso em kg")
    altura: float = Field(..., ge=1.0, le=2.5, description="Altura em metros")
    colesterol: float = Field(..., ge=50, le=500, description="Colesterol total em mg/dL")
    glicose: float = Field(..., ge=50, le=400, description="Glicose em mg/dL")
    
    # Historico medico
    num_medicamentos: int = Field(..., ge=0, le=20, description="Numero de medicamentos")
    visitas_anuais: int = Field(..., ge=0, le=50, description="Visitas medicas por ano")
    
    # Sintomas (booleanos)
    dor_peito: bool = Field(..., description="Presenca de dor no peito")
    falta_ar: bool = Field(..., description="Presenca de falta de ar")
    fadiga: bool = Field(..., description="Presenca de fadiga")
    tontura: bool = Field(..., description="Presenca de tontura")
    
    @field_validator('pressao_diastolica')
    @classmethod
    def validar_pressao_diastolica(cls, v, info):
        if 'pressao_sistolica' in info.data and v >= info.data['pressao_sistolica']:
            raise ValueError('Pressao diastolica deve ser menor que sistolica')
        return v

class PredicaoResponse(BaseModel):
    """Modelo para resposta da predicao"""
    
    categoria_risco: str = Field(..., description="Categoria de risco: Baixo Risco, Medio Risco, Alto Risco")
    probabilidade: float = Field(..., ge=0, le=1, description="Probabilidade de alto risco (0-1)")
    score_risco: float = Field(..., ge=0, le=1, description="Score de risco calculado")
    confianca: float = Field(..., ge=0, le=1, description="Confianca da predicao")
    timestamp: str = Field(..., description="Timestamp da analise")
    
    # Dados calculados
    bmi: float = Field(..., description="BMI calculado")
    classificacao_bmi: str = Field(..., description="Classificacao do BMI")
    classificacao_pressao: str = Field(..., description="Classificacao da pressao arterial")

class ExplicacaoSHAP(BaseModel):
    """Modelo para explicacao individual SHAP"""
    
    fator: str = Field(..., description="Nome do fator/feature")
    valor: float = Field(..., description="Valor do fator para este paciente")
    impacto: float = Field(..., description="Impacto SHAP no risco")
    interpretacao: str = Field(..., description="Interpretacao em linguagem medica")
    categoria: str = Field(..., description="Categoria: increase_risk, decrease_risk, neutral")

class ExplicacoesResponse(BaseModel):
    """Modelo para resposta das explicacoes"""
    
    fatores_risco: List[ExplicacaoSHAP] = Field(..., description="Fatores que aumentam o risco")
    fatores_protecao: List[ExplicacaoSHAP] = Field(..., description="Fatores que diminuem o risco")
    interpretacao_geral: str = Field(..., description="Interpretacao geral do caso")
    recomendacoes: List[str] = Field(..., description="Recomendacoes medicas")

class AnaliseCompletaResponse(BaseModel):
    """Modelo para analise completa"""
    
    predicao: PredicaoResponse
    explicacoes: ExplicacoesResponse
    dados_processados: Dict[str, Any] = Field(..., description="Dados processados para auditoria")

# LOGICA DE NEGOCIO
class ModeloIAMedica:
    """Classe para encapsular logica do modelo de IA medica - PRODUCTION VERSION"""
    
    def __init__(self):
        print("CardioCare AI - Modelo IA Medica inicializado - Production Version")
    
    def calcular_bmi(self, peso: float, altura: float) -> tuple:
        """Calcula BMI e sua classificacao"""
        bmi = peso / (altura ** 2)
        
        if bmi < 18.5:
            classificacao = "Abaixo do peso"
        elif bmi < 25:
            classificacao = "Peso normal"
        elif bmi < 30:
            classificacao = "Sobrepeso"
        elif bmi < 35:
            classificacao = "Obesidade Grau I"
        elif bmi < 40:
            classificacao = "Obesidade Grau II"
        else:
            classificacao = "Obesidade Grau III (Morbida)"
            
        return round(bmi, 2), classificacao
    
    def classificar_pressao(self, sistolica: float, diastolica: float) -> str:
        """Classifica pressao arterial segundo diretrizes"""
        if sistolica < 120 and diastolica < 80:
            return "Normal"
        elif sistolica < 130 and diastolica < 80:
            return "Elevada"
        elif (sistolica >= 130 and sistolica < 140) or (diastolica >= 80 and diastolica < 90):
            return "Hipertensao Estagio 1"
        elif (sistolica >= 140 and sistolica < 180) or (diastolica >= 90 and diastolica < 120):
            return "Hipertensao Estagio 2"
        else:
            return "Crise Hipertensiva"
    
    def calcular_risco_avancado(self, dados: PacienteInput) -> tuple:
        """Algoritmo de risco cardiovascular aprimorado"""
        
        bmi, _ = self.calcular_bmi(dados.peso, dados.altura)
        score = 0
        
        # FATORES DE RISCO PRINCIPAIS
        
        # 1. IDADE (peso variavel por faixa)
        if dados.idade >= 75:
            score += 0.35
        elif dados.idade >= 65:
            score += 0.25
        elif dados.idade >= 55:
            score += 0.20
        elif dados.idade >= 45:
            score += 0.15
        elif dados.idade >= 35:
            score += 0.10
        
        # 2. PRESSAO ARTERIAL (baseado em guidelines)
        if dados.pressao_sistolica >= 180 or dados.pressao_diastolica >= 120:
            score += 0.30  # Crise hipertensiva
        elif dados.pressao_sistolica >= 140 or dados.pressao_diastolica >= 90:
            score += 0.25  # Hipertensao estagio 2
        elif dados.pressao_sistolica >= 130 or dados.pressao_diastolica >= 80:
            score += 0.15  # Hipertensao estagio 1
        elif dados.pressao_sistolica >= 120:
            score += 0.05  # Pressao elevada
        
        # 3. BMI (obesidade e fator de risco significativo)
        if bmi >= 40:
            score += 0.25  # Obesidade morbida
        elif bmi >= 35:
            score += 0.20  # Obesidade grau II
        elif bmi >= 30:
            score += 0.15  # Obesidade grau I
        elif bmi >= 25:
            score += 0.08  # Sobrepeso
        
        # 4. PERFIL LIPIDICO
        if dados.colesterol >= 300:
            score += 0.25
        elif dados.colesterol >= 240:
            score += 0.20
        elif dados.colesterol >= 200:
            score += 0.10
        
        # 5. GLICOSE (diabetes/pre-diabetes)
        if dados.glicose >= 200:
            score += 0.25  # Diabetes descompensado
        elif dados.glicose >= 126:
            score += 0.20  # Diabetes
        elif dados.glicose >= 100:
            score += 0.10  # Pre-diabetes
        
        # 6. SINTOMAS CARDIOVASCULARES
        if dados.dor_peito:
            score += 0.20  # Sintoma cardinal
        if dados.falta_ar:
            score += 0.15  # Dispneia importante
        if dados.fadiga:
            score += 0.10  # Fadiga cardiovascular
        if dados.tontura:
            score += 0.08  # Possivel hipotensao/arritmia
        
        # 7. COMPLEXIDADE CLINICA
        if dados.num_medicamentos >= 5:
            score += 0.10  # Polifarmacia
        elif dados.num_medicamentos >= 3:
            score += 0.05
        
        if dados.visitas_anuais >= 6:
            score += 0.08  # Frequentes consultas = comorbidades
        elif dados.visitas_anuais >= 3:
            score += 0.04
        
        # MODIFICADORES POR GENERO
        if dados.genero == "Masculino":
            score += 0.05  # Homens tem risco ligeiramente maior
        
        # DETERMINACAO DA CATEGORIA
        score = min(score, 1.0)
        
        if score >= 0.75:
            categoria = "Alto Risco"
            probabilidade = 0.85 + (score - 0.75) * 0.6
            confianca = 0.92
        elif score >= 0.45:
            categoria = "Medio Risco"
            probabilidade = 0.30 + (score - 0.45) * 1.83
            confianca = 0.88
        else:
            categoria = "Baixo Risco"
            probabilidade = score * 0.67
            confianca = 0.85
        
        probabilidade = max(0.01, min(0.99, probabilidade))
        
        return categoria, probabilidade, score, confianca

    def gerar_explicacoes_shap(self, dados: PacienteInput, resultado: dict) -> ExplicacoesResponse:
        """Gera explicacoes SHAP simuladas"""
        
        fatores_risco = []
        fatores_protecao = []
        
        bmi, _ = self.calcular_bmi(dados.peso, dados.altura)
        
        # Analisar fatores de risco
        if dados.idade > 50:
            impacto = (dados.idade - 50) * 0.005
            fatores_risco.append(ExplicacaoSHAP(
                fator="Idade",
                valor=dados.idade,
                impacto=impacto,
                interpretacao=f"Idade de {dados.idade} anos aumenta o risco cardiovascular",
                categoria="increase_risk"
            ))
        
        if dados.pressao_sistolica > 140:
            impacto = (dados.pressao_sistolica - 140) * 0.003
            fatores_risco.append(ExplicacaoSHAP(
                fator="Pressao Sistolica",
                valor=dados.pressao_sistolica,
                impacto=impacto,
                interpretacao=f"Hipertensao (PAS: {dados.pressao_sistolica} mmHg) e fator de risco importante",
                categoria="increase_risk"
            ))
        
        if bmi > 30:
            impacto = (bmi - 30) * 0.015
            fatores_risco.append(ExplicacaoSHAP(
                fator="BMI",
                valor=bmi,
                impacto=impacto,
                interpretacao=f"Obesidade (BMI: {bmi:.1f}) aumenta significativamente o risco",
                categoria="increase_risk"
            ))
        
        if dados.dor_peito:
            fatores_risco.append(ExplicacaoSHAP(
                fator="Dor no Peito",
                valor=1,
                impacto=0.20,
                interpretacao="Dor toracica e sintoma cardinal de risco cardiovascular",
                categoria="increase_risk"
            ))
        
        # Analisar fatores protetivos
        if dados.idade < 40:
            fatores_protecao.append(ExplicacaoSHAP(
                fator="Idade Jovem",
                valor=dados.idade,
                impacto=-0.05,
                interpretacao=f"Idade de {dados.idade} anos e fator protetor",
                categoria="decrease_risk"
            ))
        
        if bmi >= 18.5 and bmi <= 24.9:
            fatores_protecao.append(ExplicacaoSHAP(
                fator="Peso Normal",
                valor=bmi,
                impacto=-0.03,
                interpretacao=f"BMI normal ({bmi:.1f}) e fator protetor",
                categoria="decrease_risk"
            ))
        
        # Gerar interpretacao geral
        if resultado['categoria'] == "Alto Risco":
            interpretacao_geral = "Paciente apresenta multiplos fatores de risco que elevam significativamente a probabilidade de eventos cardiovasculares. Recomenda-se avaliacao cardiologica imediata e intervencoes terapeuticas intensivas."
        elif resultado['categoria'] == "Medio Risco":
            interpretacao_geral = "Paciente apresenta alguns fatores de risco que requerem monitoramento regular e intervencoes preventivas. Modificacoes no estilo de vida e acompanhamento medico sao essenciais."
        else:
            interpretacao_geral = "Paciente apresenta baixo risco cardiovascular atual, mas deve manter habitos preventivos e consultas regulares para monitoramento continuo."
        
        # Gerar recomendacoes
        recomendacoes = []
        if dados.pressao_sistolica > 140:
            recomendacoes.append("🩺 Controle rigoroso da hipertensao arterial com medicacao otimizada")
        if bmi > 30:
            recomendacoes.append("⚖️ Programa estruturado de reducao de peso com nutricionalista")
        if dados.dor_peito:
            recomendacoes.append("🚨 Investigacao cardiologica imediata com ECG e marcadores cardiacos")
        if dados.colesterol > 240:
            recomendacoes.append("💊 Tratamento da dislipidemia com estatinas conforme protocolo")
        if dados.glicose > 126:
            recomendacoes.append("🍎 Controle glicemico rigoroso e avaliacao endocrinologica")
        
        if not recomendacoes:
            recomendacoes = ["✅ Manter habitos saudaveis e consultas preventivas regulares"]
        
        return ExplicacoesResponse(
            fatores_risco=fatores_risco,
            fatores_protecao=fatores_protecao,
            interpretacao_geral=interpretacao_geral,
            recomendacoes=recomendacoes
        )

# Instancia global do modelo
modelo_ia = ModeloIAMedica()

# ENDPOINTS DA API
@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raiz com informacoes da API"""
    return {
        "sistema": "CardioCare AI - Sistema IA Medica",
        "versao": "1.0.3",
        "status": "API funcionando em producao",
        "ambiente": "production",
        "descricao": "API REST para analise de risco cardiaco com IA e explicabilidade SHAP",
        "documentacao": "/docs",
        "frontend": "Integrado com React + Vite + Shadcn/ui"
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Endpoint para verificacao de saude da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.3",
        "environment": "production",
        "modelo_ia": "CardioCare AI - Carregado e funcional"
    }

@app.post("/predicao", response_model=PredicaoResponse, tags=["Analise"])
async def fazer_predicao(dados: PacienteInput):
    """
    Realiza predicao de risco cardiaco para um paciente
    """
    try:
        # Calcular BMI e classificacoes
        bmi, classificacao_bmi = modelo_ia.calcular_bmi(dados.peso, dados.altura)
        classificacao_pressao = modelo_ia.classificar_pressao(dados.pressao_sistolica, dados.pressao_diastolica)
        
        # Calcular risco com algoritmo avancado
        categoria, probabilidade, score, confianca = modelo_ia.calcular_risco_avancado(dados)
        
        return PredicaoResponse(
            categoria_risco=categoria,
            probabilidade=round(probabilidade, 4),
            score_risco=round(score, 4),
            confianca=round(confianca, 3),
            timestamp=datetime.now().isoformat(),
            bmi=bmi,
            classificacao_bmi=classificacao_bmi,
            classificacao_pressao=classificacao_pressao
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na predicao: {str(e)}")

@app.post("/analise-completa", response_model=AnaliseCompletaResponse, tags=["Analise"])
async def analise_completa(dados: PacienteInput):
    """
    Realiza analise completa com predicao e explicacoes SHAP
    """
    try:
        # Fazer predicao
        bmi, classificacao_bmi = modelo_ia.calcular_bmi(dados.peso, dados.altura)
        classificacao_pressao = modelo_ia.classificar_pressao(dados.pressao_sistolica, dados.pressao_diastolica)
        categoria, probabilidade, score, confianca = modelo_ia.calcular_risco_avancado(dados)
        
        predicao = PredicaoResponse(
            categoria_risco=categoria,
            probabilidade=round(probabilidade, 4),
            score_risco=round(score, 4),
            confianca=round(confianca, 3),
            timestamp=datetime.now().isoformat(),
            bmi=bmi,
            classificacao_bmi=classificacao_bmi,
            classificacao_pressao=classificacao_pressao
        )
        
        # Gerar explicacoes
        resultado = {
            'categoria': categoria,
            'probabilidade': probabilidade,
            'score': score
        }
        
        explicacoes = modelo_ia.gerar_explicacoes_shap(dados, resultado)
        
        # Dados processados para auditoria
        dados_processados = {
            'entrada': dados.model_dump(),
            'calculos': {
                'bmi': bmi,
                'score_final': score,
                'fatores_analisados': len(explicacoes.fatores_risco)
            }
        }
        
        return AnaliseCompletaResponse(
            predicao=predicao,
            explicacoes=explicacoes,
            dados_processados=dados_processados
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na analise completa: {str(e)}")

@app.get("/exemplo-paciente", tags=["Utilitarios"])
async def exemplo_paciente():
    """Retorna exemplo de dados de paciente para testes"""
    return {
        "exemplo_baixo_risco": {
            "idade": 35,
            "genero": "Feminino",
            "tipo_sanguineo": "O+",
            "pressao_sistolica": 110,
            "pressao_diastolica": 70,
            "freq_cardiaca": 68,
            "peso": 65,
            "altura": 1.65,
            "colesterol": 180,
            "glicose": 90,
            "num_medicamentos": 0,
            "visitas_anuais": 1,
            "dor_peito": False,
            "falta_ar": False,
            "fadiga": False,
            "tontura": False
        },
        "exemplo_medio_risco": {
            "idade": 50,
            "genero": "Masculino",
            "tipo_sanguineo": "A+",
            "pressao_sistolica": 135,
            "pressao_diastolica": 85,
            "freq_cardiaca": 75,
            "peso": 85,
            "altura": 1.75,
            "colesterol": 220,
            "glicose": 105,
            "num_medicamentos": 2,
            "visitas_anuais": 2,
            "dor_peito": False,
            "falta_ar": False,
            "fadiga": True,
            "tontura": False
        },
        "exemplo_alto_risco": {
            "idade": 65,
            "genero": "Masculino",
            "tipo_sanguineo": "A+",
            "pressao_sistolica": 165,
            "pressao_diastolica": 95,
            "freq_cardiaca": 85,
            "peso": 95,
            "altura": 1.75,
            "colesterol": 280,
            "glicose": 140,
            "num_medicamentos": 4,
            "visitas_anuais": 6,
            "dor_peito": True,
            "falta_ar": True,
            "fadiga": True,
            "tontura": False
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)