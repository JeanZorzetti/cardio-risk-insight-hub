"""PREVENT (Khan SS et al., Circulation 2024;149(6):430-449) — modelo "base", desfecho DCV total.

Coeficientes: ver "Proveniência dos coeficientes" no plano de implementação.
Fórmula: regressão logística sobre termos-spline lineares por partes, centrados em
pontos de corte clínicos (colesterol/HDL em mmol/L, PAS em 110/130, IMC em 25/30,
eGFR em 60/90), mais interações idade×fator e medicação×fator.
"""

import math
from dataclasses import dataclass

FAIXA_ETARIA = (30, 79)
FAIXA_30_ANOS = (30, 59)

_COEF_10 = {
    "feminino": [0.7939329, 0.0305239, -0.1606857, -0.2394003, 0.3600781, 0.8667604, 0.5360739, 0.0, 0.0,
                 0.6045917, 0.0433769, 0.3151672, -0.1477655, -0.0663612, 0.1197879, -0.0819715, 0.0306769,
                 -0.0946348, -0.27057, -0.078715, 0.0, -0.1637806, -3.307728],
    "masculino": [0.7688528, 0.0736174, -0.0954431, -0.4347345, 0.3362658, 0.7692857, 0.4386871, 0.0, 0.0,
                  0.5378979, 0.0164827, 0.288879, -0.1337349, -0.0475924, 0.150273, -0.0517874, 0.0191169,
                  -0.1049477, -0.2251948, -0.0895067, 0.0, -0.1543702, -3.031168],
}
_COEF_30 = {
    "feminino": [0.5503079, -0.0928369, 0.0409794, -0.1663306, -0.1628654, 0.3299505, 0.6793894, 0.3196112, 0.0,
                 0.0, 0.1857101, 0.0553528, 0.2894, -0.075688, -0.056367, 0.1071019, -0.0751438, 0.0301786,
                 -0.0998776, -0.3206166, -0.1607862, 0.0, -0.1450788, -1.318827],
    "masculino": [0.4627309, -0.0984281, 0.0836088, -0.1029824, -0.2140352, 0.2904325, 0.5331276, 0.2141914, 0.0,
                  0.0, 0.1155556, 0.0603775, 0.232714, -0.0272112, -0.0384488, 0.134192, -0.0511759, 0.0165865,
                  -0.1101437, -0.2585943, -0.1566406, 0.0, -0.1166776, -1.148204],
}

# Índice de cada termo no vetor de coeficientes de 10 anos.
# O vetor de 30 anos é idêntico, mas insere "idade_c2" logo após "idade_c" — daí o +1 em tudo depois.
_IDX_10 = dict(idade_c=0, nao_hdl=1, hdl=2, pas_baixa=3, pas_alta=4, diabetes=5, tabagismo=6,
               imc_baixo=7, imc_alto=8, egfr_baixo=9, egfr_alto=10, anti_hipertensivo=11, estatina=12,
               anti_hipertensivo_x_pas_alta=13, estatina_x_nao_hdl=14, idade_x_nao_hdl=15, idade_x_hdl=16,
               idade_x_pas_alta=17, idade_x_diabetes=18, idade_x_tabagismo=19, idade_x_imc_alto=20,
               idade_x_egfr_baixo=21, intercepto=22)
_IDX_30 = dict(idade_c=0, idade_c2=1, nao_hdl=2, hdl=3, pas_baixa=4, pas_alta=5, diabetes=6, tabagismo=7,
               imc_baixo=8, imc_alto=9, egfr_baixo=10, egfr_alto=11, anti_hipertensivo=12, estatina=13,
               anti_hipertensivo_x_pas_alta=14, estatina_x_nao_hdl=15, idade_x_nao_hdl=16, idade_x_hdl=17,
               idade_x_pas_alta=18, idade_x_diabetes=19, idade_x_tabagismo=20, idade_x_imc_alto=21,
               idade_x_egfr_baixo=22, intercepto=23)

# Cada fator clínico agrupa seu termo principal + suas interações com idade/medicação,
# para exibir "quanto a pressão contribuiu" em vez de termos-spline crus.
_GRUPOS = {
    "Colesterol não-HDL": ("nao_hdl", "idade_x_nao_hdl"),
    "HDL": ("hdl", "idade_x_hdl"),
    "Pressão sistólica": ("pas_baixa", "pas_alta", "anti_hipertensivo_x_pas_alta", "idade_x_pas_alta"),
    "Diabetes": ("diabetes", "idade_x_diabetes"),
    "Tabagismo": ("tabagismo", "idade_x_tabagismo"),
    "IMC": ("imc_baixo", "imc_alto", "idade_x_imc_alto"),
    "Função renal (eGFR)": ("egfr_baixo", "egfr_alto", "idade_x_egfr_baixo"),
    "Uso de anti-hipertensivo": ("anti_hipertensivo",),
    "Uso de estatina": ("estatina", "estatina_x_nao_hdl"),
}


def _para_mmol(mg_dl):
    return mg_dl * 0.02586


@dataclass(frozen=True)
class Contribuicao:
    fator: str
    valor: float
    contribuicao: float


@dataclass(frozen=True)
class ResultadoHorizonte:
    risco: float
    preditor_linear: float
    preditor_linear_referencia: float
    contribuicoes: list


@dataclass(frozen=True)
class ResultadoPrevent:
    dez_anos: ResultadoHorizonte
    trinta_anos: "ResultadoHorizonte | None"


def _termos(idade, colesterol_total, hdl, pas, imc, egfr, diabetes, tabagismo,
            anti_hipertensivo, estatina, com_quadrado):
    idade_c = (idade - 55) / 10
    nao_hdl = _para_mmol(colesterol_total - hdl) - 3.5
    hdl_termo = (_para_mmol(hdl) - 1.3) / 0.3
    pas_baixa = (min(pas, 110) - 110) / 20
    pas_alta = (max(pas, 110) - 130) / 20
    imc_baixo = (min(imc, 30) - 25) / 5
    imc_alto = (max(imc, 30) - 30) / 5
    egfr_baixo = (min(egfr, 60) - 60) / -15
    egfr_alto = (max(egfr, 60) - 90) / -15
    dm = 1.0 if diabetes else 0.0
    sm = 1.0 if tabagismo else 0.0
    bp = 1.0 if anti_hipertensivo else 0.0
    st = 1.0 if estatina else 0.0

    valores = dict(idade_c=idade_c, nao_hdl=nao_hdl, hdl=hdl_termo, pas_baixa=pas_baixa, pas_alta=pas_alta,
                   diabetes=dm, tabagismo=sm, imc_baixo=imc_baixo, imc_alto=imc_alto,
                   egfr_baixo=egfr_baixo, egfr_alto=egfr_alto, anti_hipertensivo=bp, estatina=st,
                   anti_hipertensivo_x_pas_alta=bp * pas_alta, estatina_x_nao_hdl=st * nao_hdl,
                   idade_x_nao_hdl=idade_c * nao_hdl, idade_x_hdl=idade_c * hdl_termo,
                   idade_x_pas_alta=idade_c * pas_alta, idade_x_diabetes=idade_c * dm,
                   idade_x_tabagismo=idade_c * sm, idade_x_imc_alto=idade_c * imc_alto,
                   idade_x_egfr_baixo=idade_c * egfr_baixo, intercepto=1.0)
    if com_quadrado:
        valores["idade_c2"] = idade_c * idade_c
    return valores


def _calcular_horizonte(idx, coef, idade, colesterol_total, hdl, pas, imc, egfr, diabetes, tabagismo,
                         anti_hipertensivo, estatina, com_quadrado):
    valores = _termos(idade, colesterol_total, hdl, pas, imc, egfr, diabetes, tabagismo,
                       anti_hipertensivo, estatina, com_quadrado)
    soma = sum(coef[idx[nome]] * valor for nome, valor in valores.items())
    p = math.exp(soma) / (1 + math.exp(soma))
    risco = math.floor(p * 1000 + 0.5 + 1e-8) / 1000

    # Perfil de referência: todos os termos-spline centrados em zero (colesterol não-HDL
    # 3,5 mmol/L, HDL 1,3 mmol/L, PAS 130, IMC 30, eGFR 90, sem meds/diabetes/tabagismo),
    # mesma idade e sexo do paciente — por isso só sobra o termo de idade + intercepto.
    soma_referencia = coef[idx["idade_c"]] * valores["idade_c"] + coef[idx["intercepto"]]
    if com_quadrado:
        soma_referencia += coef[idx["idade_c2"]] * valores["idade_c2"]

    valores_clinicos = {
        "Colesterol não-HDL": colesterol_total - hdl,
        "HDL": hdl,
        "Pressão sistólica": pas,
        "Diabetes": float(diabetes),
        "Tabagismo": float(tabagismo),
        "IMC": imc,
        "Função renal (eGFR)": egfr,
        "Uso de anti-hipertensivo": float(anti_hipertensivo),
        "Uso de estatina": float(estatina),
    }

    contribuicoes = [
        Contribuicao(fator, valores_clinicos[fator], sum(coef[idx[t]] * valores[t] for t in termos))
        for fator, termos in _GRUPOS.items()
    ]

    return ResultadoHorizonte(risco=risco, preditor_linear=soma, preditor_linear_referencia=soma_referencia,
                               contribuicoes=contribuicoes)


def calcular(sexo, idade, colesterol_total, hdl, pas, imc, egfr, diabetes, tabagismo,
             anti_hipertensivo, estatina):
    if sexo not in _COEF_10:
        raise ValueError(f"sexo deve ser 'masculino' ou 'feminino', recebido: {sexo!r}")

    dez = _calcular_horizonte(_IDX_10, _COEF_10[sexo], idade, colesterol_total, hdl, pas, imc, egfr,
                               diabetes, tabagismo, anti_hipertensivo, estatina, com_quadrado=False)

    trinta = None
    if FAIXA_30_ANOS[0] <= idade <= FAIXA_30_ANOS[1]:
        trinta = _calcular_horizonte(_IDX_30, _COEF_30[sexo], idade, colesterol_total, hdl, pas, imc, egfr,
                                      diabetes, tabagismo, anti_hipertensivo, estatina, com_quadrado=True)

    return ResultadoPrevent(dez_anos=dez, trinta_anos=trinta)
