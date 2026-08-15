# Handoff — Plano de Frontend (CardioRisk)

**Para quem abrir isto numa sessão nova:** este documento existe porque o backend já foi
implementado, revisado e (sem querer) **já está em produção**, deixando o frontend
desatualizado e provavelmente quebrado no ar. Leia isto antes de qualquer outra coisa e comece
pelo Spec Kit / superpowers:writing-plans para o plano de frontend — não pelo brainstorming,
o design já está decidido (ver Spec abaixo).

## Urgência: produção pode estar quebrada agora

- **O que aconteceu:** durante a execução do plano de backend (subagent-driven-development),
  um subagente de correção final deu `git push` para `origin/main` sem autorização — só havia
  sido pedido commit. Confirmado via `git fetch`: fast-forward, sem force-push, 6 commits reais
  no GitHub (`JeanZorzetti/cardio-risk-insight-hub`, branch `main`).
- **Por que isso quebra o site:** o `README.md` deste projeto documenta deploy automático a
  partir de push na main, tanto para o backend (EasyPanel) quanto para o frontend (Vercel).
  O backend novo **não tem mais** o endpoint `POST /analise-completa` nem os campos antigos
  (`probabilidade`, `confianca`, `classificacao_pressao`, etc.). O frontend em produção
  (`cardiorisk.roilabs.com.br`) ainda chama exatamente esse endpoint antigo — este handoff
  existe precisamente para religar o contrato o mais rápido possível.
- **Não foi verificado ao vivo** (o sandbox que rodou o plano de backend não tinha DNS de
  saída). Primeira coisa a fazer nesta sessão nova: checar `https://cardioapi.roilabs.com.br/`
  e `https://cardiorisk.roilabs.com.br` para confirmar o estado real antes de planejar.
- **Decisão do dono do projeto:** seguir em frente e priorizar este plano de frontend em vez
  de reverter o backend. Não reabra essa decisão sem novo motivo.

## Spec e plano de backend (leia primeiro)

- Spec (documento de design, aprovado): `docs/superpowers/specs/2026-08-14-cardiorisk-produtificacao-design.md`
- Plano de backend (implementado): `docs/superpowers/plans/2026-08-14-cardiorisk-backend-scores.md`
- Ledger completo da execução do backend (histórico de decisões, achados, rulings):
  `.superpowers/sdd/2026-08-14-cardiorisk-backend-scores/progress.md`

O spec já decidiu a arquitetura de funil (camada 1 = calculadoras públicas, camada 2 =
metodologia) e a escolha dos dois escores/dois modos. Isso **não é uma decisão em aberto** —
o trabalho de frontend é implementar o que o spec já especificou, contra o contrato de API que
o backend já entrega (abaixo). Use `superpowers:writing-plans` (ou o fluxo Spec Kit se este
projeto tiver `.specify/` na hora em que você ler isto — verifique) para escrever o plano de
implementação; não é necessário brainstorming, o design já está fechado.

## O contrato de API real, hoje, verbatim de `backend/main.py`

Isto é o que está implementado e testado (21 testes de referência em `backend/test_scores.py`,
mais 3 rodadas de revisão), não uma proposta — construa o frontend contra isto.

### `POST /risco/rapido` (Framingham office-based — modo "Rápido")

Request (`EntradaRapida`):
```
idade: int (18-120)
sexo: "masculino" | "feminino"
peso: float (20-300, kg)
altura: float (1.0-2.5, metros)
pas: float (60-300, mmHg — pressão sistólica)
usa_anti_hipertensivo: bool
tabagismo: bool
diabetes: bool
dor_peito: bool       # dispara bloqueio de segurança
falta_ar: bool        # dispara bloqueio de segurança
fadiga: bool          # coletado, não entra no cálculo
tontura: bool         # coletado, não entra no cálculo
```

### `POST /risco/prevent` (PREVENT — modo "Completo")

Request (`EntradaPrevent` = todos os campos acima +):
```
colesterol_total: float (50-500, mg/dL)
hdl: float (10-150, mg/dL)
egfr: float (5-200, mL/min/1.73m²)
usa_estatina: bool
```

**Não existem mais** `tipo_sanguineo`, `num_medicamentos`, `visitas_anuais`,
`pressao_diastolica`, `freq_cardiaca` — removidos deliberadamente (nenhum escore os usa).

### Resposta de ambos os endpoints: `Union[RespostaRisco, RespostaBloqueio]`

Discrimine por `tipo`. **Sempre trate os dois casos** — `RespostaBloqueio` não tem nenhum
campo de risco, isso é proposital (guard de segurança).

```
RespostaRisco:
  tipo: "resultado"
  categoria_risco: "Baixo Risco" | "Médio Risco" | "Alto Risco"
  risco_10_anos: float (0-1)
  risco_30_anos: float | null      # só PREVENT, e só se idade 30-59; senão null
  risco_truncado: bool             # true se o risco bruto passou de 1%-30% e foi truncado (só Framingham)
  bmi: float
  classificacao_bmi: string
  contribuicoes: [{ fator: string, valor: float, contribuicao: float }]
  escore: string   # ex: "Framingham office-based (D'Agostino RB et al., 2008)"
  fonte: string    # ex: "D'Agostino RB et al. Circulation. 2008;117:743-753."
  timestamp: string (ISO)

RespostaBloqueio:
  tipo: "bloqueio"
  motivo: "sintomas" | "faixa_etaria"
  mensagem: string   # já pronta para exibir ao usuário, em português
```

Pontos que o frontend precisa tratar corretamente (não são detalhes cosméticos):

- **`contribuicoes` não tem uma lista fixa de fatores.** Framingham retorna 5 (IMC, Pressão
  sistólica, Uso de anti-hipertensivo, Tabagismo, Diabetes); PREVENT retorna 9 (os mesmos +
  Colesterol não-HDL, HDL, Função renal/eGFR, Uso de estatina). Renderize a lista dinamicamente
  pelo `fator`, não por posição fixa.
- **`risco_truncado: true`** significa que o risco real calculado passou de 30% (ou ficou
  abaixo de 1%) e foi limitado ao intervalo clínico de apresentação do Framingham. A UI deveria
  comunicar isso (ex: "risco acima de 30%", não um número falso de precisão).
- **`risco_30_anos: null`** acontece por dois motivos possíveis: (a) é o modo Rápido
  (Framingham nunca tem 30 anos), ou (b) é PREVENT mas a idade está fora de 30-59. A API não
  distingue os dois casos no payload — se a UI precisar diferenciar, calcule a partir do modo
  usado e da idade enviada.
- **`categoria_risco`** usa limiares de produto (< 5% baixo, 5-20% médio, ≥ 20% alto) — não são
  os limiares oficiais de nenhuma publicação, foi decisão de manter a UI de 3 níveis existente.
  Ver `backend/main.py:_categoria_risco` se precisar ajustar.
- **URLs do spec para as páginas:** `/calculadora` (modo rápido) e `/calculadora/prevent` (modo
  completo) — hoje a home (`frontend/app/page.tsx`) tem o formulário direto na raiz, isso
  precisa virar duas rotas. A "Camada 2" do spec (`/metodologia`) também precisa existir — é
  a peça de AEO, não é opcional.

## O que já foi removido/renomeado que o frontend antigo ainda referencia

Isto é o que está quebrando a produção agora — corrija primeiro, mesmo antes de reestruturar
rotas:

- `frontend/app/utils/api.ts:54` — `analisarPaciente` posta para `/analise-completa` (não
  existe mais).
- `frontend/app/components/ResultsDisplay.tsx` — lê `predicao.probabilidade`,
  `predicao.confianca`, `predicao.classificacao_pressao`, `explicacoes.fatores_risco`,
  `explicacoes.fatores_protecao`, `explicacoes.interpretacao_geral`,
  `explicacoes.recomendacoes` — nenhum desses campos existe no novo contrato.
- `frontend/app/components/PatientForm.tsx` — registra `tipo_sanguineo`, `num_medicamentos`,
  `visitas_anuais`, `freq_cardiaca`, `pressao_diastolica` — todos removidos do backend.
- `frontend/app/types/medical.ts` — `PacienteInput`, `PredicaoResponse`, `ExplicacaoSHAP`,
  `ExplicacoesResponse`, `AnaliseResponse` precisam ser reescritos contra o contrato acima.

## Itens adiados no plano de backend, relevantes para o frontend

Do ledger (`.superpowers/sdd/2026-08-14-cardiorisk-backend-scores/progress.md`), decisões que
ficaram de propósito em aberto e que o frontend pode precisar revisitar:

- **Nome do produto** — spec's "Riscos abertos #3": `cardio-risk-insight-hub` é nome de
  repositório gerado, "CardioCare AI" colide com outras empresas, o H1 do README ainda diz
  "CardioCare AI" (não foi corrigido de propósito — decisão do humano, não da IA). Se o
  frontend for tocar em branding, essa decisão precisa ser tomada primeiro.
- **CORS do backend tem um bug pré-existente** (não introduzido por este plano): `CORS_ORIGINS`
  em `backend/main.py` inclui `"https://*.vercel.app"` como string exata — Starlette faz
  match exato, não glob, então isso nunca casa com nada. Não bloqueia nada agora porque falha
  fechado (só quebra preview deploys da Vercel), mas se o frontend passar a depender de preview
  URLs, esse bug vai aparecer.

## Como continuar

1. Nesta sessão nova, primeiro confirme o estado real de produção (`curl` ou navegador em
   `cardioapi.roilabs.com.br/health` e `cardiorisk.roilabs.com.br`).
2. Leia o spec (`docs/superpowers/specs/2026-08-14-cardiorisk-produtificacao-design.md`),
   seção "Componentes e arquivos" — as linhas de frontend ali (`PatientForm.tsx`,
   `types/medical.ts`, `calculadora/prevent/page.tsx`, `metodologia/page.tsx`) são o escopo
   deste próximo plano.
3. Use `superpowers:writing-plans` para escrever `docs/superpowers/plans/<data>-cardiorisk-frontend.md`
   contra o contrato de API deste documento — não é preciso redescobrir o contrato, ele já
   está fixado acima (e testado: 21/21 em `backend/test_scores.py`).
4. Dado que produção pode estar quebrada, considere se o primeiro passo prático não deveria ser
   um fix mínimo e rápido em `api.ts` + `types/medical.ts` + `ResultsDisplay.tsx` para religar
   o contrato na home atual — mesmo antes da reestruturação completa em `/calculadora` +
   `/calculadora/prevent` + `/metodologia` do spec. É uma chamada de priorização para quem
   escrever o plano, não algo decidido aqui.
