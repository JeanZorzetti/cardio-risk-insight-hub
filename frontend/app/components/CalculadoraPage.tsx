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
