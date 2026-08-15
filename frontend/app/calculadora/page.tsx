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
