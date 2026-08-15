"""API REST — CardioRisk. Escores de risco cardiovascular validados (Framingham office-based e PREVENT)."""

import os
from datetime import datetime
from typing import List, Literal, Optional, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from scores import framingham_office, prevent

app = FastAPI(
    title="CardioRisk — API de Estratificação de Risco Cardiovascular",
    description=(
        "Escores de risco cardiovascular validados publicamente (Framingham office-based "
        "e PREVENT) para triagem e priorização administrativa. Não é diagnóstico e não "
        "substitui avaliação médica."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:4173",
    "https://*.vercel.app",
    "https://cardio-risk-insight-hub.vercel.app",
    "https://cardiorisk.roilabs.com.br",
    "http://cardiorisk.roilabs.com.br",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# MODELOS DE ENTRADA

class EntradaRapida(BaseModel):
    """Campos do modo rápido (/risco/rapido) — Framingham office-based, sem exames."""

    idade: int = Field(..., ge=18, le=120, description="Idade em anos")
    sexo: str = Field(..., pattern="^(masculino|feminino)$")
    peso: float = Field(..., ge=20, le=300, description="Peso em kg")
    altura: float = Field(..., ge=1.0, le=2.5, description="Altura em metros")
    pas: float = Field(..., ge=60, le=300, description="Pressão arterial sistólica em mmHg")
    usa_anti_hipertensivo: bool = Field(..., description="Em tratamento farmacológico para hipertensão")
    tabagismo: bool = Field(..., description="Fumante atual")
    diabetes: bool = Field(..., description="Diagnóstico de diabetes")
    dor_peito: bool = Field(..., description="Dor no peito atual — dispara bloqueio de segurança")
    falta_ar: bool = Field(..., description="Falta de ar atual — dispara bloqueio de segurança")
    fadiga: bool = Field(..., description="Fadiga atual (coletado por contexto clínico, não entra no cálculo)")
    tontura: bool = Field(..., description="Tontura atual (coletado por contexto clínico, não entra no cálculo)")


class EntradaPrevent(EntradaRapida):
    """Campos do modo completo (/risco/prevent) — soma-se aos do modo rápido."""

    colesterol_total: float = Field(..., ge=50, le=500, description="Colesterol total em mg/dL")
    hdl: float = Field(..., ge=10, le=150, description="HDL em mg/dL")
    egfr: float = Field(..., ge=5, le=200, description="Taxa de filtração glomerular estimada, mL/min/1.73m²")
    usa_estatina: bool = Field(..., description="Em uso de estatina")


# MODELOS DE SAÍDA

class ContribuicaoResponse(BaseModel):
    fator: str
    valor: float
    contribuicao: float


class RespostaRisco(BaseModel):
    tipo: Literal["resultado"] = "resultado"
    categoria_risco: str
    risco_10_anos: float = Field(..., description="Probabilidade em 10 anos (0-1)")
    risco_30_anos: Optional[float] = Field(
        None, description="Probabilidade em 30 anos (0-1); só PREVENT, e só para idade 30-59"
    )
    risco_truncado: bool = Field(
        False, description="True se o risco bruto calculado estava fora de 1%-30% e foi truncado nesse intervalo"
    )
    bmi: float
    classificacao_bmi: str
    contribuicoes: List[ContribuicaoResponse]
    escore: str
    fonte: str
    timestamp: str


class RespostaBloqueio(BaseModel):
    tipo: Literal["bloqueio"] = "bloqueio"
    motivo: Literal["sintomas", "faixa_etaria"]
    mensagem: str


# LOGICA COMPARTILHADA

def _calcular_bmi(peso: float, altura: float) -> tuple:
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


def _categoria_risco(risco_10_anos: float) -> str:
    """Categorias de 3 níveis (decisão de produto, não da publicação original) —
    mantém a UI existente (Baixo/Médio/Alto) com os limiares clínicos usuais de risco ASCVD."""
    if risco_10_anos >= 0.20:
        return "Alto Risco"
    if risco_10_anos >= 0.05:
        return "Médio Risco"
    return "Baixo Risco"


def _guard_sintomas(dados) -> Optional[RespostaBloqueio]:
    if dados.dor_peito or dados.falta_ar:
        return RespostaBloqueio(
            motivo="sintomas",
            mensagem=(
                "Você relatou dor no peito ou falta de ar. Este é um escore de prevenção "
                "primária, válido apenas para quem não tem sintomas cardiovasculares. "
                "Procure avaliação médica presencial o quanto antes — não é possível "
                "estimar risco com segurança neste caso."
            ),
        )
    return None


def _guard_idade(idade: int, faixa: tuple, nome_escore: str) -> Optional[RespostaBloqueio]:
    if not (faixa[0] <= idade <= faixa[1]):
        return RespostaBloqueio(
            motivo="faixa_etaria",
            mensagem=(
                f"O escore {nome_escore} é validado apenas para {faixa[0]}-{faixa[1]} anos. "
                "Fora dessa faixa o resultado não é confiável e não é calculado."
            ),
        )
    return None


# ENDPOINTS

@app.get("/", tags=["Sistema"])
async def root():
    return {
        "sistema": "CardioRisk — Estratificação de Risco Cardiovascular",
        "versao": "2.0.0",
        "status": "API funcionando em producao",
        "descricao": (
            "Escores validados (Framingham office-based e PREVENT) para triagem e "
            "priorização administrativa. Não é diagnóstico."
        ),
        "documentacao": "/docs",
    }


@app.get("/health", tags=["Sistema"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
    }


@app.post("/risco/rapido", response_model=Union[RespostaRisco, RespostaBloqueio], tags=["Risco"])
async def risco_rapido(dados: EntradaRapida):
    bloqueio = _guard_sintomas(dados) or _guard_idade(
        dados.idade, framingham_office.FAIXA_ETARIA, "Framingham (modo rápido)"
    )
    if bloqueio:
        return bloqueio

    bmi, classificacao_bmi = _calcular_bmi(dados.peso, dados.altura)
    resultado = framingham_office.calcular(
        sexo=dados.sexo, idade=dados.idade, imc=bmi, pas=dados.pas,
        em_tratamento_anti_hipertensivo=dados.usa_anti_hipertensivo,
        tabagismo=dados.tabagismo, diabetes=dados.diabetes,
    )

    return RespostaRisco(
        categoria_risco=_categoria_risco(resultado.risco_10_anos),
        risco_10_anos=resultado.risco_10_anos,
        risco_truncado=resultado.risco_truncado,
        bmi=bmi,
        classificacao_bmi=classificacao_bmi,
        contribuicoes=[
            ContribuicaoResponse(fator=c.fator, valor=c.valor, contribuicao=c.contribuicao)
            for c in resultado.contribuicoes
        ],
        escore="Framingham office-based (D'Agostino RB et al., 2008)",
        fonte="D'Agostino RB et al. Circulation. 2008;117:743-753.",
        timestamp=datetime.now().isoformat(),
    )


@app.post("/risco/prevent", response_model=Union[RespostaRisco, RespostaBloqueio], tags=["Risco"])
async def risco_prevent(dados: EntradaPrevent):
    bloqueio = _guard_sintomas(dados) or _guard_idade(dados.idade, prevent.FAIXA_ETARIA, "PREVENT")
    if bloqueio:
        return bloqueio

    bmi, classificacao_bmi = _calcular_bmi(dados.peso, dados.altura)
    resultado = prevent.calcular(
        sexo=dados.sexo, idade=dados.idade, colesterol_total=dados.colesterol_total, hdl=dados.hdl,
        pas=dados.pas, imc=bmi, egfr=dados.egfr, diabetes=dados.diabetes, tabagismo=dados.tabagismo,
        anti_hipertensivo=dados.usa_anti_hipertensivo, estatina=dados.usa_estatina,
    )

    return RespostaRisco(
        categoria_risco=_categoria_risco(resultado.dez_anos.risco),
        risco_10_anos=resultado.dez_anos.risco,
        risco_30_anos=resultado.trinta_anos.risco if resultado.trinta_anos else None,
        bmi=bmi,
        classificacao_bmi=classificacao_bmi,
        contribuicoes=[
            ContribuicaoResponse(fator=c.fator, valor=c.valor, contribuicao=c.contribuicao)
            for c in resultado.dez_anos.contribuicoes
        ],
        escore="PREVENT (Khan SS et al., AHA/Circulation 2024)",
        fonte="Khan SS et al. Circulation. 2024;149(6):430-449.",
        timestamp=datetime.now().isoformat(),
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
