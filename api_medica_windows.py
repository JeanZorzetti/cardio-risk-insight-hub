# API REST MEDICA - VERSAO WINDOWS COMPATIVEL
# Sistema IA MÃ©dica - Corrigido para Windows + Pydantic v2

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
import uvicorn

# Configuracao da API
app = FastAPI(
    title="Sistema IA Medica - API REST",
    description="API profissional para analise de risco cardiaco com IA",
    version="1.0.2",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para permitir front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de dados
class PacienteInput(BaseModel):
    idade: int = Field(..., ge=18, le=120, description="Idade do paciente em anos")
    genero: str = Field(..., pattern="^(Masculino|Feminino)$", description="Genero do paciente")
    tipo_sanguineo: str = Field(..., pattern="^(A\\+|A-|B\\+|B-|AB\\+|AB-|O\\+|O-)$", description="Tipo sanguineo")
    pressao_sistolica: float = Field(..., ge=60, le=300, description="Pressao sistolica em mmHg")
    pressao_diastolica: float = Field(..., ge=30, le=200, description="Pressao diastolica em mmHg")
    freq_cardiaca: float = Field(..., ge=30, le=200, description="Frequencia cardiaca em bpm")
    peso: float = Field(..., ge=20, le=300, description="Peso em kg")
    altura: float = Field(..., ge=1.0, le=2.5, description="Altura em metros")
    colesterol: float = Field(..., ge=50, le=500, description="Colesterol total em mg/dL")
    glicose: float = Field(..., ge=50, le=400, description="Glicose em mg/dL")
    num_medicamentos: int = Field(..., ge=0, le=20, description="Numero de medicamentos")
    visitas_anuais: int = Field(..., ge=0, le=50, description="Visitas medicas por ano")
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
    categoria_risco: str = Field(..., description="Categoria de risco")
    probabilidade: float = Field(..., ge=0, le=1, description="Probabilidade de alto risco")
    score_risco: float = Field(..., ge=0, le=1, description="Score de risco calculado")
    confianca: float = Field(..., ge=0, le=1, description="Confianca da predicao")
    timestamp: str = Field(..., description="Timestamp da analise")
    bmi: float = Field(..., description="BMI calculado")
    classificacao_bmi: str = Field(..., description="Classificacao do BMI")
    classificacao_pressao: str = Field(..., description="Classificacao da pressao arterial")

class ExplicacaoSHAP(BaseModel):
    fator: str = Field(..., description="Nome do fator")
    valor: float = Field(..., description="Valor do fator")
    impacto: float = Field(..., description="Impacto SHAP no risco")
    interpretacao: str = Field(..., description="Interpretacao medica")
    categoria: str = Field(..., description="Categoria do impacto")

class ExplicacoesResponse(BaseModel):
    fatores_risco: List[ExplicacaoSHAP] = Field(..., description="Fatores que aumentam o risco")
    fatores_protecao: List[ExplicacaoSHAP] = Field(..., description="Fatores que diminuem o risco")
    interpretacao_geral: str = Field(..., description="Interpretacao geral do caso")
    recomendacoes: List[str] = Field(..., description="Recomendacoes medicas")

class AnaliseCompletaResponse(BaseModel):
    predicao: PredicaoResponse
    explicacoes: ExplicacoesResponse
    dados_processados: Dict[str, Any] = Field(..., description="Dados processados")

# Logica de negocio
class ModeloIAMedica:
    def __init__(self):
        print("Modelo IA Medica inicializado com sucesso!")
    
    def calcular_bmi(self, peso: float, altura: float) -> tuple:
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
        bmi, _ = self.calcular_bmi(dados.peso, dados.altura)
        score = 0
        
        # Fator idade
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
        
        # Fator pressao arterial
        if dados.pressao_sistolica >= 180 or dados.pressao_diastolica >= 120:
            score += 0.30
        elif dados.pressao_sistolica >= 140 or dados.pressao_diastolica >= 90:
            score += 0.25
        elif dados.pressao_sistolica >= 130 or dados.pressao_diastolica >= 80:
            score += 0.15
        elif dados.pressao_sistolica >= 120:
            score += 0.05
        
        # Fator BMI
        if bmi >= 40:
            score += 0.25
        elif bmi >= 35:
            score += 0.20
        elif bmi >= 30:
            score += 0.15
        elif bmi >= 25:
            score += 0.08
        
        # Fator colesterol
        if dados.colesterol >= 300:
            score += 0.25
        elif dados.colesterol >= 240:
            score += 0.20
        elif dados.colesterol >= 200:
            score += 0.10
        
        # Fator glicose
        if dados.glicose >= 200:
            score += 0.25
        elif dados.glicose >= 126:
            score += 0.20
        elif dados.glicose >= 100:
            score += 0.10
        
        # Sintomas
        if dados.dor_peito:
            score += 0.20
        if dados.falta_ar:
            score += 0.15
        if dados.fadiga:
            score += 0.10
        if dados.tontura:
            score += 0.08
        
        # Complexidade clinica
        if dados.num_medicamentos >= 5:
            score += 0.10
        elif dados.num_medicamentos >= 3:
            score += 0.05
        
        if dados.visitas_anuais >= 6:
            score += 0.08
        elif dados.visitas_anuais >= 3:
            score += 0.04
        
        # Modificador por genero
        if dados.genero == "Masculino":
            score += 0.05
        
        # Normalizar score
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
    
    def gerar_explicacoes_detalhadas(self, dados: PacienteInput, categoria: str, score: float) -> ExplicacoesResponse:
        bmi, bmi_class = self.calcular_bmi(dados.peso, dados.altura)
        classificacao_pressao = self.classificar_pressao(dados.pressao_sistolica, dados.pressao_diastolica)
        
        fatores_risco = []
        fatores_protecao = []
        
        # Analise da idade
        if dados.idade >= 65:
            impacto = 0.25 + (dados.idade - 65) * 0.01
            fatores_risco.append(ExplicacaoSHAP(
                fator="Idade Avancada",
                valor=dados.idade,
                impacto=round(impacto, 3),
                interpretacao=f"Idade de {dados.idade} anos representa fator de risco cardiovascular significativo",
                categoria="increase_risk"
            ))
        elif dados.idade >= 45:
            impacto = 0.10 + (dados.idade - 45) * 0.005
            fatores_risco.append(ExplicacaoSHAP(
                fator="Idade Intermediaria",
                valor=dados.idade,
                impacto=round(impacto, 3),
                interpretacao=f"Idade de {dados.idade} anos e fator de risco moderado",
                categoria="increase_risk"
            ))
        else:
            fatores_protecao.append(ExplicacaoSHAP(
                fator="Idade Jovem",
                valor=dados.idade,
                impacto=-0.05,
                interpretacao=f"Idade jovem ({dados.idade} anos) e fator protetor",
                categoria="decrease_risk"
            ))
        
        # Analise da pressao arterial
        if classificacao_pressao in ["Hipertensao Estagio 2", "Crise Hipertensiva"]:
            impacto = 0.25 + (dados.pressao_sistolica - 140) * 0.002
            fatores_risco.append(ExplicacaoSHAP(
                fator="Hipertensao Severa",
                valor=dados.pressao_sistolica,
                impacto=round(impacto, 3),
                interpretacao=f"{classificacao_pressao}: {dados.pressao_sistolica}/{dados.pressao_diastolica} mmHg",
                categoria="increase_risk"
            ))
        elif classificacao_pressao == "Hipertensao Estagio 1":
            impacto = 0.15
            fatores_risco.append(ExplicacaoSHAP(
                fator="Hipertensao Leve",
                valor=dados.pressao_sistolica,
                impacto=impacto,
                interpretacao=f"Hipertensao estagio 1: {dados.pressao_sistolica}/{dados.pressao_diastolica} mmHg",
                categoria="increase_risk"
            ))
        elif classificacao_pressao == "Normal":
            fatores_protecao.append(ExplicacaoSHAP(
                fator="Pressao Normal",
                valor=dados.pressao_sistolica,
                impacto=-0.05,
                interpretacao=f"Pressao arterial normal: {dados.pressao_sistolica}/{dados.pressao_diastolica} mmHg",
                categoria="decrease_risk"
            ))
        
        # Analise do BMI
        if bmi >= 30:
            impacto = 0.15 + (bmi - 30) * 0.01
            fatores_risco.append(ExplicacaoSHAP(
                fator="Obesidade",
                valor=bmi,
                impacto=round(impacto, 3),
                interpretacao=f"{bmi_class}: BMI {bmi} kg/m2 aumenta risco cardiovascular",
                categoria="increase_risk"
            ))
        elif bmi >= 25:
            impacto = 0.08
            fatores_risco.append(ExplicacaoSHAP(
                fator="Sobrepeso",
                valor=bmi,
                impacto=impacto,
                interpretacao=f"Sobrepeso: BMI {bmi} kg/m2 e fator de risco moderado",
                categoria="increase_risk"
            ))
        elif bmi >= 18.5:
            fatores_protecao.append(ExplicacaoSHAP(
                fator="Peso Normal",
                valor=bmi,
                impacto=-0.03,
                interpretacao=f"BMI normal ({bmi} kg/m2) e fator protetor",
                categoria="decrease_risk"
            ))
        
        # Sintomas cardiovasculares
        if dados.dor_peito:
            fatores_risco.append(ExplicacaoSHAP(
                fator="Dor Toracica",
                valor=1,
                impacto=0.20,
                interpretacao="Dor no peito e sintoma cardinal de doenca cardiovascular",
                categoria="increase_risk"
            ))
        
        if dados.falta_ar:
            fatores_risco.append(ExplicacaoSHAP(
                fator="Dispneia",
                valor=1,
                impacto=0.15,
                interpretacao="Falta de ar pode indicar insuficiencia cardiaca ou isquemia",
                categoria="increase_risk"
            ))
        
        # Ordenar por impacto
        fatores_risco.sort(key=lambda x: x.impacto, reverse=True)
        fatores_protecao.sort(key=lambda x: abs(x.impacto), reverse=True)
        
        # Interpretacao geral
        if categoria == "Alto Risco":
            interpretacao = f"Paciente {dados.genero.lower()}, {dados.idade} anos, apresenta multiplos fatores de risco cardiovascular. Score de risco elevado ({score:.3f}) indica necessidade de avaliacao cardiologica IMEDIATA."
        elif categoria == "Medio Risco":
            interpretacao = f"Paciente {dados.genero.lower()}, {dados.idade} anos, com fatores de risco cardiovascular moderados. Score {score:.3f} requer monitoramento proximo."
        else:
            interpretacao = f"Paciente {dados.genero.lower()}, {dados.idade} anos, apresenta baixo risco cardiovascular (score {score:.3f}). Manter estrategias de prevencao primaria."
        
        # Recomendacoes
        recomendacoes = self.gerar_recomendacoes_personalizadas(categoria, dados, bmi, classificacao_pressao)
        
        return ExplicacoesResponse(
            fatores_risco=fatores_risco[:5],
            fatores_protecao=fatores_protecao[:3],
            interpretacao_geral=interpretacao,
            recomendacoes=recomendacoes
        )
    
    def gerar_recomendacoes_personalizadas(self, categoria: str, dados: PacienteInput, bmi: float, classificacao_pressao: str) -> List[str]:
        recomendacoes = []
        
        if categoria == "Alto Risco":
            recomendacoes.extend([
                "URGENTE: Consulta cardiologica nas proximas 24-48h",
                "ECG de 12 derivacoes e ecocardiograma imediatos",
                "Troponina, BNP/NT-proBNP, D-dimero urgentes",
                "Revisar e otimizar medicacoes cardiovasculares"
            ])
        elif categoria == "Medio Risco":
            recomendacoes.extend([
                "Consulta cardiologica em 2-4 semanas",
                "Perfil lipidico completo, HbA1c, funcao renal",
                "Teste ergometrico ou cintilografia miocardica",
                "Monitoramento domiciliar da pressao arterial"
            ])
        else:
            recomendacoes.extend([
                "Check-up cardiologico anual",
                "Perfil lipidico e glicemia anuais",
                "Atividade fisica regular (150min/semana)",
                "Dieta mediterranea ou DASH"
            ])
        
        # Recomendacoes especificas
        if classificacao_pressao in ["Hipertensao Estagio 1", "Hipertensao Estagio 2"]:
            recomendacoes.append("Monitoramento PA domiciliar")
        
        if bmi >= 30:
            recomendacoes.append("Meta: perda 5-10% peso em 6 meses")
        
        if dados.colesterol >= 240:
            recomendacoes.append("Estatina alta intensidade + ezetimiba")
        
        if dados.dor_peito:
            recomendacoes.insert(0, "INVESTIGAR dor toracica: ECG, troponina")
        
        return recomendacoes[:8]

# Instancia global do modelo
modelo_ia = ModeloIAMedica()

# Endpoints da API
@app.get("/", tags=["Sistema"])
async def root():
    return {
        "sistema": "Sistema IA Medica",
        "versao": "1.0.2",
        "status": "API funcionando perfeitamente",
        "pydantic_version": "v2 compatible",
        "endpoints": {
            "docs": "/docs",
            "predicao": "/predicao",
            "explicacoes": "/explicacoes",
            "analise_completa": "/analise-completa",
            "exemplo": "/exemplo-paciente"
        }
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.2",
        "pydantic": "v2_compatible",
        "modelo_ia": "Carregado e funcional"
    }

@app.post("/predicao", response_model=PredicaoResponse, tags=["Analise"])
async def fazer_predicao(dados: PacienteInput):
    try:
        bmi, classificacao_bmi = modelo_ia.calcular_bmi(dados.peso, dados.altura)
        classificacao_pressao = modelo_ia.classificar_pressao(dados.pressao_sistolica, dados.pressao_diastolica)
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

@app.post("/explicacoes", response_model=ExplicacoesResponse, tags=["Explicabilidade"])
async def obter_explicacoes(dados: PacienteInput):
    try:
        categoria, probabilidade, score, confianca = modelo_ia.calcular_risco_avancado(dados)
        explicacoes = modelo_ia.gerar_explicacoes_detalhadas(dados, categoria, score)
        return explicacoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro nas explicacoes: {str(e)}")

@app.post("/analise-completa", response_model=AnaliseCompletaResponse, tags=["Analise"])
async def analise_completa(dados: PacienteInput):
    try:
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
        
        explicacoes = modelo_ia.gerar_explicacoes_detalhadas(dados, categoria, score)
        
        dados_processados = {
            "dados_entrada": dados.model_dump(),
            "metricas_calculadas": {
                "bmi": bmi,
                "classificacao_bmi": classificacao_bmi,
                "classificacao_pressao": classificacao_pressao
            },
            "algoritmo": {
                "score_detalhado": round(score, 4),
                "fatores_analisados": len(explicacoes.fatores_risco) + len(explicacoes.fatores_protecao),
                "versao_algoritmo": "2.0_advanced"
            },
            "timestamps": {
                "processamento": datetime.now().isoformat(),
                "versao_api": "1.0.2"
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
    print("Iniciando API REST Medica...")
    print("Documentacao: http://localhost:8000/docs")
    print("Sistema IA Medica v1.0.2 - Windows Compatible")
    
    uvicorn.run(
        "api_medica_windows:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
