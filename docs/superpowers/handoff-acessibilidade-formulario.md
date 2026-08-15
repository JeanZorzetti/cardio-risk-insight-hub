# Handoff — Acessibilidade do formulário (texto digitado invisível)

**Data:** 2026-08-15
**Antecessor:** `handoff-plano-completo.md` (o plano das três rotas **já foi executado** —
`docs/superpowers/plans/2026-08-15-cardiorisk-frontend.md`, commits `6a75736`..`fc9ad41`).
**Escopo deste handoff:** um bug P0 de contraste que apaga o texto digitado, mais os achados de
acessibilidade encontrados na mesma varredura do formulário.

Tudo abaixo foi **verificado ao vivo em produção** (`cardiorisk.roilabs.com.br`) via browser real,
não é dedução a partir do código.

---

## 1. 🔴 O bug: em dark mode, o texto digitado fica invisível

Quem visita o site com o sistema operacional/navegador em **modo escuro** vê os campos do
formulário aparentemente vazios — mas os valores estão lá. É texto branco sobre fundo branco.

Isso atinge **todos os campos de digitação** de `/calculadora` e `/calculadora/prevent`, incluindo
o `<select>` de sexo (a opção não destacada some no dropdown nativo). Como o formulário é a única
superfície de conversão do produto e o canal de aquisição é busca orgânica, o visitante preenche
às cegas ou desiste — sem nunca reportar nada.

### Evidência (produção, medida no navegador)

| Medida | Valor |
|---|---|
| `input[type=number]` valor real | `"45"` (o campo tem conteúdo) |
| `background-color` do input | `rgb(255, 255, 255)` |
| `color` do input, modo claro | `rgb(0, 0, 0)` ✅ |
| `color` do input, com `--foreground-rgb` em modo escuro | `rgb(255, 255, 255)` ❌ |
| Contraste resultante | **1:1 — invisível** |
| `color-scheme` declarado no `:root` | `normal` (nenhum) |

---

## 2. Causa raiz — e por que ela não é nos inputs

A cadeia, inteira, tem três elos. Os três precisam ser entendidos antes de corrigir, senão o fix
vai no lugar errado:

1. **`frontend/app/globals.css:11-17`** tem um bloco `@media (prefers-color-scheme: dark)` que
   troca `--foreground-rgb` para `255, 255, 255`.
2. **`globals.css:19-27`** aplica isso em `body { color: rgb(var(--foreground-rgb)) }`.
3. **O preflight do Tailwind** define `color: inherit` para `input`/`select`/`textarea`. Os campos
   em `PatientForm.tsx` não têm nenhuma classe `text-*` nem `bg-*` própria — então herdam o branco
   do `body`.

O que fecha a armadilha: **os contêineres nunca escurecem junto.** Eles são `bg-white` /
`bg-gray-50` fixos (`CalculadoraPage.tsx`, os cards do formulário). O bloco dark do `globals.css`
só inverte a cor **do texto herdado**, nunca o fundo. Ou seja: esse bloco nunca foi capaz de
produzir um tema escuro funcional — ele só consegue produzir texto invisível.

Por isso os rótulos ("Idade", "Sexo") continuam legíveis: eles têm `text-gray-700` explícito. Só
quem depende da cor herdada some. É boilerplate do `create-next-app` que sobreviveu e briga com um
design que é fixo em claro.

---

## 3. O fix recomendado — um arquivo, ~7 linhas removidas

Corrigir no `globals.css`, não nos inputs. Todos os campos passam por lá; é o único ponto por onde
qualquer elemento futuro que dependa de cor herdada também passa.

```css
/* frontend/app/globals.css */
:root {
  color-scheme: light;          /* ADICIONAR */
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 214, 219, 220;
  --background-end-rgb: 255, 255, 255;
}

/* REMOVER o bloco inteiro — nunca produziu um tema escuro utilizável,
   só texto invisível sobre contêineres que continuam claros:

@media (prefers-color-scheme: dark) { ... }
*/
```

`color-scheme: light` não é enfeite: sem ele, o Chrome em modo escuro renderiza os controles
nativos (o popup do `<select>`, autofill, scrollbars) com paleta escura por conta própria, e o
`<select>` volta a sumir mesmo depois do resto corrigido.

**O que NÃO fazer:** sair colando `text-gray-900` nos 9 campos. Trata o sintoma, são 9 edições em
vez de 1, e deixa a armadilha armada para o próximo componente que alguém adicionar.

**Se um dia quiserem dark mode de verdade:** é com variantes `dark:` do Tailwind aplicadas aos
contêineres (`dark:bg-gray-900`, `dark:text-gray-100`, etc.), não com override de cor no `body`.
É projeto separado, não este.

---

## 4. Achados de acessibilidade adjacentes (mesma varredura)

Encontrados no mesmo formulário, verificados em produção. Não bloqueiam o P0, mas estão todos no
arquivo que quem pegar isso já vai abrir.

| # | Achado | Evidência | Severidade |
|---|---|---|---|
| A | **Rótulos não associados aos campos.** `8` de `16` controles em `/calculadora/prevent` (e `5` de `12` em `/calculadora`) não têm nome acessível: `idade`, `sexo`, `pas`, `peso`, `altura`, `colesterol_total`, `hdl`, `egfr`. Existem `0` `label[for]` e `0` `id` na página. Leitor de tela anuncia "campo de edição" sem dizer qual. Clicar no rótulo também não foca o campo. | medido no DOM | **Alta** (WCAG 1.3.1 / 3.3.2) |
| B | **Contraste do texto de erro insuficiente.** `text-red-500` (`#ef4444`) sobre branco = **3.76:1**; o mínimo AA para texto normal é 4.5:1. Trocar por `text-red-600` (`#dc2626`) = **4.83:1**, passa. | calculado | Média (WCAG 1.4.3) |
| C | **Erros não são anunciados.** Nenhum campo tem `aria-invalid`, os `<p>` de erro não têm `role="alert"` nem estão ligados por `aria-describedby`. Quem usa leitor de tela submete e não fica sabendo o que falhou. | inspeção do DOM | Média (WCAG 3.3.1) |
| D | Texto de erro em `text-xs` (12px). Não é falha WCAG por si só, mas é pequeno para mensagem de validação. | — | Baixa |

Os **7 checkboxes estão corretos** — usam `<label>` envolvendo o input, o que já cria associação
implícita. Não mexer neles.

O aviso de faixa etária (`text-yellow-700`, 4.93:1) **passa** em contraste. Não é achado.

### Correção do achado A (o padrão a repetir)

Hoje, em `PatientForm.tsx` (linhas 75-85, 97-102, 119-129, 135-146, 152-163, 217-227, 233-243,
249-259), o padrão é rótulo e campo como irmãos, sem ligação:

```tsx
<label className="block text-sm font-medium text-gray-700 mb-1">Idade</label>
<input type="number" {...register('idade', { ... })} className="..." />
```

O conserto é `htmlFor` + `id` casados (e, de brinde, resolve C junto):

```tsx
<label htmlFor="idade" className="block text-sm font-medium text-gray-700 mb-1">Idade</label>
<input
  id="idade"
  type="number"
  aria-invalid={errors.idade ? 'true' : undefined}
  aria-describedby={errors.idade ? 'idade-erro' : undefined}
  {...register('idade', { ... })}
  className="..."
/>
{errors.idade && <p id="idade-erro" role="alert" className="text-red-600 text-xs mt-1">{errors.idade.message}</p>}
```

---

## 5. Como validar (rode, não confie)

O P0 **não reproduz** com o SO em modo claro — é o motivo de ter passado por toda a verificação do
plano anterior, inclusive checagens em browser real. Force o modo escuro:

```js
// Playwright
const ctx = await browser.newContext({ colorScheme: 'dark' })
```

Ou, no Chrome sem mudar o SO: DevTools → `Ctrl+Shift+P` → "Show Rendering" → **Emulate CSS
prefers-color-scheme: dark**.

Prova objetiva, sem depender do olho (rodar no console da página):

```js
const i = document.querySelector('input[type="number"]')
getComputedStyle(i).color            // esperado depois do fix: rgb(0, 0, 0)
getComputedStyle(i).backgroundColor  // rgb(255, 255, 255)
```

Se `color` voltar `rgb(255, 255, 255)` com o fundo branco, não está corrigido.

Checagem dos nomes acessíveis (achado A) — deve retornar `0`:

```js
[...document.querySelectorAll('input, select')]
  .filter(el => !el.labels?.length && !el.getAttribute('aria-label')).length
```

Rotina padrão do repo antes de qualquer push (o build **não** valida tipos —
`typescript.ignoreBuildErrors: true`):

```bash
cd frontend && npx tsc --noEmit && npm run build
```

---

## 6. Fora de escopo

- Tema escuro real (ver §3).
- Auditoria de a11y das outras superfícies: `ResultsDisplay` (gráfico recharts sem alternativa
  textual), `/metodologia`, navegação por teclado ponta a ponta. Este handoff cobriu o formulário
  porque foi ali que o bug apareceu.
- `README.md` com stack desatualizada (menciona Vite/Shadcn/`src/`, que não existem) — pendência
  conhecida, registrada na revisão final do plano anterior.
- `NEXT_PUBLIC_API_URL` na Vercel, CORS `*.vercel.app`, upgrade do `next@14.0.3`, limpeza dos
  arquivos do curso na raiz — todos já listados como fora de escopo no handoff anterior.

---

## 7. Ordem sugerida

1. **§3, o fix do `globals.css`** — uma edição, resolve o P0 que está no ar agora.
2. Validar em modo escuro emulado (§5) nas duas calculadoras.
3. Achado A (rótulos) + C (aria de erro) juntos, no mesmo passe — é o mesmo bloco de JSX.
4. Achado B (`text-red-500` → `text-red-600`), busca e substitui.
