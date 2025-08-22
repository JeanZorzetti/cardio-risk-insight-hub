# 🚀 API REST MÉDICA CORRIGIDA - Sistema IA (Passo 3 - FIXED)
# Correção para Pydantic v2 + Melhorias

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
import uvicorn

# Configuração da API
app = FastAPI(
    title="🏥 Sistema IA Médica - API REST",
    description="API profissional para análise de risco cardíaco com IA e explicabilidade SHAP",
    version="1.0.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para permitir front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# MODELOS DE DADOS (Pydantic v2 Compatible)
# =====================================================================

class PacienteInput(BaseModel):
    """Modelo para entrada de dados do paciente - CORRIGIDO PYDANTIC V2"""
    
    # Dados demográficos
    idade: int = Field(..., ge=18, le=120, description="Idade do paciente em anos")
    genero: str = Field(..., pattern="^(Masculino|Feminino)$", description="Gênero do paciente")
    tipo_sanguineo: str = Field(..., pattern="^(A\\+|A-|B\\+|B-|AB\\+|AB-|O\\+|O-)$", description="Tipo sanguíneo")
    
    # Dados vitais
    pressao_sistolica: float = Field(..., ge=60, le=300, description="Pressão sistólica em mmHg")
    pressao_diastolica: float = Field(..., ge=30, le=200, description="Pressão diastólica em mmHg")
    freq_cardiaca: float = Field(..., ge=30, le=200, description="Frequência cardíaca em bpm")
    
    # Dados antropométricos e laboratoriais
    peso: float = Field(..., ge=20, le=300, description="Peso em kg")
    altura: float = Field(..., ge=1.0, le=2.5, description="Altura em metros")
    colesterol: float = Field(..., ge=50, le=500, description="Colesterol total em mg/dL")
    glicose: float = Field(..., ge=50, le=400, description="Glicose em mg/dL")
    
    # Histórico médico
    num_medicamentos: int = Field(..., ge=0, le=20, description="Número de medicamentos")
    visitas_anuais: int = Field(..., ge=0, le=50, description="Visitas médicas por ano")
    
    # Sintomas (booleanos)
    dor_peito: bool = Field(..., description="Presença de dor no peito")
    falta_ar: bool = Field(..., description="Presença de falta de ar")
    fadiga: bool = Field(..., description="Presença de fadiga")
    tontura: bool = Field(..., description="Presença de tontura")
    
    @validator('pressao_diastolica')
    def validar_pressao_diastolica(cls, v, values):
        if 'pressao_sistolica' in values and v >= values['pressao_sistolica']:
            raise ValueError('Pressão diastólica deve ser menor que sistólica')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "idade": 55,
                "genero": "Masculino",
                "tipo_sanguineo": "O+",
                "pressao_sistolica": 140,
                "pressao_diastolica": 90,
                "freq_cardiaca": 75,
                "peso": 80,
                "altura": 1.75,
                "colesterol": 220,
                "glicose": 110,
                "num_medicamentos": 2,
                "visitas_anuais": 3,
                "dor_peito": True,
                "falta_ar": False,
                "fadiga": True,
                "tontura": False
            }
        }

class PredicaoResponse(BaseModel):
    """Modelo para resposta da predição"""
    
    categoria_risco: str = Field(..., description="Categoria de risco: Baixo Risco, Médio Risco, Alto Risco")
    probabilidade: float = Field(..., ge=0, le=1, description="Probabilidade de alto risco (0-1)")
    score_risco: float = Field(..., ge=0, le=1, description="Score de risco calculado")
    confianca: float = Field(..., ge=0, le=1, description="Confiança da predição")
    timestamp: str = Field(..., description="Timestamp da análise")
    
    # Dados calculados
    bmi: float = Field(..., description="BMI calculado")
    classificacao_bmi: str = Field(..., description="Classificação do BMI")
    classificacao_pressao: str = Field(..., description="Classificação da pressão arterial")

class ExplicacaoSHAP(BaseModel):
    """Modelo para explicação individual SHAP"""
    
    fator: str = Field(..., description="Nome do fator/feature")
    valor: float = Field(..., description="Valor do fator para este paciente")
    impacto: float = Field(..., description="Impacto SHAP no risco")
    interpretacao: str = Field(..., description="Interpretação em linguagem médica")
    categoria: str = Field(..., description="Categoria: increase_risk, decrease_risk, neutral")

class ExplicacoesResponse(BaseModel):
    """Modelo para resposta das explicações"""
    
    fatores_risco: List[ExplicacaoSHAP] = Field(..., description="Fatores que aumentam o risco")
    fatores_protecao: List[ExplicacaoSHAP] = Field(..., description="Fatores que diminuem o risco")
    interpretacao_geral: str = Field(..., description="Interpretação geral do caso")
    recomendacoes: List[str] = Field(..., description="Recomendações médicas")

class AnaliseCompletaResponse(BaseModel):
    """Modelo para análise completa"""
    
    predicao: PredicaoResponse
    explicacoes: ExplicacoesResponse
    dados_processados: Dict[str, Any] = Field(..., description="Dados processados para auditoria")

# =====================================================================
# LÓGICA DE NEGÓCIO APRIMORADA
# =====================================================================

class ModeloIAMedica:
    """Classe para encapsular lógica do modelo de IA médica - VERSÃO APRIMORADA"""
    
    def __init__(self):
        print("🏥 Modelo IA Médica inicializado com sucesso!")
    
    def calcular_bmi(self, peso: float, altura: float) -> tuple:
        """Calcula BMI e sua classificação"""
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
            classificacao = "Obesidade Grau III (Mórbida)"
            
        return round(bmi, 2), classificacao
    
    def classificar_pressao(self, sistolica: float, diastolica: float) -> str:
        """Classifica pressão arterial segundo diretrizes"""
        if sistolica < 120 and diastolica < 80:
            return "Normal"
        elif sistolica < 130 and diastolica < 80:
            return "Elevada"
        elif (sistolica >= 130 and sistolica < 140) or (diastolica >= 80 and diastolica < 90):
            return "Hipertensão Estágio 1"
        elif (sistolica >= 140 and sistolica < 180) or (diastolica >= 90 and diastolica < 120):
            return "Hipertensão Estágio 2"
        else:
            return "Crise Hipertensiva"
    
    def calcular_risco_avancado(self, dados: PacienteInput) -> tuple:
        """Algoritmo de risco cardiovascular aprimorado"""
        
        bmi, _ = self.calcular_bmi(dados.peso, dados.altura)
        score = 0
        
        # === FATORES DE RISCO PRINCIPAIS ===
        
        # 1. IDADE (peso variável por faixa)
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
        
        # 2. PRESSÃO ARTERIAL (baseado em guidelines)
        if dados.pressao_sistolica >= 180 or dados.pressao_diastolica >= 120:
            score += 0.30  # Crise hipertensiva
        elif dados.pressao_sistolica >= 140 or dados.pressao_diastolica >= 90:
            score += 0.25  # Hipertensão estágio 2
        elif dados.pressao_sistolica >= 130 or dados.pressao_diastolica >= 80:
            score += 0.15  # Hipertensão estágio 1
        elif dados.pressao_sistolica >= 120:
            score += 0.05  # Pressão elevada
        
        # 3. BMI (obesidade é fator de risco significativo)
        if bmi >= 40:
            score += 0.25  # Obesidade mórbida
        elif bmi >= 35:
            score += 0.20  # Obesidade grau II
        elif bmi >= 30:
            score += 0.15  # Obesidade grau I
        elif bmi >= 25:
            score += 0.08  # Sobrepeso
        
        # 4. PERFIL LIPÍDICO
        if dados.colesterol >= 300:
            score += 0.25
        elif dados.colesterol >= 240:
            score += 0.20
        elif dados.colesterol >= 200:
            score += 0.10
        
        # 5. GLICOSE (diabetes/pré-diabetes)
        if dados.glicose >= 200:
            score += 0.25  # Diabetes descompensado
        elif dados.glicose >= 126:
            score += 0.20  # Diabetes
        elif dados.glicose >= 100:
            score += 0.10  # Pré-diabetes
        
        # === FATORES CLÍNICOS ===
        
        # 6. SINTOMAS CARDIOVASCULARES (peso alto)
        if dados.dor_peito:
            score += 0.20  # Sintoma cardinal
        if dados.falta_ar:
            score += 0.15  # Dispneia importante
        if dados.fadiga:
            score += 0.10  # Fadiga cardiovascular
        if dados.tontura:
            score += 0.08  # Possível hipotensão/arritmia
        
        # 7. COMPLEXIDADE CLÍNICA
        if dados.num_medicamentos >= 5:
            score += 0.10  # Polifarmácia
        elif dados.num_medicamentos >= 3:
            score += 0.05
        
        if dados.visitas_anuais >= 6:
            score += 0.08  # Frequentes consultas = comorbidades
        elif dados.visitas_anuais >= 3:
            score += 0.04
        
        # === MODIFICADORES POR GÊNERO ===
        if dados.genero == "Masculino":
            score += 0.05  # Homens têm risco ligeiramente maior
        
        # === DETERMINAÇÃO DA CATEGORIA ===
        
        # Normalizar score (máximo teórico ~1.5, normalizar para 1.0)
        score = min(score, 1.0)
        
        if score >= 0.75:
            categoria = "Alto Risco"
            probabilidade = 0.85 + (score - 0.75) * 0.6  # 85-100%
            confianca = 0.92
        elif score >= 0.45:
            categoria = "Médio Risco"
            probabilidade = 0.30 + (score - 0.45) * 1.83  # 30-85%
            confianca = 0.88
        else:
            categoria = "Baixo Risco"
            probabilidade = score * 0.67  # 0-30%
            confianca = 0.85
        
        # Garantir bounds
        probabilidade = max(0.01, min(0.99, probabilidade))
        
        return categoria, probabilidade, score, confianca
    
    def gerar_explicacoes_detalhadas(self, dados: PacienteInput, categoria: str, score: float) -> ExplicacoesResponse:
        """Gera explicações SHAP detalhadas e precisas"""
        
        bmi, bmi_class = self.calcular_bmi(dados.peso, dados.altura)
        classificacao_pressao = self.classificar_pressao(dados.pressao_sistolica, dados.pressao_diastolica)
        
        fatores_risco = []
        fatores_protecao = []
        
        # === ANÁLISE DETALHADA DOS FATORES ===
        
        # 1. IDADE
        if dados.idade >= 65:
            impacto = 0.25 + (dados.idade - 65) * 0.01
            fatores_risco.append(ExplicacaoSHAP(
                fator="Idade Avançada",
                valor=dados.idade,
                impacto=round(impacto, 3),
                interpretacao=f"Idade de {dados.idade} anos representa fator de risco cardiovascular significativo",
                categoria="increase_risk"
            ))
        elif dados.idade >= 45:
            impacto = 0.10 + (dados.idade - 45) * 0.005
            fatores_risco.append(ExplicacaoSHAP(
                fator="Idade Intermediária",
                valor=dados.idade,
                impacto=round(impacto, 3),
                interpretacao=f"Idade de {dados.idade} anos é fator de risco moderado",
                categoria="increase_risk"
            ))
        else:
            fatores_protecao.append(ExplicacaoSHAP(
                fator="Idade Jovem",
                valor=dados.idade,
                impacto=-0.05,
                interpretacao=f"Idade jovem ({dados.idade} anos) é fator protetor",
                categoria="decrease_risk"
            ))
        
        # 2. PRESSÃO ARTERIAL
        if classificacao_pressao in ["Hipertensão Estágio 2", "Crise Hipertensiva"]:
            impacto = 0.25 + (dados.pressao_sistolica - 140) * 0.002
            fatores_risco.append(ExplicacaoSHAP(
                fator="Hipertensão Severa",
                valor=dados.pressao_sistolica,
                impacto=round(impacto, 3),
                interpretacao=f"{classificacao_pressao}: {dados.pressao_sistolica}/{dados.pressao_diastolica} mmHg",
                categoria="increase_risk"
            ))
        elif classificacao_pressao == "Hipertensão Estágio 1":
            impacto = 0.15
            fatores_risco.append(ExplicacaoSHAP(
                fator="Hipertensão Leve",
                valor=dados.pressao_sistolica,
                impacto=impacto,
                interpretacao=f"Hipertensão estágio 1: {dados.pressao_sistolica}/{dados.pressao_diastolica} mmHg",
                categoria="increase_risk"
            ))
        elif classificacao_pressao == "Normal":
            fatores_protecao.append(ExplicacaoSHAP(
                fator="Pressão Normal",
                valor=dados.pressao_sistolica,
                impacto=-0.05,
                interpretacao=f"Pressão arterial normal: {dados.pressao_sistolica}/{dados.pressao_diastolica} mmHg",
                categoria="decrease_risk"
            ))
        
        # 3. BMI E OBESIDADE
        if bmi >= 30:
            impacto = 0.15 + (bmi - 30) * 0.01
            fatores_risco.append(ExplicacaoSHAP(
                fator="Obesidade",
                valor=bmi,
                impacto=round(impacto, 3),
                interpretacao=f"{bmi_class}: BMI {bmi} kg/m² aumenta risco cardiovascular",
                categoria="increase_risk"
            ))
        elif bmi >= 25:
            impacto = 0.08
            fatores_risco.append(ExplicacaoSHAP(
                fator="Sobrepeso",
                valor=bmi,
                impacto=impacto,
                interpretacao=f"Sobrepeso: BMI {bmi} kg/m² é fator de risco moderado",
                categoria="increase_risk"
            ))
        elif bmi >= 18.5:
            fatores_protecao.append(ExplicacaoSHAP(
                fator="Peso Normal",
                valor=bmi,
                impacto=-0.03,
                interpretacao=f"BMI normal ({bmi} kg/m²) é fator protetor",
                categoria="decrease_risk"
            ))
        
        # 4. PERFIL LIPÍDICO
        if dados.colesterol >= 240:
            impacto = 0.20 + (dados.colesterol - 240) * 0.0005
            fatores_risco.append(ExplicacaoSHAP(
                fator="Colesterol Muito Alto",
                valor=dados.colesterol,
                impacto=round(impacto, 3),
                interpretacao=f"Colesterol total {dados.colesterol} mg/dL - dislipidemia significativa",
                categoria="increase_risk"
            ))
        elif dados.colesterol >= 200:
            impacto = 0.10
            fatores_risco.append(ExplicacaoSHAP(
                fator="Colesterol Elevado",
                valor=dados.colesterol,
                impacto=impacto,
                interpretacao=f"Colesterol {dados.colesterol} mg/dL acima do ideal (<200)",
                categoria="increase_risk"
            ))
        
        # 5. GLICOSE
        if dados.glicose >= 126:
            impacto = 0.20 + (dados.glicose - 126) * 0.001
            fatores_risco.append(ExplicacaoSHAP(
                fator="Diabetes",
                valor=dados.glicose,
                impacto=round(impacto, 3),
                interpretacao=f"Glicose {dados.glicose} mg/dL sugere diabetes mellitus",
                categoria="increase_risk"
            ))
        elif dados.glicose >= 100:
            impacto = 0.10
            fatores_risco.append(ExplicacaoSHAP(
                fator="Pré-diabetes",
                valor=dados.glicose,
                impacto=impacto,
                interpretacao=f"Glicose {dados.glicose} mg/dL indica pré-diabetes",
                categoria="increase_risk"
            ))
        
        # 6. SINTOMAS CARDIOVASCULARES
        if dados.dor_peito:
            fatores_risco.append(ExplicacaoSHAP(
                fator="Dor Torácica",
                valor=1,
                impacto=0.20,
                interpretacao="Dor no peito é sintoma cardinal de doença cardiovascular",
                categoria="increase_risk"
            ))
        
        if dados.falta_ar:
            fatores_risco.append(ExplicacaoSHAP(
                fator="Dispneia",
                valor=1,
                impacto=0.15,
                interpretacao="Falta de ar pode indicar insuficiência cardíaca ou isquemia",
                categoria="increase_risk"
            ))
        
        if dados.fadiga:
            fatores_risco.append(ExplicacaoSHAP(
                fator="Fadiga",
                valor=1,
                impacto=0.10,
                interpretacao="Fadiga pode ser sinal de disfunção cardiovascular",
                categoria="increase_risk"
            ))
        
        # Ordenar por impacto
        fatores_risco.sort(key=lambda x: x.impacto, reverse=True)
        fatores_protecao.sort(key=lambda x: abs(x.impacto), reverse=True)
        
        # === INTERPRETAÇÃO GERAL CLÍNICA ===
        if categoria == "Alto Risco":
            interpretacao = (
                f"Paciente {dados.genero.lower()}, {dados.idade} anos, apresenta múltiplos fatores de risco "
                f"cardiovascular. Score de risco elevado ({score:.3f}) indica necessidade de "
                f"avaliação cardiológica IMEDIATA e intervenção terapêutica intensiva."
            )
        elif categoria == "Médio Risco":
            interpretacao = (
                f"Paciente {dados.genero.lower()}, {dados.idade} anos, com fatores de risco "
                f"cardiovascular moderados. Score {score:.3f} requer monitoramento próximo, "
                f"modificação do estilo de vida e possível terapia medicamentosa."
            )
        else:
            interpretacao = (
                f"Paciente {dados.genero.lower()}, {dados.idade} anos, apresenta baixo risco "
                f"cardiovascular (score {score:.3f}). Manter estratégias de prevenção primária "
                f"e monitoramento periódico."
            )
        
        # === RECOMENDAÇÕES PERSONALIZADAS ===
        recomendacoes = self.gerar_recomendacoes_personalizadas(categoria, dados, bmi, classificacao_pressao)
        
        return ExplicacoesResponse(
            fatores_risco=fatores_risco[:5],  # Top 5
            fatores_protecao=fatores_protecao[:3],  # Top 3
            interpretacao_geral=interpretacao,
            recomendacoes=recomendacoes
        )
    
    def gerar_recomendacoes_personalizadas(self, categoria: str, dados: PacienteInput, bmi: float, classificacao_pressao: str) -> List[str]:
        """Gera recomendações médicas personalizadas e específicas"""
        
        recomendacoes = []
        
        # === RECOMENDAÇÕES POR CATEGORIA DE RISCO ===
        if categoria == "Alto Risco":
            recomendacoes.extend([
                "🚨 URGENTE: Consulta cardiológica nas próximas 24-48h",
                "📋 ECG de 12 derivações e ecocardiograma imediatos",
                "🩸 Troponina, BNP/NT-proBNP, D-dímero urgentes",
                "💊 Revisar e otimizar medicações cardiovasculares",
                "🏥 Considerar hospitalização se sintomas graves"
            ])
        elif categoria == "Médio Risco":
            recomendacoes.extend([
                "👨‍⚕️ Consulta cardiológica em 2-4 semanas",
                "📊 Perfil lipídico completo, HbA1c, função renal",
                "🔍 Teste ergométrico ou cintilografia miocárdica",
                "💊 Iniciar/otimizar estatina se indicado",
                "📱 Monitoramento domiciliar da pressão arterial"
            ])
        else:
            recomendacoes.extend([
                "👨‍⚕️ Check-up cardiológico anual",
                "📊 Perfil lipídico e glicemia anuais",
                "🏃‍♂️ Atividade física regular (150min/semana)",
                "🥗 Dieta mediterrânea ou DASH",
                "🚭 Cessação do tabagismo se aplicável"
            ])
        
        # === RECOMENDAÇÕES ESPECÍFICAS POR CONDIÇÃO ===
        
        # Hipertensão
        if classificacao_pressao in ["Hipertensão Estágio 1", "Hipertensão Estágio 2"]:
            recomendacoes.extend([
                "🩺 Monitoramento PA domiciliar (MAPA se possível)",
                "🧂 Redução sódio <2g/dia, aumentar potássio",
                "💊 Otimizar anti-hipertensivos (IECA/BRA + diurético)"
            ])
        
        if classificacao_pressao == "Crise Hipertensiva":
            recomendacoes.insert(0, "🚨 EMERGÊNCIA: Atendimento imediato - risco de AVC/IAM")
        
        # Obesidade/Sobrepeso
        if bmi >= 30:
            recomendacoes.extend([
                "⚖️ Meta: perda 5-10% peso em 6 meses",
                "👥 Acompanhamento nutricional multidisciplinar",
                "🏃‍♂️ Exercícios combinados (aeróbio + resistência)",
                "💊 Considerar medicação anti-obesidade se indicado"
            ])
        elif bmi >= 25:
            recomendacoes.append("⚖️ Meta: redução 3-5kg, manter IMC <25")
        
        # Dislipidemia
        if dados.colesterol >= 240:
            recomendacoes.extend([
                "💊 Estatina alta intensidade + ezetimiba",
                "🥗 Dieta baixa em gordura saturada (<7% cal)",
                "📊 Meta: LDL <70mg/dL (ou <55mg/dL se alto risco)"
            ])
        elif dados.colesterol >= 200:
            recomendacoes.append("💊 Considerar estatina + mudanças dietéticas")
        
        # Diabetes/Pré-diabetes
        if dados.glicose >= 126:
            recomendacoes.extend([
                "🍎 HbA1c meta <7% (individualizar se necessário)",
                "💊 Metformina + SGLT2i ou GLP1-RA se risco CV",
                "👁️ Fundo de olho anual, microalbuminúria"
            ])
        elif dados.glicose >= 100:
            recomendacoes.append("🍎 Programa prevenção diabetes (perda peso + exercício)")
        
        # Sintomas específicos
        if dados.dor_peito:
            recomendacoes.insert(0, "💔 INVESTIGAR dor torácica: ECG, troponina, considerar cateterismo")
        
        if dados.falta_ar:
            recomendacoes.append("🫁 Ecocardiograma + BNP para investigar IC")
        
        # Polifarmácia
        if dados.num_medicamentos >= 5:
            recomendacoes.append("💊 Revisão medicamentosa: desprescrição e interações")
        
        return recomendacoes[:8]  # Máximo 8 recomendações para não sobrecarregar

# Instância global do modelo
modelo_ia = ModeloIAMedica()

# =====================================================================
# ENDPOINTS DA API
# =====================================================================

@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "sistema": "🏥 Sistema IA Médica",
        "versao": "1.0.1",
        "status": "✅ API funcionando perfeitamente",
        "pydantic_version": "v2 compatible",
        "descricao": "API REST para análise de risco cardíaco com IA",
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
    """Endpoint para verificação de saúde da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.1",
        "pydantic": "v2_compatible",
        "modelo_ia": "✅ Carregado e funcional"
    }

@app.post("/predicao", response_model=PredicaoResponse, tags=["Análise"])
async def fazer_predicao(dados: PacienteInput):
    """
    Realiza predição de risco cardíaco para um paciente
    
    - **Entrada**: Dados completos do paciente
    - **Saída**: Categoria de risco, probabilidade e métricas
    """
    try:
        # Calcular BMI e classificações
        bmi, classificacao_bmi = modelo_ia.calcular_bmi(dados.peso, dados.altura)
        classificacao_pressao = modelo_ia.classificar_pressao(dados.pressao_sistolica, dados.pressao_diastolica)
        
        # Calcular risco com algoritmo avançado
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
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@app.post("/explicacoes", response_model=ExplicacoesResponse, tags=["Explicabilidade"])
async def obter_explicacoes(dados: PacienteInput):
    """
    Gera explicações SHAP para a predição
    
    - **Entrada**: Dados do paciente
    - **Saída**: Explicações detalhadas dos fatores de risco
    """
    try:
        # Calcular risco primeiro
        categoria, probabilidade, score, confianca = modelo_ia.calcular_risco_avancado(dados)
        
        # Gerar explicações detalhadas
        explicacoes = modelo_ia.gerar_explicacoes_detalhadas(dados, categoria, score)
        
        return explicacoes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro nas explicações: {str(e)}")

@app.post("/analise-completa", response_model=AnaliseCompletaResponse, tags=["Análise"])
async def analise_completa(dados: PacienteInput):
    """
    Análise completa: predição + explicações SHAP
    
    - **Entrada**: Dados do paciente
    - **Saída**: Análise completa com predição e explicações
    """
    try:
        # Calcular BMI e classificações
        bmi, classificacao_bmi = modelo_ia.calcular_bmi(dados.peso, dados.altura)
        classificacao_pressao = modelo_ia.classificar_pressao(dados.pressao_sistolica, dados.pressao_diastolica)
        
        # Calcular risco com algoritmo avançado
        categoria, probabilidade, score, confianca = modelo_ia.calcular_risco_avancado(dados)
        
        # Criar resposta de predição
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
        
        # Gerar explicações detalhadas
        explicacoes = modelo_ia.gerar_explicacoes_detalhadas(dados, categoria, score)
        
        # Dados processados para auditoria
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
                "versao_api": "1.0.1"
            }
        }
        
        return AnaliseCompletaResponse(
            predicao=predicao,
            explicacoes=explicacoes,
            dados_processados=dados_processados
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise completa: {str(e)}")

@app.get("/exemplo-paciente", tags=["Utilitários"])
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

# =====================================================================
# EXECUTAR API
# =====================================================================

if __name__ == "__main__":
    print("🚀 Iniciando API REST Médica...")
    print("📋 Documentação: http://localhost:8000/docs")
    print("🏥 Sistema IA Médica v1.0.1 - Pydantic v2 Compatible")
    
    uvicorn.run(
        "api_medica_corrigida:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )