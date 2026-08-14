# CardioRisk — Design de Produtificação

**Data:** 2026-08-14
**Status:** aprovado, pendente de plano de implementação

## Contexto

O projeto nasceu como trabalho de um curso de IA aplicada e já está publicado
(`cardiorisk.roilabs.com.br` no Vercel, backend FastAPI em EasyPanel). A casca é
de produto; o miolo não é.

Diagnóstico do estado atual:

- Não existe modelo de machine learning. `ModeloIAMedica.calcular_risco_avancado`
  (`backend/main.py`) é uma cadeia de `if/else` com pesos escolhidos à mão.
  `scikit-learn` consta em `requirements.txt` mas não é importado.
- `gerar_explicacoes_shap` é documentada no próprio código como
  `"""Gera explicacoes SHAP simuladas"""`. O README e a `description` da API
  anunciam "IA Explicável com SHAP".
- Os datasets são sintéticos. `tipo_sanguineo` aparece como fator de risco
  cardiovascular, o que entrega a origem gerada dos dados.

O objetivo deste documento é transformar isso em produto com receita, tendo
**SEO/GEO/AEO como único canal de aquisição**.

## Restrição determinante: canal único

Com busca orgânica e citação por LLM como única aquisição, o produto precisa de
superfície pública indexável. Um app B2B atrás de login não gera tráfego nenhum.

O conflito central: o termo com volume de busca não é o termo que o comprador
digita.

| Intenção | Volume | Compra? |
|---|---|---|
| "calculadora risco cardiovascular", "escore PREVENT" | alto | não — médico, estudante, paciente |
| "estratificação risco cardiovascular ocupacional" | quase nulo | sim |

Com um canal só, não dá para escolher. A resposta é um funil em camadas.

## Arquitetura de funil

**Camada 1 — calculadoras públicas gratuitas (o ímã).**
Sem login, resultado instantâneo, URLs limpas. Ranqueiam nos termos de alto
volume e são o ativo de GEO/AEO.

**Camada 2 — página de metodologia (a peça de AEO).**
Qual escore, quais coeficientes, qual publicação, quais limitações, para quem
não se aplica. É o que faz o produto virar a fonte citada por LLM em vez do
MDCalc.

**Camada 3 — produto pago B2B (a receita).**
Upload de planilha de população → estratificação em lote → priorização
exportável. Alvo: medicina ocupacional, check-up corporativo, autogestão de
plano. O valor é operacional (quem chamar primeiro), não algorítmico.

**Ordem de construção, inegociável:** a camada 3 não começa antes da camada 1
provar tráfego. Se ninguém chega, o produto pago é código morto. Horizonte de
avaliação: 2-3 meses de indexação.

## Escolha dos escores

A atualização da diretriz da SBC de 2025 substituiu o Escore de Risco Global
(Framingham) pelo **PREVENT** (AHA, 2023) para a faixa de 30-79 anos.
Implementar Framingham como escore principal seria lançar já superado — ruim
para credibilidade e para AEO, já que um LLM consultado hoje busca o escore
vigente.

PREVENT também serve melhor o caso de uso B2B:

- Estima risco em **10 e 30 anos**. População trabalhadora é jovem (25-50), e um
  escore de 10 anos devolve 1-2% para quase todos nessa faixa — uma planilha de
  500 funcionários voltaria com "baixo risco" em quase todas as linhas e não
  priorizaria nada. O horizonte de 30 anos discrimina de verdade.
- Usa IMC, que o formulário atual já coleta.
- Não usa raça como variável, ao contrário das equações anteriores.
- Espaço de busca em português praticamente vazio, enquanto o Framingham tem
  15 anos de backlinks acumulados pelos concorrentes.

Custo: mais conjuntos de coeficientes (por sexo × desfecho × horizonte) e um
input adicional, o eGFR.

### Dois modos, dois escores

O eGFR é barreira de conversão na página pública: um leigo não sabe o dele.
A decisão foi oferecer dois modos. Isso exige dois escores — um "modo rápido"
que imputasse colesterol e HDL seria reincidir no erro de inventar números.

| Modo | Rota | Escore | Entradas |
|---|---|---|---|
| Rápido | `/calculadora` | Framingham *office-based* (D'Agostino 2008, variante sem exames) | idade, sexo, IMC, PAS, uso de anti-hipertensivo, tabagismo, diabetes |
| Completo | `/calculadora/prevent` | PREVENT (AHA 2023 / SBC 2025) | acima + colesterol total, HDL, eGFR, uso de estatina |

Ambos são validados e publicados. Cada página declara qual escore usa, a fonte e
a limitação. São duas intenções de busca distintas — "sem exames" e "completa" —
o que amplia a cobertura do canal único.

## Explicabilidade: remover SHAP

Os dois escores são log-lineares (Cox). A contribuição de cada fator é
exatamente `β·(x − x_referência)` contra um perfil de referência de mesma idade
e sexo, e a decomposição é aditiva por construção.

SHAP existe para *aproximar* essa decomposição em modelos não-lineares. Aqui o
valor exato sai da própria fórmula. Menos código que hoje, e passa a ser
verdade. Toda menção a SHAP sai do código, do README e da `description` da API.

## Mudanças no formulário

Saem do cálculo:

| Campo | Motivo |
|---|---|
| `tipo_sanguineo` | não é fator de risco cardiovascular |
| `num_medicamentos`, `visitas_anuais` | não constam em escore validado |

Entram: `hdl`, `tabagismo`, `diabetes`, `usa_anti_hipertensivo`, `usa_estatina`,
`egfr` (modo completo). `peso` e `altura` permanecem — alimentam o IMC, que é
entrada de ambos os escores.

### Guard de segurança (não simplificável)

Os sintomas (`dor_peito`, `falta_ar`, `fadiga`, `tontura`) saem do cálculo, mas
não da interface. Escore de prevenção primária vale para pessoa assintomática.
Se o usuário marca dor no peito ou falta de ar, a aplicação **não** retorna um
percentual: retorna orientação de buscar avaliação médica. Isto é validação em
fronteira de confiança e é requisito, não enfeite.

Igualmente obrigatório: bloqueio fora da faixa etária de validade de cada escore
(PREVENT: 30-79 anos) e disclaimer de que a ferramenta não é diagnóstico.

## Posicionamento regulatório

Software que estratifica risco de doença para decisão clínica é dispositivo
médico (RDC 657/2022, ANVISA). O produto se posiciona como **triagem e
priorização administrativa** — apoio à ordenação de agenda e de programas de
saúde populacional — não como diagnóstico, com disclaimer explícito em toda
superfície que devolve resultado.

Isso mitiga, não elimina. Antes de faturar, confirmar o enquadramento com
assessoria regulatória. Registrado aqui como risco aberto e conhecido.

## Componentes e arquivos

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `backend/scores/framingham_office.py` | novo | função pura: entradas → risco 10 anos + contribuições |
| `backend/scores/prevent.py` | novo | função pura: entradas → risco 10 e 30 anos + contribuições |
| `backend/test_scores.py` | novo | casos de referência publicados, ambos os escores |
| `backend/main.py` | editar | remove `calcular_risco_avancado` e `gerar_explicacoes_shap`; endpoints chamam os módulos de escore |
| `frontend/app/components/PatientForm.tsx` | editar | campos novos, campos removidos, guard de sintomas |
| `frontend/app/types/medical.ts` | editar | tipos acompanham o contrato da API |
| `frontend/app/calculadora/prevent/page.tsx` | novo | modo completo |
| `frontend/app/metodologia/page.tsx` | novo | camada 2, peça de AEO |
| `README.md`, `description` da API | editar | remover alegação de SHAP e de ML |

Os escores ficam em módulos puros, sem FastAPI, porque são a parte auditável e
citável do sistema: precisam ser testáveis e legíveis isoladamente.

## Testes

Requisito de aceitação: `backend/test_scores.py` valida cada escore contra os
casos de referência das publicações originais, com tolerância declarada. Os
coeficientes vêm do paper do D'Agostino (Circulation, 2008) e do material
suplementar do PREVENT (Circulation, 2024) — transcritos da fonte, nunca de
memória.

Um escore de saúde sem teste de referência não vai para produção.

## Limpeza do repositório

A raiz carrega entulho do trabalho de curso: `api_medica_corrigida.py`,
`api_medica_final.py`, `api_medica_windows.py`, `dashboard_medico.py`,
`Projeto_IA_Aplicada.py`, três CSVs sintéticos, o diretório duplicado
`cardio-risk-insight-hub-main/`, `README_ORIGINAL.md` e dois guias de deploy
redundantes.

Tag `curso-ia-aplicada` marcando o commit atual, depois remoção da `main`. O
histórico preserva tudo.

## Fora de escopo

Upload em lote, autenticação, billing e o painel B2B. Só depois que a camada 1
provar tráfego.

## Riscos abertos

1. **Enquadramento regulatório** — mitigado por posicionamento, não resolvido.
   Requer confirmação profissional antes da monetização.
2. **Tráfego pode não vir.** O plano inteiro depende de a camada 1 ranquear. Se
   em 3 meses não houver tráfego qualificado, o caminho B2B se invalida e a
   opção de recuo é usar o ativo como vitrine da ROI Labs.
3. **Nome.** `cardio-risk-insight-hub` é nome de repositório gerado pelo
   Lovable e "CardioCare AI" já é usado por outras empresas. Para um produto
   cujo canal é busca, isso merece decisão explícita.

## Fontes

- D'Agostino RB et al. *General Cardiovascular Risk Profile for Use in Primary
  Care: The Framingham Heart Study.* Circulation. 2008;117:743-53.
  <https://pubmed.ncbi.nlm.nih.gov/18212285/>
- Khan SS et al. *Development and Validation of the American Heart
  Association's PREVENT Equations.* Circulation. 2024.
  <https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.123.067626>
- Atualização da Diretriz de Prevenção Cardiovascular da SBC.
  <http://publicacoes.cardiol.br/portal/abc/portugues/aop/2019/aop-diretriz-prevencao-cardiovascular-portugues.pdf>
- ANVISA, RDC 657/2022 — dispositivos médicos de software.
