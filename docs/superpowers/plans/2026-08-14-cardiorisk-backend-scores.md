# CardioRisk — Motores de Escore (Backend) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir o algoritmo if/else de `calcular_risco_avancado` e as explicações SHAP simuladas por dois escores de risco cardiovascular reais e publicados — Framingham office-based (D'Agostino 2008) e PREVENT (Khan 2024) — como funções puras testadas contra casos de referência, expostas por uma API FastAPI sem qualquer alegação de IA/ML/SHAP.

**Architecture:** Dois módulos Python puros (`backend/scores/framingham_office.py`, `backend/scores/prevent.py`), cada um `entradas → risco + contribuições por fator`, sem FastAPI nem I/O — só matemática, testável isoladamente. `backend/main.py` vira uma casca fina: valida entrada com Pydantic, aplica dois guards de segurança (sintomas, faixa etária), chama o módulo de escore certo, formata a resposta.

**Tech Stack:** Python 3.11, FastAPI + Pydantic v2 (já em uso), pytest (novo, só para `backend/test_scores.py`).

**Spec:** `docs/superpowers/specs/2026-08-14-cardiorisk-produtificacao-design.md`

## Global Constraints

- Nenhuma menção a "SHAP", "Machine Learning" ou "IA" que não exista de fato — nem em código, nem em `description` da API, nem no README.
- Os dois escores são funções puras (`entradas → risco + contribuições`), sem FastAPI, sem estado global.
- Guard de segurança: se `dor_peito` ou `falta_ar` forem `true`, a API **nunca** retorna um percentual — retorna orientação de buscar avaliação médica. Isto é validado antes de qualquer cálculo.
- Guard de faixa etária: fora de 30–74 anos (Framingham) ou 30–79 anos (PREVENT), a API não calcula — retorna bloqueio explicando a faixa validada.
- Risco de 30 anos do PREVENT só é retornado para idade entre 30 e 59 anos (faixa validada pela publicação original — fora dela, `risco_30_anos` é `None`).
- `backend/test_scores.py` é requisito de aceitação: nenhum escore vai para produção sem teste de referência. Tolerância declarada: **±0,2 pontos percentuais**.
- `pressao_diastolica` e `freq_cardiaca` saem do contrato de entrada. Não é omissão: a tabela "Dois modos, dois escores" do spec lista as entradas de cada modo de forma exaustiva (idade, sexo, IMC, PAS, uso de anti-hipertensivo, tabagismo, diabetes [+ colesterol, HDL, eGFR, estatina no completo]) e nenhum dos dois escores usa diastólica ou frequência cardíaca — mantê-los seria coletar dado que não alimenta cálculo nenhum.

## Proveniência dos coeficientes (leia antes de codar)

Os coeficientes abaixo **não** foram transcritos diretamente dos PDFs dos papers (não temos acesso confiável a extrair tabelas de PDF com precisão numérica). Eles vêm de duas implementações de terceiros, código aberto, que documentam a mesma fonte:

- **Framingham office-based**: `frs_simple_coef` do pacote R [`CVrisk`](https://github.com/vcastro/CVrisk) (`data-raw/score_coef.R`), que cita D'Agostino RB et al., *Circulation* 2008;117:743-753. O exemplo `ascvd_10y_frs_simple(gender="male", age=55, bmi=30, sbp=140, bp_med=0, smoker=0, diabetes=0)` documentado no próprio pacote (`# 16.7`) foi reproduzido à mão com os coeficientes abaixo e bateu (16,75% vs 16,7% documentado) — é o `test_caso_documentado_cvrisk_homem` na Task 1.
- **PREVENT**: coeficientes do modelo "base" (10 e 30 anos, desfecho DCV total) extraídos de [`Salomao0569/Prevent-Score`](https://github.com/Salomao0569/Prevent-Score) (`calculadora-prevent.html`, objeto `COEF`), calculadora de código aberto (MIT) que declara no rodapé: *"Coeficientes matemáticos base compatíveis com o calculador oficial da AHA... quando Zip Code/SDI não é informado"*, citando Khan SS et al., *Circulation* 2024;149(6):430-449.

**Antes de considerar a Task 2 (PREVENT) pronta para produção**, valide manualmente pelo menos 1 caso contra a calculadora oficial da AHA (`tools.acc.org/cvd-risk-estimator-plus` ou `professional.heart.org`) e registre o resultado no PR. Os testes deste plano garantem que a implementação bate com a fonte transcrita — não substituem essa checagem cruzada final contra a calculadora oficial.

Se, ao revisar, você tiver acesso direto ao paper/material suplementar e os números divergirem, o paper original vence — corrija os coeficientes e os casos de teste.

---

### Task 1: Escore Framingham office-based (D'Agostino 2008)

**Files:**
- Create: `backend/scores/__init__.py`
- Create: `backend/scores/framingham_office.py`
- Create: `backend/test_scores.py`
- Modify: `backend/requirements.txt`

**Interfaces:**
- Produces: `framingham_office.FAIXA_ETARIA = (30, 74)` — tupla usada pelo guard de idade em `main.py` (Task 3).
- Produces: `framingham_office.calcular(sexo: str, idade: int, imc: float, pas: float, em_tratamento_anti_hipertensivo: bool, tabagismo: bool, diabetes: bool) -> ResultadoFramingham`. `sexo` é `"masculino"` ou `"feminino"` (levanta `ValueError` para qualquer outro valor).
- Produces: `ResultadoFramingham` (dataclass): `risco_10_anos: float` (0–1), `preditor_linear: float`, `preditor_linear_referencia: float`, `contribuicoes: list[Contribuicao]`.
- Produces: `Contribuicao` (dataclass): `fator: str`, `valor: float`, `contribuicao: float`.

- [ ] **Step 1: Scaffolding — pacote de escores e pytest**

Criar `backend/scores/__init__.py` vazio (marca o diretório como pacote Python).

Adicionar ao final de `backend/requirements.txt`:

```
pytest==8.3.3
```

Instalar:

```bash
cd backend
pip install -r requirements.txt
```

- [ ] **Step 2: Escrever o teste de referência (vai falhar — módulo ainda não existe)**

Criar `backend/test_scores.py`:

```python
import pytest

from scores import framingham_office


class TestFraminghamOfficeBased:
    def test_caso_documentado_cvrisk_homem(self):
        r = framingham_office.calcular(
            sexo="masculino", idade=55, imc=30, pas=140,
            em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False,
        )
        assert r.risco_10_anos * 100 == pytest.approx(16.7, abs=0.2)

    def test_mulher_tabagista_pas_elevada(self):
        r = framingham_office.calcular(
            sexo="feminino", idade=58, imc=28, pas=135,
            em_tratamento_anti_hipertensivo=False, tabagismo=True, diabetes=False,
        )
        assert r.risco_10_anos * 100 == pytest.approx(15.49, abs=0.2)

    def test_homem_sem_fatores_risco(self):
        r = framingham_office.calcular(
            sexo="masculino", idade=50, imc=27, pas=125,
            em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False,
        )
        assert r.risco_10_anos * 100 == pytest.approx(9.66, abs=0.2)

    def test_mulher_baixo_risco(self):
        r = framingham_office.calcular(
            sexo="feminino", idade=45, imc=22, pas=110,
            em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False,
        )
        assert r.risco_10_anos * 100 == pytest.approx(2.23, abs=0.2)

    def test_risco_e_limitado_entre_1_e_30_por_cento(self):
        r = framingham_office.calcular(
            sexo="masculino", idade=65, imc=32, pas=150,
            em_tratamento_anti_hipertensivo=True, tabagismo=True, diabetes=True,
        )
        assert r.risco_10_anos == pytest.approx(0.30, abs=1e-9)

    def test_sexo_invalido_levanta_erro(self):
        with pytest.raises(ValueError):
            framingham_office.calcular(
                sexo="outro", idade=50, imc=25, pas=120,
                em_tratamento_anti_hipertensivo=False, tabagismo=False, diabetes=False,
            )

    def test_contribuicoes_somam_a_diferenca_do_preditor_linear(self):
        r = framingham_office.calcular(
            sexo="masculino", idade=60, imc=33, pas=150,
            em_tratamento_anti_hipertensivo=True, tabagismo=True, diabetes=True,
        )
        soma_contribuicoes = sum(c.contribuicao for c in r.contribuicoes)
        assert soma_contribuicoes == pytest.approx(
            r.preditor_linear - r.preditor_linear_referencia, abs=1e-9
        )
```

- [ ] **Step 3: Rodar os testes e confirmar que falham**

```bash
cd backend
pytest test_scores.py -v
```

Esperado: `ModuleNotFoundError: No module named 'scores.framingham_office'` (ou `ImportError`) — o arquivo ainda não existe.

- [ ] **Step 4: Implementar `backend/scores/framingham_office.py`**

```python
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
    risco = 1 - coef["sobrevida_base"] ** math.exp(soma - coef["media_grupo"])
    risco = max(0.01, min(0.30, risco))

    soma_referencia = _preditor_linear(
        coef, idade,
        _REFERENCIA["imc"], _REFERENCIA["pas"],
        _REFERENCIA["em_tratamento_anti_hipertensivo"], _REFERENCIA["tabagismo"], _REFERENCIA["diabetes"],
    )

    pas_coef_paciente = coef["ln_pas_tratada"] if em_tratamento_anti_hipertensivo else coef["ln_pas_sem_tratamento"]
    pas_coef_referencia = coef["ln_pas_sem_tratamento"]

    contribuicoes = [
        Contribuicao("IMC", imc, coef["ln_imc"] * (math.log(imc) - math.log(_REFERENCIA["imc"]))),
        Contribuicao(
            "Pressão sistólica",
            pas,
            pas_coef_paciente * math.log(pas) - pas_coef_referencia * math.log(_REFERENCIA["pas"]),
        ),
        Contribuicao("Tabagismo", float(tabagismo), coef["tabagismo"] * (1.0 if tabagismo else 0.0)),
        Contribuicao("Diabetes", float(diabetes), coef["diabetes"] * (1.0 if diabetes else 0.0)),
    ]

    return ResultadoFramingham(
        risco_10_anos=round(risco, 4),
        preditor_linear=soma,
        preditor_linear_referencia=soma_referencia,
        contribuicoes=contribuicoes,
    )
```

- [ ] **Step 5: Rodar os testes de novo e confirmar que passam**

```bash
cd backend
pytest test_scores.py -v
```

Esperado: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/scores/__init__.py backend/scores/framingham_office.py backend/test_scores.py backend/requirements.txt
git commit -m "feat: add Framingham office-based risk score module"
```

---

### Task 2: Escore PREVENT (Khan et al., 2024)

**Files:**
- Create: `backend/scores/prevent.py`
- Modify: `backend/test_scores.py`

**Interfaces:**
- Consumes: nenhuma (módulo independente do Framingham).
- Produces: `prevent.FAIXA_ETARIA = (30, 79)`, `prevent.FAIXA_30_ANOS = (30, 59)` — usados pelo guard de idade em `main.py` (Task 3): a idade precisa estar em `FAIXA_ETARIA` para calcular; `risco_30_anos` só é retornado quando a idade também está em `FAIXA_30_ANOS`.
- Produces: `prevent.calcular(sexo: str, idade: int, colesterol_total: float, hdl: float, pas: float, imc: float, egfr: float, diabetes: bool, tabagismo: bool, anti_hipertensivo: bool, estatina: bool) -> ResultadoPrevent`. `colesterol_total`/`hdl` em mg/dL, `egfr` em mL/min/1.73m². Levanta `ValueError` se `sexo` não for `"masculino"`/`"feminino"`.
- Produces: `ResultadoPrevent` (dataclass): `dez_anos: ResultadoHorizonte`, `trinta_anos: ResultadoHorizonte | None` (`None` quando `idade` fora de `FAIXA_30_ANOS`).
- Produces: `ResultadoHorizonte` (dataclass): `risco: float` (0–1), `preditor_linear: float`, `preditor_linear_referencia: float`, `contribuicoes: list[Contribuicao]` (mesmo tipo `Contribuicao` da Task 1 — reimplementado localmente neste módulo, mesma forma).

- [ ] **Step 1: Escrever os testes de referência (vão falhar — módulo ainda não existe)**

Editar `backend/test_scores.py`, mudando o import do topo:

```python
import pytest

from scores import framingham_office, prevent
```

E adicionar ao final do arquivo:

```python
class TestPrevent:
    CASO_MEDIO = dict(idade=55, colesterol_total=200, hdl=50, pas=130, imc=27, egfr=90,
                       diabetes=False, tabagismo=False, anti_hipertensivo=False, estatina=False)
    CASO_ALTO_RISCO = dict(idade=65, colesterol_total=240, hdl=40, pas=150, imc=32, egfr=70,
                            diabetes=True, tabagismo=True, anti_hipertensivo=True, estatina=False)
    CASO_JOVEM_SAUDAVEL = dict(idade=35, colesterol_total=180, hdl=60, pas=115, imc=23, egfr=100,
                                diabetes=False, tabagismo=False, anti_hipertensivo=False, estatina=False)

    @pytest.mark.parametrize("sexo,risco_10_esperado,risco_30_esperado", [
        ("feminino", 3.6, 21.4),
        ("masculino", 4.7, 24.7),
    ])
    def test_perfil_medio(self, sexo, risco_10_esperado, risco_30_esperado):
        r = prevent.calcular(sexo=sexo, **self.CASO_MEDIO)
        assert r.dez_anos.risco * 100 == pytest.approx(risco_10_esperado, abs=0.2)
        assert r.trinta_anos is not None
        assert r.trinta_anos.risco * 100 == pytest.approx(risco_30_esperado, abs=0.2)

    @pytest.mark.parametrize("sexo,risco_10_esperado", [
        ("feminino", 29.8),
        ("masculino", 31.6),
    ])
    def test_perfil_alto_risco_sem_estimativa_30_anos(self, sexo, risco_10_esperado):
        r = prevent.calcular(sexo=sexo, **self.CASO_ALTO_RISCO)
        assert r.dez_anos.risco * 100 == pytest.approx(risco_10_esperado, abs=0.2)
        assert r.trinta_anos is None  # idade 65 está fora de FAIXA_30_ANOS (30-59)

    @pytest.mark.parametrize("sexo,risco_10_esperado,risco_30_esperado", [
        ("feminino", 0.4, 3.0),
        ("masculino", 0.6, 4.4),
    ])
    def test_perfil_jovem_saudavel(self, sexo, risco_10_esperado, risco_30_esperado):
        r = prevent.calcular(sexo=sexo, **self.CASO_JOVEM_SAUDAVEL)
        assert r.dez_anos.risco * 100 == pytest.approx(risco_10_esperado, abs=0.2)
        assert r.trinta_anos.risco * 100 == pytest.approx(risco_30_esperado, abs=0.2)

    def test_sexo_invalido_levanta_erro(self):
        with pytest.raises(ValueError):
            prevent.calcular(sexo="outro", **self.CASO_MEDIO)

    def test_contribuicoes_somam_a_diferenca_do_preditor_linear(self):
        r = prevent.calcular(sexo="feminino", **self.CASO_ALTO_RISCO)
        soma = sum(c.contribuicao for c in r.dez_anos.contribuicoes)
        assert soma == pytest.approx(
            r.dez_anos.preditor_linear - r.dez_anos.preditor_linear_referencia, abs=1e-9
        )
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

```bash
cd backend
pytest test_scores.py -v
```

Esperado: `ImportError: cannot import name 'prevent' from 'scores'` — o arquivo ainda não existe.

- [ ] **Step 3: Implementar `backend/scores/prevent.py`**

```python
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
```

Nota para quem revisar: no desfecho "DCV total" do PREVENT, os coeficientes de IMC (`imc_baixo`/`imc_alto`) são `0.0` tanto no modelo de 10 quanto no de 30 anos (ver `_COEF_10`/`_COEF_30` acima). Isso não é bug — no modelo original, IMC só ganha peso no submodelo de insuficiência cardíaca, que este plano não implementa (spec pede risco cardiovascular geral, não por subtipo). Na prática, a contribuição de "IMC" no PREVENT sempre será `0.0`; o campo continua no contrato porque alimenta o cálculo do próprio IMC exibido na resposta (`bmi`) e porque pode passar a valer caso um submodelo futuro seja adicionado.

- [ ] **Step 4: Rodar os testes de novo e confirmar que todos passam**

```bash
cd backend
pytest test_scores.py -v
```

Esperado: 15 passed (7 do Framingham + 8 do PREVENT).

- [ ] **Step 5: Commit**

```bash
git add backend/scores/prevent.py backend/test_scores.py
git commit -m "feat: add PREVENT risk score module"
```

---

### Task 3: Reescrever `backend/main.py` — contrato de API, guards, endpoints

**Files:**
- Modify: `backend/main.py` (substituição integral do arquivo, linhas 1-523)

**Interfaces:**
- Consumes: `framingham_office.FAIXA_ETARIA`, `framingham_office.calcular(...)` (Task 1); `prevent.FAIXA_ETARIA`, `prevent.calcular(...)` (Task 2).
- Produces: `POST /risco/rapido` (Framingham) e `POST /risco/prevent` (PREVENT) — usados pelo plano de frontend (fora deste plano) para popular `/calculadora` e `/calculadora/prevent`.

Este contrato é o que o plano de frontend (próximo plano) vai consumir — os nomes de campo abaixo (`risco_10_anos`, `contribuicoes`, `tipo: "bloqueio"`, etc.) não são renomeáveis sem coordenar os dois planos.

- [ ] **Step 1: Substituir todo o conteúdo de `backend/main.py`**

```python
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
```

- [ ] **Step 2: Verificação manual — subir a API e testar os 4 caminhos**

```bash
cd backend
uvicorn main:app --reload
```

Em outro terminal, com a API rodando em `http://localhost:8000`:

```bash
# 1. Caminho feliz — Framingham
curl -s -X POST http://localhost:8000/risco/rapido -H "Content-Type: application/json" -d '{
  "idade": 55, "sexo": "masculino", "peso": 85, "altura": 1.75, "pas": 140,
  "usa_anti_hipertensivo": false, "tabagismo": false, "diabetes": false,
  "dor_peito": false, "falta_ar": false, "fadiga": false, "tontura": false
}'
# peso 85kg / altura 1.75m -> IMC 27.76 (não 30 — o caso de referência do Step 4 usa IMC=30 direto,
# aqui o IMC é derivado de peso/altura como a API realmente recebe).
# Esperado: "tipo": "resultado", "risco_10_anos" perto de 0.158 (15.8%), "categoria_risco": "Médio Risco"

# 2. Caminho feliz — PREVENT
curl -s -X POST http://localhost:8000/risco/prevent -H "Content-Type: application/json" -d '{
  "idade": 55, "sexo": "feminino", "peso": 70, "altura": 1.65, "pas": 130,
  "usa_anti_hipertensivo": false, "tabagismo": false, "diabetes": false,
  "dor_peito": false, "falta_ar": false, "fadiga": false, "tontura": false,
  "colesterol_total": 200, "hdl": 50, "egfr": 90, "usa_estatina": false
}'
# Esperado: "tipo": "resultado", "risco_10_anos" perto de 0.036, "risco_30_anos" perto de 0.214

# 3. Guard de sintomas
curl -s -X POST http://localhost:8000/risco/rapido -H "Content-Type: application/json" -d '{
  "idade": 55, "sexo": "masculino", "peso": 85, "altura": 1.75, "pas": 140,
  "usa_anti_hipertensivo": false, "tabagismo": false, "diabetes": false,
  "dor_peito": true, "falta_ar": false, "fadiga": false, "tontura": false
}'
# Esperado: "tipo": "bloqueio", "motivo": "sintomas" — SEM nenhum campo de risco

# 4. Guard de faixa etária
curl -s -X POST http://localhost:8000/risco/rapido -H "Content-Type: application/json" -d '{
  "idade": 20, "sexo": "masculino", "peso": 85, "altura": 1.75, "pas": 140,
  "usa_anti_hipertensivo": false, "tabagismo": false, "diabetes": false,
  "dor_peito": false, "falta_ar": false, "fadiga": false, "tontura": false
}'
# Esperado: "tipo": "bloqueio", "motivo": "faixa_etaria"
```

Confirme os 4 resultados antes de seguir. Pare o servidor (Ctrl+C) depois.

- [ ] **Step 3: Rodar a suíte de testes completa de novo (nada deve quebrar)**

```bash
cd backend
pytest test_scores.py -v
```

Esperado: 15 passed (o rewrite de `main.py` não toca nos módulos de escore).

- [ ] **Step 4: Commit**

```bash
git add backend/main.py
git commit -m "refactor: replace fake SHAP/ad-hoc score with real validated risk scores"
```

---

### Task 4: Limpar dependências mortas e alegações de SHAP/ML

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `README.md`

**Interfaces:**
- Nenhuma — task de limpeza, não toca em código executável além de `requirements.txt`.

- [ ] **Step 1: Remover dependências não usadas de `backend/requirements.txt`**

O diagnóstico do spec aponta `scikit-learn` como evidência do "casca sem miolo" (consta no requirements, nunca é importado). Ao ler `backend/main.py` (Task 3), confirma-se que `pandas` e `numpy` também nunca são usados. Nenhum dos três é necessário para os módulos de escore (só usam `math` da stdlib).

Remover as linhas `scikit-learn==1.3.2`, `pandas==2.1.3` e `numpy==1.25.2` de `backend/requirements.txt`. O arquivo final:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pytest==8.3.3
```

- [ ] **Step 2: Confirmar que a API ainda sobe sem as dependências removidas**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Confirme que sobe sem erro de import, depois Ctrl+C.

- [ ] **Step 3: Remover alegações de SHAP/ML do `README.md`**

Editar `README.md`:

Trocar (linha 3):
```
Sistema completo de inteligência artificial para análise de risco cardiovascular, desenvolvido com React + FastAPI.
```
por:
```
Sistema de estratificação de risco cardiovascular baseado em escores clínicos validados e publicados (Framingham office-based e PREVENT), desenvolvido com Next.js + FastAPI.
```

Trocar (linha 7):
```
- **🤖 IA Explicável**: Análise de risco com explicações SHAP detalhadas
```
por:
```
- **🩺 Escores Validados**: Framingham office-based e PREVENT (AHA/SBC), com decomposição exata por fator de risco
```

Trocar (linha 83):
```
- `POST /analise-completa` - Análise completa com SHAP
```
por:
```
- `POST /risco/rapido` - Framingham office-based (modo rápido, sem exames)
- `POST /risco/prevent` - PREVENT (modo completo, risco em 10 e 30 anos)
```

Trocar (linha 98):
```
3. Visualize análise de risco com explicações SHAP
```
por:
```
3. Visualize o risco calculado e a decomposição por fator de risco
```

Trocar (linha 115):
```
- **NumPy/Pandas** (processamento de dados)
```
por: (remover a linha — não são mais dependências do projeto, ver Step 1)

Trocar (linhas 139-141):
```
- **Geração de dados sintéticos** realistas
- **Algoritmos de Machine Learning** supervisionados
- **Explicabilidade de modelos** com técnicas SHAP
```
por:
```
- **Escores de risco cardiovascular** publicados e validados (Framingham, PREVENT)
- **Decomposição exata por fator** (log-linear, sem aproximação)
```

- [ ] **Step 4: Commit**

```bash
git add backend/requirements.txt README.md
git commit -m "chore: remove unused ML dependencies and SHAP/ML claims from docs"
```
