import type { Metadata } from 'next'
import Link from 'next/link'
import Logo from '../components/Logo'

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
            <Logo className="w-14 h-14 shrink-0" />
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
