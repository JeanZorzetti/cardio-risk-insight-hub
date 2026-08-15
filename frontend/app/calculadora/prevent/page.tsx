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
