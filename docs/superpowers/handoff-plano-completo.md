# Handoff — Plano Completo de Frontend (CardioRisk)

**Data:** 2026-08-15
**Antecessor:** `handoff-front.md` (o hotfix que ele pedia **já foi feito** — ver abaixo).
**Próximo passo:** escrever `docs/superpowers/plans/<data>-cardiorisk-frontend.md` com
`superpowers:writing-plans` e executar. O design **já está fechado no spec** — não faça
brainstorming, não reabra a arquitetura de funil.

---

## 1. Estado real, verificado ao vivo hoje (não é suposição)

| Item | Estado | Evidência |
|---|---|---|
| Backend `cardioapi.roilabs.com.br` | 🟢 **no ar** | `GET /health` → `{"status":"healthy","version":"2.0.0"}` |
| `POST /risco/rapido` | 🟢 responde contrato novo | testado com payload real, retornou `tipo:"resultado"` + 5 contribuições |
| Frontend `cardiorisk.roilabs.com.br` | 🟢 no ar, redeployado | hash do bundle mudou `d43c35a7` → `d4b6e7ab` após o push |
| Contrato front↔back | 🟢 religado | commit `5998f71` |
| DNS | 🟢 resolvido | A record → `2.24.207.200` (EasyPanel) |

**Infra do backend (para referência, não mexer sem motivo):** EasyPanel, projeto
`sirius-crm` / serviço `cardio_api`, source GitHub `JeanZorzetti/cardio-risk-insight-hub`,
branch `main`, **Build Path `/backend`**. Push em `main` → redeploy automático (EasyPanel
para o backend, Vercel para o frontend). Trate `main` como produção.

### O que o hotfix (`5998f71`) já resolveu — não refaça

- `types/medical.ts` reescrito: `EntradaRapida`, `RespostaRisco`, `RespostaBloqueio`,
  `RespostaAvaliacao` (união discriminada), `Contribuicao`.
- `utils/api.ts`: `analisarPaciente`/`/analise-completa` mortos; agora
  `calcularRiscoRapido()` → `POST /risco/rapido`. Também foram deletadas
  `obterExemplosPacientes`, `validateAPIUrl`, `testConnection` (nenhuma tinha caller).
- `PatientForm.tsx`: coleta os campos certos do `EntradaRapida` — inclusive
  `usa_anti_hipertensivo`, `tabagismo`, `diabetes`, que **não existiam** no form antigo.
- `ResultsDisplay.tsx`: trata os dois ramos de `tipo`, renderiza `contribuicoes`
  dinamicamente (não por posição), mostra `risco_30_anos` e `risco_truncado`.
- `next.config.js`: corrigido fallback que assava `http://localhost:8000` no bundle de
  produção quando a env var não estava setada na Vercel.

---

## 2. 🔴 Achado aberto e urgente: a home mente em produção agora

O backend foi limpo de toda alegação de ML/SHAP (commits `764318a`, `79703c3`), mas **o
frontend continua anunciando tudo aquilo ao vivo**. Isto está no ar neste momento:

| Arquivo:linha | Texto em produção | Realidade |
|---|---|---|
| `frontend/app/page.tsx:41` | "Precisão do Modelo **94.2%**" | não existe modelo; número inventado |
| `frontend/app/page.tsx:48` | "Pacientes Analisados **1,000+**" | número inventado |
| `frontend/app/page.tsx:55` | "Explicabilidade **SHAP**" | SHAP foi deletado do backend |
| `frontend/app/page.tsx:93` | "Nossa IA analisa os dados usando algoritmos avançados" | não há IA; são escores log-lineares |
| `frontend/app/page.tsx:97` | "Receba análise detalhada com explicações SHAP" | idem |
| `frontend/app/page.tsx:112` | "Explicabilidade com SHAP" | idem |
| `frontend/app/page.tsx:30-31`, `layout.tsx:10-18` | "CardioCare AI … com Inteligência Artificial" | ver decisão de nome, §5 |

O spec (§"Explicabilidade: remover SHAP") manda isso sair de **código, README e API** — o
backend cumpriu, o frontend não. Além de ser falso, é exatamente o oposto do que a Camada 2
quer conquistar: credibilidade citável por LLM. **Trate como item 1 do plano.**

---

## 3. O trabalho: as três rotas do spec

Hoje só existe `/` (o formulário do modo rápido na raiz). Alvo do spec §"Dois modos":

| Rota | Existe? | O que é |
|---|---|---|
| `/calculadora` | ❌ (está na raiz `/`) | modo Rápido — Framingham office-based, `POST /risco/rapido` |
| `/calculadora/prevent` | ❌ **nada feito** | modo Completo — PREVENT, `POST /risco/prevent` |
| `/metodologia` | ❌ **nada feito** | Camada 2, peça de AEO — **não é opcional** |

Decisões que o plano precisa tomar explicitamente (o spec não fecha):

- **O que fica em `/`.** Vira landing/hub que aponta para as duas calculadoras, ou
  redireciona para `/calculadora`? Afeta canonical, sitemap e o H1 que ranqueia.
- **Reuso do formulário.** `PatientForm` hoje é hardcoded no modo rápido. O modo completo
  soma 4 campos (`colesterol_total`, `hdl`, `egfr`, `usa_estatina`) — a laziness manda
  parametrizar o mesmo componente por `modo`, não duplicar o arquivo. Confirme antes.
- **Faixa etária vs. conversão.** ⚠️ Achado: o form valida idade **18-120** (espelha o
  Pydantic), mas os escores só calculam **30-74** (Framingham) e **30-79** (PREVENT).
  Todo visitante de 18-29 anos preenche tudo e leva um `bloqueio` na cara. Para um funil
  que vive de tráfego orgânico, isso é decisão de produto, não detalhe: avisar antes de
  submeter, ou deixar a API bloquear? Decida no plano.

### Contrato do modo completo (ainda não implementado no front)

`POST /risco/prevent` — `EntradaPrevent` = todos os campos de `EntradaRapida` **+**:

```
colesterol_total: float (50-500, mg/dL)
hdl: float (10-150, mg/dL)
egfr: float (5-200, mL/min/1.73m²)
usa_estatina: bool
```

Resposta: **mesmo** `RespostaRisco | RespostaBloqueio` do modo rápido (os tipos em
`types/medical.ts` já servem — só falta a função cliente em `utils/api.ts`, espelhando
`calcularRiscoRapido`). Diferenças de comportamento:

- `risco_30_anos` vem preenchido **só** se idade ∈ 30-59; senão `null`. A API não diz por
  quê — se a UI precisar distinguir "não se aplica ao Framingham" de "idade fora de 30-59",
  derive do modo + idade enviada.
- `risco_truncado` é sempre `false` no PREVENT (o clamp de 1%-30% é só do Framingham).
- `contribuicoes` traz **9** fatores (os 5 do Framingham + Colesterol não-HDL, HDL,
  Função renal/eGFR, Uso de estatina). Renderize pelo `fator`, nunca por índice.

Fontes para citar na UI e na `/metodologia` (o backend já as devolve em `escore`/`fonte`):
D'Agostino RB et al. Circulation. 2008;117:743-753 · Khan SS et al. Circulation.
2024;149(6):430-449.

---

## 4. SEO/GEO/AEO — o canal único, hoje configurado só para uma rota

Isso é o **único** canal de aquisição do produto (spec §"Restrição determinante"), então
não é polimento de fim de plano:

- `app/sitemap.ts` lista **apenas** a raiz — precisa das rotas novas.
- `app/layout.tsx` tem `alternates.canonical: '/'` **global**, o que faria toda página nova
  canonicalizar para a home e se auto-desindexar. Cada rota precisa do próprio
  `metadata` (title, description, canonical, OG).
- Nenhuma página tem structured data. `/metodologia` e as calculadoras são candidatas
  óbvias a `MedicalWebPage` / `FAQPage` — é o que faz virar fonte citada em vez do MDCalc.
- Existe o skill `seo-geo-aeo-specialist` neste ambiente, com base de conhecimento própria.
  **Considere acioná-lo para a Camada 2** em vez de improvisar o conteúdo de AEO.

---

## 5. Decisão travando trabalho: o nome do produto

Risco aberto #3 do spec, ainda **não decidido** — e agora ele bloqueia mais coisa do que
antes, porque toda rota nova assa o nome em `<title>`, canonical, OG e H1. Trocar depois
custa retrabalho de SEO em várias páginas.

- `cardio-risk-insight-hub` = nome de repo gerado pelo Lovable.
- "CardioCare AI" colide com outras empresas **e** carrega o "AI" que o spec mandou remover.
- Aparece hoje em: `page.tsx:30`, `layout.tsx:10,17` e o H1 do `README.md`.

**Decisão do humano, não da IA.** Pergunte antes de escrever as páginas novas.

---

## 6. Armadilhas técnicas (todas encontradas na marra, economize o tempo)

1. **O build NÃO valida tipos.** `next.config.js` tem `typescript.ignoreBuildErrors: true`
   e `eslint.ignoreDuringBuilds: true`. `npm run build` passa verde com erro de tipo.
   Rode `npx tsc --noEmit` **sempre**, senão você deploya quebrado.
2. **`tsconfig.json` não está no repo** — é gerado pelo `next build`. Em clone limpo,
   `npx tsc --noEmit` cospe a tela de ajuda em vez de checar. Rode `npm run build` uma vez
   antes. (O `.gitignore` já foi corrigido para cobrir `.next/`, `__pycache__/`, `.venv/`,
   `tsconfig.tsbuildinfo` e `next-env.d.ts`.)
3. **`NEXT_PUBLIC_API_URL` provavelmente continua não setada na Vercel.** O fallback de
   produção que eu adicionei mascara isso. Setar a env var de verdade no painel é o
   conserto certo — o fallback é rede de segurança, não solução.
4. **CORS:** `backend/main.py:29` tem `"https://*.vercel.app"`, que **nunca casa** —
   Starlette faz match exato, não glob. Não atrapalha o domínio de produção, mas se o
   plano depender de testar em preview URL da Vercel, o preview vai tomar erro de CORS.
5. **`next@14.0.3` tem CVE conhecida** com patch disponível. Upgrade é mudança separada,
   não misture com este plano.
6. **Ledger de execução do backend não é versionado:** `.superpowers/sdd/` (histórico de
   decisões e rulings do plano de backend) é ignorado por design do próprio superpowers
   (`.superpowers/sdd/.gitignore` = `*`). Se precisar do porquê de alguma decisão do
   backend, ele só existe na máquina local — em
   `.superpowers/sdd/2026-08-14-cardiorisk-backend-scores/progress.md`.

---

## 7. Como validar (rode, não confie)

```bash
# backend em produção
curl https://cardioapi.roilabs.com.br/health

# contrato do modo completo, ao vivo
curl -X POST https://cardioapi.roilabs.com.br/risco/prevent \
  -H "Content-Type: application/json" \
  -d '{"idade":45,"sexo":"masculino","peso":75,"altura":1.70,"pas":120,
       "usa_anti_hipertensivo":false,"tabagismo":false,"diabetes":false,
       "dor_peito":false,"falta_ar":false,"fadiga":false,"tontura":false,
       "colesterol_total":200,"hdl":50,"egfr":90,"usa_estatina":false}'

# frontend
cd frontend && npm install && npm run build && npx tsc --noEmit

# backend local (venv já existe)
cd backend && ./.venv/Scripts/python.exe -m uvicorn main:app --port 8000
./.venv/Scripts/python.exe -m pytest test_scores.py   # 21 testes de referência
```

**Casos que a UI precisa sobreviver** (guard de segurança é requisito do spec, §"Guard de
segurança (não simplificável)"): `dor_peito:true` → `bloqueio/sintomas`; `idade:25` →
`bloqueio/faixa_etaria`; PREVENT com `idade:65` → `risco_30_anos: null`.

---

## 8. Ordem sugerida

1. Decidir o **nome** (§5) — bloqueia todo metadata.
2. **Matar as alegações falsas da home** (§2) — está no ar agora, é o mais barato e o mais
   urgente.
3. `superpowers:writing-plans` → `docs/superpowers/plans/<data>-cardiorisk-frontend.md`.
4. Executar: `/calculadora` → `/calculadora/prevent` → `/metodologia`, com metadata e
   sitemap de cada rota entrando junto com a rota, não depois.

**Fora de escopo** (spec §"Fora de escopo"): upload em lote, autenticação, billing, painel
B2B. A Camada 3 não começa antes de a Camada 1 provar tráfego — horizonte de 2-3 meses.

**Não versionado ainda:** limpeza do repo (spec §"Limpeza do repositório" — os
`api_medica_*.py`, CSVs sintéticos, `cardio-risk-insight-hub-main/` etc. continuam na raiz,
com a tag `curso-ia-aplicada` ainda não criada). Independente do frontend; não deixe virar
requisito deste plano.
