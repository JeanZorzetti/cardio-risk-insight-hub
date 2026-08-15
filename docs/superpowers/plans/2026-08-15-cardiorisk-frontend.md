# CardioRisk — Frontend das Três Rotas — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sair de uma única rota `/` (modo rápido, alegações falsas de IA/SHAP no ar) para as três rotas do spec — `/calculadora` (rápido), `/calculadora/prevent` (completo, PREVENT), `/metodologia` (AEO) — cada uma com metadata, canonical e structured data próprios.

**Architecture:** Extrai o corpo interativo de `app/page.tsx` para um componente cliente único `CalculadoraPage`, parametrizado por `modo: 'rapido' | 'completo'`, e monta cada rota como um Server Component fino que só define `metadata` e renderiza esse componente — porque `export const metadata` exige um Server Component, e `useState`/`react-hook-form` exigem `'use client'`; não dá para ter as duas coisas no mesmo arquivo. `/` vira um redirect 308 para `/calculadora` (via `next.config.js`), não uma página própria, para não competir por indexação com `/calculadora`.

**Tech Stack:** Next.js 14 App Router, TypeScript, react-hook-form, axios, Tailwind. Sem framework de teste no frontend (nenhum hoje no `package.json`) — verificação é `tsc --noEmit` + `next build` (que faz prerender estático) + checagem manual no browser, espelhando como o hotfix anterior (commit `5998f71`) já foi validado.

**Spec:** `docs/superpowers/specs/2026-08-14-cardiorisk-produtificacao-design.md`
**Handoff:** `docs/superpowers/handoff-plano-completo.md`

## Global Constraints

- Nome do produto: **CardioRisk** (decidido com o usuário nesta sessão — substitui "CardioCare AI" em todo lugar).
- Nenhuma menção a SHAP, ML ou "Inteligência Artificial"/"IA" em código, README ou UI (spec §"Explicabilidade: remover SHAP").
- Guard de segurança não é simplificável: sintomas (`dor_peito`, `falta_ar`, `fadiga`, `tontura`) ou idade fora da faixa validada de cada escore devem gerar bloqueio, nunca um percentual inventado. O backend já faz isso (`tipo: "bloqueio"`); o frontend só precisa continuar repassando essa resposta ao `ResultsDisplay`, que já trata os dois ramos — não reimplementar a regra no cliente.
- Faixas etárias validadas: Framingham office-based 30–74 anos, PREVENT 30–79 anos (`backend/scores/framingham_office.py:11`, `backend/scores/prevent.py:12`).
- Disclaimer de "não é diagnóstico" obrigatório em toda superfície que devolve resultado (posicionamento regulatório, RDC 657/2022).
- `next.config.js` tem `typescript.ignoreBuildErrors: true` e `eslint.ignoreDuringBuilds: true` — `npm run build` passa verde com erro de tipo. **Rodar `npx tsc --noEmit` em toda task**, não só no final.
- `tsconfig.json` não é versionado (gerado pelo `next build`); rodar `npm run build` uma vez antes de `tsc --noEmit` em um clone limpo.
- Fora de escopo (spec §"Fora de escopo" + handoff): upload em lote, autenticação, billing, painel B2B, upgrade do `next@14.0.3`, limpeza do repositório (`api_medica_*.py` etc.). Não misturar com este plano.

## Decisões desta sessão (não fechadas no spec/handoff)

1. **O que fica em `/`:** redirect 308 (`permanent: true`) para `/calculadora`, sem página própria. Uma "landing/hub" sem palavra-chave própria não ranquearia nada e ainda competiria por canonical com `/calculadora` — pior para SEO, mais código para manter. `/` sai do `sitemap.ts`; só rotas indexáveis entram.
2. **Reuso do formulário:** `PatientForm` ganha uma prop `modo: 'rapido' | 'completo'` e renderiza os 4 campos do PREVENT condicionalmente, em vez de duplicar o arquivo — como o handoff já recomendava.
3. **Faixa etária vs. conversão:** aviso inline, não bloqueante, abaixo do campo idade quando a idade sai da faixa válida do modo atual. Não impede o submit — a API já devolve um `bloqueio` tratável pelo `ResultsDisplay` existente, então duplicar a regra no cliente só para bloquear o botão seria trabalho redundante sem ganho de segurança.

---

### Task 1: Contrato do modo completo no cliente (tipos + função de API)

**Files:**
- Modify: `frontend/app/types/medical.ts`
- Modify: `frontend/app/utils/api.ts`

**Interfaces:**
- Produces: `EntradaPrevent` (tipo), `calcularRiscoPrevent(dados: EntradaPrevent): Promise<RespostaAvaliacao>` — usados pelas Tasks 2-4.

- [ ] **Step 1: Adicionar `EntradaPrevent` a `types/medical.ts`**

Adicionar logo após `EntradaRapida` (linha 16 hoje):

```ts
export interface EntradaPrevent extends EntradaRapida {
  colesterol_total: number
  hdl: number
  egfr: number
  usa_estatina: boolean
}
```

- [ ] **Step 2: Adicionar `calcularRiscoPrevent` a `utils/api.ts`**

Trocar o import do topo:

```ts
import { EntradaRapida, EntradaPrevent, RespostaAvaliacao, APIError } from '../types/medical'
```

E adicionar depois de `calcularRiscoRapido` (linha 55 hoje):

```ts
// Modo completo (PREVENT, com exames)
export const calcularRiscoPrevent = async (dados: EntradaPrevent): Promise<RespostaAvaliacao> => {
  const response = await api.post<RespostaAvaliacao>('/risco/prevent', dados)
  return response.data
}
```

- [ ] **Step 3: Verificar**

```bash
cd frontend && npx tsc --noEmit
```

Esperado: sem erros (nenhum caller usa `EntradaPrevent`/`calcularRiscoPrevent` ainda, então isso só confirma que os tipos novos são válidos).

- [ ] **Step 4: Commit**

```bash
git add frontend/app/types/medical.ts frontend/app/utils/api.ts
git commit -m "feat(frontend): add PREVENT contract to the API client"
```

---

### Task 2: `PatientForm` parametrizado por `modo`

**Files:**
- Modify: `frontend/app/components/PatientForm.tsx`

**Interfaces:**
- Consumes: `EntradaPrevent`, `calcularRiscoPrevent` (Task 1); `EntradaRapida`, `calcularRiscoRapido`, `RespostaAvaliacao` (já existentes).
- Produces: `PatientForm({ modo, onAnalysisComplete, isLoading, setIsLoading })` — usado pela Task 3.

- [ ] **Step 1: Trocar imports e a assinatura do componente**

```ts
import { useForm } from 'react-hook-form'
import { toast } from 'react-hot-toast'
import { Loader2, User, Activity, Stethoscope, FlaskConical } from 'lucide-react'
import { EntradaPrevent, RespostaAvaliacao } from '../types/medical'
import { calcularRiscoRapido, calcularRiscoPrevent } from '../utils/api'

const FAIXA_ETARIA: Record<'rapido' | 'completo', [number, number]> = {
  rapido: [30, 74],
  completo: [30, 79],
}

interface PatientFormProps {
  modo: 'rapido' | 'completo'
  onAnalysisComplete: (result: RespostaAvaliacao) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function PatientForm({ modo, onAnalysisComplete, isLoading, setIsLoading }: PatientFormProps) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<EntradaPrevent>({
    defaultValues: {
      idade: 45,
      sexo: 'masculino',
      peso: 75,
      altura: 1.70,
      pas: 120,
      usa_anti_hipertensivo: false,
      tabagismo: false,
      diabetes: false,
      dor_peito: false,
      falta_ar: false,
      fadiga: false,
      tontura: false,
      colesterol_total: 200,
      hdl: 50,
      egfr: 90,
      usa_estatina: false,
    }
  })

  const watchedData = watch()
  const bmi = watchedData.peso / (watchedData.altura ** 2)
  const [faixaMin, faixaMax] = FAIXA_ETARIA[modo]
  const idadeForaDaFaixa = watchedData.idade != null && (watchedData.idade < faixaMin || watchedData.idade > faixaMax)

  const onSubmit = async (data: EntradaPrevent) => {
    setIsLoading(true)
    try {
      const { colesterol_total, hdl, egfr, usa_estatina, ...dadosRapido } = data
      const result = modo === 'completo'
        ? await calcularRiscoPrevent(data)
        : await calcularRiscoRapido(dadosRapido)
      onAnalysisComplete(result)
      toast.success('Análise realizada com sucesso!')
    } catch (error: any) {
      console.error('Erro na análise:', error)
      toast.error(error.message || 'Erro ao realizar análise')
    } finally {
      setIsLoading(false)
    }
  }
```

Isso substitui o bloco atual do topo do arquivo (linhas 1-48). O destructure de `colesterol_total`/`hdl`/`egfr`/`usa_estatina` para fora de `dadosRapido` garante que o modo rápido nunca manda esses 4 campos pro endpoint errado, independente de o formulário tê-los registrado ou não.

- [ ] **Step 2: Adicionar o aviso de faixa etária, logo abaixo do erro de `idade` (linha 72 hoje)**

```tsx
            {errors.idade && <p className="text-red-500 text-xs mt-1">{errors.idade.message}</p>}
            {idadeForaDaFaixa && (
              <p className="text-yellow-700 text-xs mt-1">
                Este cálculo é validado para {faixaMin}–{faixaMax} anos. Fora dessa faixa, você recebe
                uma orientação para buscar avaliação médica, não um percentual de risco.
              </p>
            )}
```

- [ ] **Step 3: Adicionar a seção de exames laboratoriais, condicional a `modo === 'completo'`, entre a seção "Histórico e Fatores de Risco" e a seção "Sintomas" (hoje entre as linhas 186 e 188)**

```tsx
      {modo === 'completo' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
            <FlaskConical className="w-5 h-5" />
            Exames Laboratoriais
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Colesterol Total (mg/dL)
              </label>
              <input
                type="number"
                {...register('colesterol_total', {
                  required: 'Colesterol total é obrigatório',
                  min: { value: 50, message: 'Valor mínimo é 50 mg/dL' },
                  max: { value: 500, message: 'Valor máximo é 500 mg/dL' }
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.colesterol_total && <p className="text-red-500 text-xs mt-1">{errors.colesterol_total.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                HDL (mg/dL)
              </label>
              <input
                type="number"
                {...register('hdl', {
                  required: 'HDL é obrigatório',
                  min: { value: 10, message: 'Valor mínimo é 10 mg/dL' },
                  max: { value: 150, message: 'Valor máximo é 150 mg/dL' }
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.hdl && <p className="text-red-500 text-xs mt-1">{errors.hdl.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                eGFR (mL/min/1.73m²)
              </label>
              <input
                type="number"
                {...register('egfr', {
                  required: 'eGFR é obrigatório',
                  min: { value: 5, message: 'Valor mínimo é 5' },
                  max: { value: 200, message: 'Valor máximo é 200' }
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.egfr && <p className="text-red-500 text-xs mt-1">{errors.egfr.message}</p>}
            </div>
          </div>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              {...register('usa_estatina')}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="text-sm text-gray-700">Em uso de estatina</span>
          </label>
        </div>
      )}
```

- [ ] **Step 4: Verificar**

```bash
cd frontend && npx tsc --noEmit
```

Esperado: sem erros. `PatientForm` agora exige a prop `modo` — isso vai quebrar a compilação de `app/page.tsx` (que ainda não passa essa prop) até a Task 3; se `tsc` acusar erro em `app/page.tsx`, é esperado neste ponto intermediário — confirme que o único erro é esse e não algo dentro do próprio `PatientForm.tsx`.

- [ ] **Step 5: Commit**

```bash
git add frontend/app/components/PatientForm.tsx
git commit -m "feat(frontend): parametrize PatientForm by modo (rapido/completo)"
```

---

### Task 3: Extrair `CalculadoraPage` e criar a rota `/calculadora` (modo rápido)

**Files:**
- Create: `frontend/app/components/CalculadoraPage.tsx`
- Create: `frontend/app/calculadora/page.tsx`
- Delete: `frontend/app/page.tsx` (o conteúdo migra para `CalculadoraPage.tsx`)

**Interfaces:**
- Consumes: `PatientForm` (Task 2), `ResultsDisplay` (sem mudanças — já renderiza `contribuicoes` por `fator`, não por posição, então serve os 9 fatores do PREVENT sem alteração), `RespostaAvaliacao`.
- Produces: `CalculadoraPage({ modo })` — reusado pela Task 4 em `/calculadora/prevent`.

- [ ] **Step 1: Criar `frontend/app/components/CalculadoraPage.tsx`**

```tsx
'use client'

import { useState } from 'react'
import { Heart, Activity, Users, Brain, ChevronRight } from 'lucide-react'
import PatientForm from './PatientForm'
import ResultsDisplay from './ResultsDisplay'
import { RespostaAvaliacao } from '../types/medical'

interface CalculadoraPageProps {
  modo: 'rapido' | 'completo'
}

const CONTEUDO = {
  rapido: {
    titulo: 'CardioRisk — Calculadora de Risco Cardiovascular',
    subtitulo: 'Modo rápido: Framingham office-based, sem exames de laboratório',
    escoreLabel: 'Framingham office-based',
  },
  completo: {
    titulo: 'CardioRisk — Calculadora Completa (PREVENT)',
    subtitulo: 'Modo completo: PREVENT (AHA 2023 / SBC 2025), com exames laboratoriais',
    escoreLabel: 'PREVENT (AHA/SBC)',
  },
}

export default function CalculadoraPage({ modo }: CalculadoraPageProps) {
  const [analysisResult, setAnalysisResult] = useState<RespostaAvaliacao | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const conteudo = CONTEUDO[modo]

  const handleAnalysisComplete = (result: RespostaAvaliacao) => {
    setAnalysisResult(result)
    setIsLoading(false)
  }

  const handleNewAnalysis = () => {
    setAnalysisResult(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="gradient-medical text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-3 mb-4">
            <Heart className="w-10 h-10" />
            <div>
              <h1 className="text-3xl font-bold">{conteudo.titulo}</h1>
              <p className="text-blue-100">{conteudo.subtitulo}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="bg-white/10 backdrop-blur rounded-lg p-4 flex items-center gap-3">
              <Activity className="w-8 h-8 text-blue-200" />
              <div>
                <p className="text-blue-100 text-sm">Escore</p>
                <p className="text-2xl font-bold">{conteudo.escoreLabel}</p>
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4 flex items-center gap-3">
              <Users className="w-8 h-8 text-blue-200" />
              <div>
                <p className="text-blue-100 text-sm">Fontes</p>
                <p className="text-2xl font-bold">Circulation (AHA)</p>
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4 flex items-center gap-3">
              <Brain className="w-8 h-8 text-blue-200" />
              <div>
                <p className="text-blue-100 text-sm">Transparência</p>
                <p className="text-2xl font-bold">Fatores por peso</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {!analysisResult ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg card-shadow p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                  <Heart className="w-6 h-6 text-red-500" />
                  Dados do Paciente
                </h2>
                <PatientForm
                  modo={modo}
                  onAnalysisComplete={handleAnalysisComplete}
                  isLoading={isLoading}
                  setIsLoading={setIsLoading}
                />
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-white rounded-lg card-shadow p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Como Funciona</h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-sm font-bold">1</div>
                    <p className="text-sm text-gray-600">Preencha os dados vitais e clínicos do paciente</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-sm font-bold">2</div>
                    <p className="text-sm text-gray-600">Calculamos o risco com o escore {conteudo.escoreLabel}</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-sm font-bold">3</div>
                    <p className="text-sm text-gray-600">Receba o resultado com o peso de cada fator na sua pontuação</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg card-shadow p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Funcionalidades</h3>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2 text-sm text-gray-600">
                    <ChevronRight className="w-4 h-4 text-green-500" />
                    Análise de Risco Cardiovascular
                  </li>
                  <li className="flex items-center gap-2 text-sm text-gray-600">
                    <ChevronRight className="w-4 h-4 text-green-500" />
                    Contribuição de cada fator de risco
                  </li>
                  <li className="flex items-center gap-2 text-sm text-gray-600">
                    <ChevronRight className="w-4 h-4 text-green-500" />
                    Recomendações Personalizadas
                  </li>
                  <li className="flex items-center gap-2 text-sm text-gray-600">
                    <ChevronRight className="w-4 h-4 text-green-500" />
                    Visualizações Interativas
                  </li>
                </ul>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  <strong>Importante:</strong> Este sistema é uma ferramenta de apoio à decisão médica.
                  Sempre consulte um profissional de saúde qualificado.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <ResultsDisplay
            result={analysisResult}
            onNewAnalysis={handleNewAnalysis}
          />
        )}
      </main>

      <footer className="bg-gray-800 text-white py-8 mt-16">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2026 CardioRisk. Ferramenta de apoio à decisão médica — não substitui avaliação clínica.</p>
        </div>
      </footer>
    </div>
  )
}
```

- [ ] **Step 2: Criar `frontend/app/calculadora/page.tsx`**

```tsx
import type { Metadata } from 'next'
import CalculadoraPage from '../components/CalculadoraPage'

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'MedicalWebPage',
  name: 'Calculadora de Risco Cardiovascular — Framingham office-based',
  description: 'Calculadora gratuita de risco cardiovascular em 10 anos usando o escore Framingham office-based, sem exames de sangue.',
  url: 'https://cardiorisk.roilabs.com.br/calculadora',
  medicalAudience: { '@type': 'MedicalAudience', audienceType: 'Patient' },
  about: { '@type': 'MedicalCondition', name: 'Doença cardiovascular' },
}

export const metadata: Metadata = {
  title: 'Calculadora de Risco Cardiovascular Online e Gratuita | CardioRisk',
  description: 'Calcule seu risco cardiovascular em 10 anos com o escore Framingham office-based, sem precisar de exames de sangue. Grátis, instantâneo, com fonte publicada.',
  alternates: { canonical: '/calculadora' },
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    url: 'https://cardiorisk.roilabs.com.br/calculadora',
    title: 'Calculadora de Risco Cardiovascular Online e Gratuita | CardioRisk',
    description: 'Calcule seu risco cardiovascular em 10 anos com o escore Framingham office-based, sem precisar de exames de sangue.',
  },
}

export default function Page() {
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <CalculadoraPage modo="rapido" />
    </>
  )
}
```

- [ ] **Step 3: Apagar `frontend/app/page.tsx`**

```bash
rm frontend/app/page.tsx
```

(A rota `/` deixa de existir como página própria — vira redirect na Task 5. Sem esse `rm`, `/` e `/calculadora` renderizariam conteúdo duplicado.)

- [ ] **Step 4: Verificar tipos e build**

```bash
cd frontend && npx tsc --noEmit && npm run build
```

Esperado: sem erros de tipo; build lista `/calculadora` nas rotas geradas.

- [ ] **Step 5: Verificar o fluxo real no browser**

```bash
cd frontend && npm run dev
```

Abrir `http://localhost:3000/calculadora`, preencher o formulário (valores default já calculam um risco válido — idade 45 está dentro de 30-74) e confirmar que:
- o resultado renderiza com `risco_10_anos`, categoria e o gráfico de contribuições;
- marcar `dor_peito` e reenviar produz a tela de bloqueio ("Sintomas relatados"), não um percentual;
- mudar idade para `25` mostra o aviso amarelo de faixa etária abaixo do campo, sem travar o botão de enviar.

- [ ] **Step 6: Commit**

```bash
git add frontend/app/components/CalculadoraPage.tsx frontend/app/calculadora/page.tsx
git rm frontend/app/page.tsx
git commit -m "feat(frontend): move modo rápido to /calculadora with its own metadata"
```

---

### Task 4: Rota `/calculadora/prevent` (modo completo)

**Files:**
- Create: `frontend/app/calculadora/prevent/page.tsx`

**Interfaces:**
- Consumes: `CalculadoraPage` (Task 3).

- [ ] **Step 1: Criar `frontend/app/calculadora/prevent/page.tsx`**

```tsx
import type { Metadata } from 'next'
import CalculadoraPage from '../../components/CalculadoraPage'

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'MedicalWebPage',
  name: 'Calculadora de Risco Cardiovascular Completa — PREVENT',
  description: 'Calculadora de risco cardiovascular em 10 e 30 anos usando o escore PREVENT (AHA 2023 / SBC 2025), a partir de colesterol, HDL, eGFR e uso de estatina.',
  url: 'https://cardiorisk.roilabs.com.br/calculadora/prevent',
  medicalAudience: { '@type': 'MedicalAudience', audienceType: 'Patient' },
  about: { '@type': 'MedicalCondition', name: 'Doença cardiovascular' },
}

export const metadata: Metadata = {
  title: 'Calculadora de Risco Cardiovascular Completa (PREVENT) | CardioRisk',
  description: 'Calcule seu risco cardiovascular em 10 e 30 anos com o escore PREVENT (AHA 2023 / SBC 2025), a partir dos seus exames de colesterol, HDL e função renal.',
  alternates: { canonical: '/calculadora/prevent' },
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    url: 'https://cardiorisk.roilabs.com.br/calculadora/prevent',
    title: 'Calculadora de Risco Cardiovascular Completa (PREVENT) | CardioRisk',
    description: 'Calcule seu risco cardiovascular em 10 e 30 anos com o escore PREVENT (AHA 2023 / SBC 2025).',
  },
}

export default function Page() {
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <CalculadoraPage modo="completo" />
    </>
  )
}
```

- [ ] **Step 2: Verificar tipos e build**

```bash
cd frontend && npx tsc --noEmit && npm run build
```

Esperado: `/calculadora/prevent` aparece nas rotas geradas.

- [ ] **Step 3: Verificar o fluxo real no browser (com o backend de produção ou local)**

```bash
cd frontend && npm run dev
```

Abrir `http://localhost:3000/calculadora/prevent` e confirmar:
- os 4 campos extras (colesterol total, HDL, eGFR, estatina) aparecem, os do modo rápido continuam lá;
- submeter com os valores default (idade 45) retorna `risco_10_anos` **e** `risco_30_anos` preenchidos (idade 45 está em 30-59) e 9 fatores no gráfico de contribuições;
- mudar idade para `65` e reenviar retorna `risco_30_anos` nulo mas ainda calcula `risco_10_anos` (não é bloqueio — 65 está dentro de 30-79).

Validar o contrato bruto contra o backend de produção, se quiser confirmar independente da UI:

```bash
curl -X POST https://cardioapi.roilabs.com.br/risco/prevent \
  -H "Content-Type: application/json" \
  -d '{"idade":45,"sexo":"masculino","peso":75,"altura":1.70,"pas":120,
       "usa_anti_hipertensivo":false,"tabagismo":false,"diabetes":false,
       "dor_peito":false,"falta_ar":false,"fadiga":false,"tontura":false,
       "colesterol_total":200,"hdl":50,"egfr":90,"usa_estatina":false}'
```

- [ ] **Step 4: Commit**

```bash
git add frontend/app/calculadora/prevent/page.tsx
git commit -m "feat(frontend): add /calculadora/prevent (modo completo, PREVENT)"
```

---

### Task 5: Redirect de `/` para `/calculadora`

**Files:**
- Modify: `frontend/next.config.js`

- [ ] **Step 1: Adicionar `redirects()` a `next.config.js`**

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  env: {
    // ponytail: production fallback exists because Vercel's NEXT_PUBLIC_API_URL was unset,
    // baking `localhost:8000` into every visitor's browser bundle. Set the real env var in
    // Vercel and this fallback stops mattering.
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === 'production' ? 'https://cardioapi.roilabs.com.br' : 'http://localhost:8000'),
  },
  async redirects() {
    return [
      { source: '/', destination: '/calculadora', permanent: true },
    ]
  },
}

module.exports = nextConfig
```

- [ ] **Step 2: Verificar**

```bash
cd frontend && npm run build && npm run start
```

Em outro terminal:

```bash
curl -sI http://localhost:3000/ | head -5
```

Esperado: `HTTP/1.1 308` (ou 307 em dev) com `location: /calculadora`.

- [ ] **Step 3: Commit**

```bash
git add frontend/next.config.js
git commit -m "feat(frontend): redirect / to /calculadora"
```

---

### Task 6: Rota `/metodologia` (Camada 2, peça de AEO)

**Files:**
- Create: `frontend/app/metodologia/page.tsx`

- [ ] **Step 1: Criar `frontend/app/metodologia/page.tsx`**

```tsx
import type { Metadata } from 'next'
import Link from 'next/link'
import { Heart } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Metodologia — Como calculamos o risco cardiovascular | CardioRisk',
  description: 'Quais escores usamos (Framingham office-based e PREVENT), de onde vêm os coeficientes, como a contribuição de cada fator é calculada, e para quem os resultados não se aplicam.',
  alternates: { canonical: '/metodologia' },
  openGraph: {
    type: 'article',
    locale: 'pt_BR',
    url: 'https://cardiorisk.roilabs.com.br/metodologia',
    title: 'Metodologia — Como calculamos o risco cardiovascular | CardioRisk',
    description: 'Quais escores usamos, de onde vêm os coeficientes, e as limitações de cada um.',
  },
}

const faq = [
  {
    pergunta: 'Quais escores de risco cardiovascular o CardioRisk usa?',
    resposta:
      "Dois: o Framingham office-based (D'Agostino RB et al., Circulation, 2008) no modo rápido, que não exige exames de sangue, e o PREVENT (Khan SS et al., Circulation, 2024), recomendado pela atualização de 2025 da diretriz da SBC, no modo completo.",
  },
  {
    pergunta: 'Por que existem dois modos de cálculo?',
    resposta:
      "O PREVENT exige a taxa de filtração glomerular estimada (eGFR), um dado de exame que a maioria das pessoas não tem em mãos. Para não inventar esse número, oferecemos um modo rápido com o Framingham office-based (sem exames) e um modo completo com PREVENT (com exames), cada um validado e citado separadamente.",
  },
  {
    pergunta: 'Como é calculada a contribuição de cada fator de risco?',
    resposta:
      'Os dois escores são modelos de risco proporcional (Cox) log-lineares. A contribuição de cada fator é β·(x − x_referência): o coeficiente publicado do fator multiplicado pela diferença entre o valor informado e um perfil de referência da mesma idade e sexo. A soma das contribuições é exatamente o log-risco relativo — não é uma aproximação.',
  },
  {
    pergunta: 'Para quem os resultados não se aplicam?',
    resposta:
      'Para menores de 30 anos (fora da faixa de validação de ambos os escores), para maiores de 74 anos no modo rápido ou 79 no modo completo, e para quem relata sintomas atuais como dor no peito ou falta de ar — nesses casos a ferramenta não estima risco e orienta buscar avaliação médica, porque os escores valem para prevenção primária em pessoas assintomáticas.',
  },
  {
    pergunta: 'O CardioRisk substitui uma consulta médica?',
    resposta:
      'Não. É uma ferramenta de apoio à triagem e priorização, não um diagnóstico. O resultado deve ser interpretado por um profissional de saúde qualificado, junto com exame clínico e, quando indicado, exames complementares.',
  },
]

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: faq.map((item) => ({
    '@type': 'Question',
    name: item.pergunta,
    acceptedAnswer: {
      '@type': 'Answer',
      text: item.resposta,
    },
  })),
}

export default function MetodologiaPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <header className="gradient-medical text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-3">
            <Heart className="w-10 h-10" />
            <div>
              <h1 className="text-3xl font-bold">Metodologia</h1>
              <p className="text-blue-100">Como o CardioRisk calcula o risco cardiovascular</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-3xl space-y-8">
        <section className="bg-white rounded-lg card-shadow p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-3">Os dois escores</h2>
          <p className="text-gray-700 mb-4">
            O CardioRisk não usa machine learning nem um modelo proprietário. Usa dois escores de
            risco cardiovascular validados e publicados em periódicos revisados por pares:
          </p>
          <div className="space-y-4">
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold text-gray-800">Framingham office-based — modo rápido</h3>
              <p className="text-sm text-gray-600 mt-1">
                Variante do Escore de Risco Global que não exige exames de sangue: idade, sexo, IMC,
                pressão sistólica, tabagismo, diabetes e uso de anti-hipertensivo. Válido para 30–74
                anos. Fonte: D&apos;Agostino RB et al. <em>General Cardiovascular Risk Profile for
                Use in Primary Care: The Framingham Heart Study.</em> Circulation. 2008;117:743-753.
              </p>
            </div>
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold text-gray-800">PREVENT — modo completo</h3>
              <p className="text-sm text-gray-600 mt-1">
                Adotado pela atualização de 2025 da diretriz de prevenção cardiovascular da SBC em
                substituição ao Framingham. Soma colesterol total, HDL, eGFR e uso de estatina, e
                estima risco em 10 e 30 anos sem usar raça como variável. Válido para 30–79 anos.
                Fonte: Khan SS et al. <em>Development and Validation of the American Heart
                Association&apos;s PREVENT Equations.</em> Circulation. 2024;149(6):430-449.
              </p>
            </div>
          </div>
        </section>

        <section className="bg-white rounded-lg card-shadow p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-3">Como calculamos a contribuição de cada fator</h2>
          <p className="text-gray-700">
            Ambos os escores são modelos de risco proporcional (Cox) log-lineares: o log-risco é uma
            soma ponderada dos fatores de entrada. Isso torna a decomposição exata — a contribuição de
            cada fator é <code className="bg-gray-100 px-1 rounded">β · (x − x_referência)</code>, o
            coeficiente publicado do fator multiplicado pela diferença entre o valor informado e um
            perfil de referência da mesma idade e sexo. Não usamos SHAP nem qualquer método de
            aproximação: o modelo já é linear no log-risco, então a decomposição exata sai direto da
            fórmula publicada.
          </p>
        </section>

        <section className="bg-white rounded-lg card-shadow p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-3">Guard de segurança e limitações</h2>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            <li>
              Os dois escores valem para <strong>prevenção primária em pessoas assintomáticas</strong>.
              Se você relata dor no peito, falta de ar, fadiga ou tontura, a ferramenta não calcula um
              percentual — orienta buscar avaliação médica.
            </li>
            <li>
              Fora da faixa etária validada de cada escore (30–74 no modo rápido, 30–79 no modo
              completo), o resultado também é bloqueado em vez de extrapolado.
            </li>
            <li>
              O modo rápido não usa exames de sangue — é uma triagem inicial. O modo completo, com
              colesterol, HDL e eGFR, é mais preciso.
            </li>
          </ul>
        </section>

        <section className="bg-white rounded-lg card-shadow p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Perguntas frequentes</h2>
          <div className="space-y-5">
            {faq.map((item) => (
              <div key={item.pergunta}>
                <h3 className="font-semibold text-gray-800">{item.pergunta}</h3>
                <p className="text-sm text-gray-600 mt-1">{item.resposta}</p>
              </div>
            ))}
          </div>
        </section>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link
            href="/calculadora"
            className="flex-1 text-center bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Calcular no modo rápido
          </Link>
          <Link
            href="/calculadora/prevent"
            className="flex-1 text-center bg-white border border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Calcular no modo completo (PREVENT)
          </Link>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <strong>Importante:</strong> O CardioRisk é uma ferramenta de apoio à triagem, não um
            diagnóstico. Consulte um profissional de saúde qualificado para interpretar o resultado.
          </p>
        </div>
      </main>
    </div>
  )
}
```

- [ ] **Step 2: Verificar**

```bash
cd frontend && npx tsc --noEmit && npm run build
```

Esperado: `/metodologia` aparece nas rotas estáticas geradas.

- [ ] **Step 3: Commit**

```bash
git add frontend/app/metodologia/page.tsx
git commit -m "feat(frontend): add /metodologia (Camada 2, AEO)"
```

---

### Task 7: Atualizar `sitemap.ts`

**Files:**
- Modify: `frontend/app/sitemap.ts`

- [ ] **Step 1: Substituir o conteúdo do arquivo**

```ts
import type { MetadataRoute } from 'next'

const BASE = 'https://cardiorisk.roilabs.com.br'

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date()
  return [
    { url: `${BASE}/calculadora`, lastModified, changeFrequency: 'monthly', priority: 1 },
    { url: `${BASE}/calculadora/prevent`, lastModified, changeFrequency: 'monthly', priority: 1 },
    { url: `${BASE}/metodologia`, lastModified, changeFrequency: 'monthly', priority: 0.8 },
  ]
}
```

`/` sai do sitemap de propósito — é um redirect 308 (Task 5), não uma URL indexável própria.

- [ ] **Step 2: Verificar**

```bash
cd frontend && npm run build && npm run start
```

```bash
curl -s http://localhost:3000/sitemap.xml
```

Esperado: XML com as 3 URLs, sem `/`.

- [ ] **Step 3: Commit**

```bash
git add frontend/app/sitemap.ts
git commit -m "feat(frontend): list the three real routes in sitemap.ts"
```

---

### Task 8: Verificação final ponta a ponta

**Files:** nenhum (só verificação).

- [ ] **Step 1: Build + typecheck limpos**

```bash
cd frontend && npm run build && npx tsc --noEmit
```

Esperado: build verde, `tsc` sem output.

- [ ] **Step 2: Rodar o backend local e o frontend juntos**

```bash
cd backend && ./.venv/Scripts/python.exe -m uvicorn main:app --port 8000
```

Em outro terminal:

```bash
cd frontend && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

- [ ] **Step 3: Percorrer o golden path em um browser real** (usar as ferramentas de browser disponíveis — ex. Playwright — ou verificação manual)

- `http://localhost:3000/` → redireciona para `/calculadora`.
- `/calculadora`: preencher e enviar com valores default → resultado com `risco_10_anos`, 5 contribuições, sem menção a IA/SHAP em lugar nenhum da página.
- `/calculadora/prevent`: preencher e enviar → resultado com `risco_10_anos` e `risco_30_anos`, 9 contribuições.
- `/calculadora/prevent` com idade 65 → `risco_30_anos` ausente/nulo, `risco_10_anos` presente (não é bloqueio).
- Qualquer um dos dois modos com `dor_peito` marcado → tela de bloqueio "Sintomas relatados", nunca um percentual.
- `/metodologia`: conteúdo carrega, os dois botões levam para as calculadoras.
- `view-source:` em cada rota nova → confirmar `<title>`, `<link rel="canonical">` e o `<script type="application/ld+json">` corretos por página (não o canonical global de `/` herdado).

- [ ] **Step 4: Confirmar que nenhuma alegação falsa sobrevive**

```bash
cd frontend && grep -rn "SHAP\|Inteligência Artificial\|CardioCare" app/ || echo "limpo"
```

Esperado: `limpo` (nenhuma ocorrência).

- [ ] **Step 5: Commit final, se houver ajustes deste passo de verificação**

```bash
git add -A
git commit -m "chore(frontend): fix issues found in end-to-end verification"
```

(Pular este commit se a verificação não exigiu nenhuma mudança.)

---

## O que fica de fora deste plano (propositalmente)

- `NEXT_PUBLIC_API_URL` na Vercel — setar o valor real no painel continua pendente (armadilha #3 do handoff); o fallback do `next.config.js` já cobre produção, então não bloqueia este plano.
- CORS com `https://*.vercel.app` (armadilha #4) — só importa se alguém for testar em preview URL da Vercel.
- Upgrade do `next@14.0.3` (CVE conhecida) — mudança separada, deliberadamente fora de escopo.
- Limpeza do repositório (`api_medica_*.py`, CSVs, `cardio-risk-insight-hub-main/`, tag `curso-ia-aplicada`) — spec §"Limpeza do repositório", independente do frontend.
- Refino de copy de AEO por um especialista (skill `seo-geo-aeo-specialist`) — o conteúdo de `/metodologia` desta plano é factual e correto, mas uma segunda passada de otimização para citação por LLM é trabalho incremental, não bloqueante.
