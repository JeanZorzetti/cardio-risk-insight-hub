"""Framingham office-based (D'Agostino RB et al., Circulation 2008) — sem exames laboratoriais.

Coeficientes: ver "Proveniência dos coeficientes" no plano de implementação.
Fórmula: risco = 1 - S0^exp(soma_dos_termos - media_do_grupo), Cox proporcional,
sem termos de interação (diferente do PREVENT).
"""

import math
from dataclasses import dataclass

FAIXA_ETARIA = (30, 74)

_COEF = {
    "masculino": dict(
        ln_idade=3.11296, ln_imc=0.79277, ln_pas_sem_tratamento=1.85508,
        ln_pas_tratada=1.92672, tabagismo=0.70953, diabetes=0.53160,
        media_grupo=23.9388, sobrevida_base=0.88431,
    ),
    "feminino": dict(
        ln_idade=2.72107, ln_imc=0.51125, ln_pas_sem_tratamento=2.81291,
        ln_pas_tratada=2.88267, tabagismo=0.61868, diabetes=0.77763,
        media_grupo=26.0145, sobrevida_base=0.94833,
    ),
}

# Perfil de referência para decomposição por fator: mesma idade e sexo do paciente,
# demais fatores no valor "ótimo" (IMC normal, PAS ótima sem tratamento, sem
# tabagismo, sem diabetes). A contribuição de cada fator é exatamente
# coeficiente * (termo_paciente - termo_referencia) — aditiva por construção.
_REFERENCIA = dict(imc=22.0, pas=115.0, em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False)


@dataclass(frozen=True)
class Contribuicao:
    fator: str
    valor: float
    contribuicao: float


@dataclass(frozen=True)
class ResultadoFramingham:
    risco_10_anos: float
    risco_truncado: bool
    preditor_linear: float
    preditor_linear_referencia: float
    contribuicoes: list


def _preditor_linear(coef, idade, imc, pas, em_tratamento, tabagismo, diabetes):
    pas_tratada = pas if em_tratamento else 1.0
    pas_sem_tratamento = pas if not em_tratamento else 1.0
    return (
        math.log(idade) * coef["ln_idade"]
        + math.log(imc) * coef["ln_imc"]
        + math.log(pas_tratada) * coef["ln_pas_tratada"]
        + math.log(pas_sem_tratamento) * coef["ln_pas_sem_tratamento"]
        + (1.0 if tabagismo else 0.0) * coef["tabagismo"]
        + (1.0 if diabetes else 0.0) * coef["diabetes"]
    )


def calcular(sexo, idade, imc, pas, em_tratamento_anti_hipertensivo, tabagismo, diabetes):
    if sexo not in _COEF:
        raise ValueError(f"sexo deve ser 'masculino' ou 'feminino', recebido: {sexo!r}")

    coef = _COEF[sexo]
    soma = _preditor_linear(coef, idade, imc, pas, em_tratamento_anti_hipertensivo, tabagismo, diabetes)
    risco_bruto = 1 - coef["sobrevida_base"] ** math.exp(soma - coef["media_grupo"])
    risco = max(0.01, min(0.30, risco_bruto))
    risco_truncado = risco_bruto < 0.01 or risco_bruto > 0.30

    soma_referencia = _preditor_linear(
        coef, idade,
        _REFERENCIA["imc"], _REFERENCIA["pas"],
        _REFERENCIA["em_tratamento_anti_hipertensivo"], _REFERENCIA["tabagismo"], _REFERENCIA["diabetes"],
    )

    pas_coef_paciente = coef["ln_pas_tratada"] if em_tratamento_anti_hipertensivo else coef["ln_pas_sem_tratamento"]

    contribuicoes = [
        Contribuicao("IMC", imc, coef["ln_imc"] * (math.log(imc) - math.log(_REFERENCIA["imc"]))),
        Contribuicao(
            "Pressão sistólica",
            pas,
            coef["ln_pas_sem_tratamento"] * (math.log(pas) - math.log(_REFERENCIA["pas"])),
        ),
        Contribuicao(
            "Uso de anti-hipertensivo",
            float(em_tratamento_anti_hipertensivo),
            (pas_coef_paciente - coef["ln_pas_sem_tratamento"]) * math.log(pas),
        ),
        Contribuicao("Tabagismo", float(tabagismo), coef["tabagismo"] * (1.0 if tabagismo else 0.0)),
        Contribuicao("Diabetes", float(diabetes), coef["diabetes"] * (1.0 if diabetes else 0.0)),
    ]

    return ResultadoFramingham(
        risco_10_anos=round(risco, 4),
        risco_truncado=risco_truncado,
        preditor_linear=soma,
        preditor_linear_referencia=soma_referencia,
        contribuicoes=contribuicoes,
    )
