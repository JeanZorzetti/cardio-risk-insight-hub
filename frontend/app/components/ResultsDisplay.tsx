'use client'

import { ArrowLeft, AlertTriangle, CheckCircle, Info, TrendingUp, ShieldAlert } from 'lucide-react'
import { RespostaAvaliacao } from '../types/medical'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface ResultsDisplayProps {
  result: RespostaAvaliacao
  onNewAnalysis: () => void
}

export default function ResultsDisplay({ result, onNewAnalysis }: ResultsDisplayProps) {
  const NovaAnaliseButton = () => (
    <button
      onClick={onNewAnalysis}
      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
    >
      <ArrowLeft className="w-4 h-4" />
      Nova Análise
    </button>
  )

  if (result.tipo === 'bloqueio') {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-bold text-gray-800">Não foi possível calcular</h2>
          <NovaAnaliseButton />
        </div>
        <div className="p-6 rounded-lg border-2 bg-yellow-50 border-yellow-200">
          <div className="flex items-start gap-4">
            <ShieldAlert className="w-12 h-12 text-yellow-600" />
            <div>
              <h3 className="text-xl font-bold text-yellow-800">
                {result.motivo === 'sintomas' ? 'Sintomas relatados' : 'Fora da faixa etária validada'}
              </h3>
              <p className="text-yellow-800 mt-2">{result.mensagem}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const { categoria_risco, risco_10_anos, risco_30_anos, risco_truncado, bmi, classificacao_bmi,
    contribuicoes, escore, fonte } = result

  const getRiskStyle = (categoria: string) => {
    switch (categoria) {
      case 'Alto Risco':
        return { color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200', icon: AlertTriangle, iconColor: 'text-red-500' }
      case 'Médio Risco':
        return { color: 'text-yellow-700', bg: 'bg-yellow-50', border: 'border-yellow-200', icon: Info, iconColor: 'text-yellow-500' }
      default:
        return { color: 'text-green-700', bg: 'bg-green-50', border: 'border-green-200', icon: CheckCircle, iconColor: 'text-green-500' }
    }
  }

  const riskStyle = getRiskStyle(categoria_risco)
  const RiskIcon = riskStyle.icon

  const chartData = contribuicoes.map(c => ({ nome: c.fator, contribuicao: c.contribuicao, valor: c.valor }))
  const fatoresAumentam = contribuicoes.filter(c => c.contribuicao > 0)
  const fatoresProtegem = contribuicoes.filter(c => c.contribuicao < 0)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-gray-800">Resultado da Análise</h2>
        <NovaAnaliseButton />
      </div>

      {/* Risk Summary Card */}
      <div className={`p-6 rounded-lg border-2 ${riskStyle.bg} ${riskStyle.border}`}>
        <div className="flex items-start gap-4">
          <RiskIcon className={`w-12 h-12 ${riskStyle.iconColor}`} />
          <div className="flex-1">
            <h3 className={`text-2xl font-bold ${riskStyle.color}`}>{categoria_risco}</h3>
            <p className={`text-lg ${riskStyle.color} opacity-80`}>
              Risco em 10 anos: {(risco_10_anos * 100).toFixed(1)}%{risco_truncado ? ' (fora da faixa de apresentação clínica)' : ''}
            </p>
            {risco_30_anos !== null && (
              <p className={`text-sm ${riskStyle.color} opacity-70 mt-1`}>
                Risco em 30 anos: {(risco_30_anos * 100).toFixed(1)}%
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg card-shadow">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-6 h-6 text-blue-500" />
            <h4 className="text-sm font-medium text-gray-600">BMI</h4>
          </div>
          <p className="text-2xl font-bold text-gray-800">{bmi}</p>
          <p className="text-sm text-gray-500">{classificacao_bmi}</p>
        </div>

        <div className="bg-white p-6 rounded-lg card-shadow">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-6 h-6 text-yellow-500" />
            <h4 className="text-sm font-medium text-gray-600">Fatores que Aumentam</h4>
          </div>
          <p className="text-2xl font-bold text-gray-800">{fatoresAumentam.length}</p>
          <p className="text-sm text-gray-500">Identificados</p>
        </div>

        <div className="bg-white p-6 rounded-lg card-shadow">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <h4 className="text-sm font-medium text-gray-600">Fatores Protetivos</h4>
          </div>
          <p className="text-2xl font-bold text-gray-800">{fatoresProtegem.length}</p>
          <p className="text-sm text-gray-500">Identificados</p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white p-6 rounded-lg card-shadow">
        <h4 className="text-lg font-semibold text-gray-800 mb-4">Contribuição por Fator</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="nome" angle={-45} textAnchor="end" height={80} fontSize={12} />
            <YAxis />
            <Tooltip formatter={(value: number) => [value.toFixed(3), 'Contribuição']} />
            <Bar dataKey="contribuicao">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.contribuicao >= 0 ? '#ef4444' : '#22c55e'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Explanations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {fatoresAumentam.length > 0 && (
          <div className="bg-white p-6 rounded-lg card-shadow">
            <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              Fatores que Aumentam o Risco
            </h4>
            <div className="space-y-4">
              {fatoresAumentam.map((c, index) => (
                <div key={index} className="border-l-4 border-red-500 pl-4">
                  <div className="flex justify-between items-start mb-1">
                    <h5 className="font-medium text-gray-800">{c.fator}</h5>
                    <span className="text-sm font-bold text-red-600">+{c.contribuicao.toFixed(3)}</span>
                  </div>
                  <p className="text-sm text-gray-600">Valor: {c.valor}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {fatoresProtegem.length > 0 && (
          <div className="bg-white p-6 rounded-lg card-shadow">
            <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              Fatores Protetivos
            </h4>
            <div className="space-y-4">
              {fatoresProtegem.map((c, index) => (
                <div key={index} className="border-l-4 border-green-500 pl-4">
                  <div className="flex justify-between items-start mb-1">
                    <h5 className="font-medium text-gray-800">{c.fator}</h5>
                    <span className="text-sm font-bold text-green-600">{c.contribuicao.toFixed(3)}</span>
                  </div>
                  <p className="text-sm text-gray-600">Valor: {c.valor}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Escore / Fonte */}
      <div className="bg-white p-6 rounded-lg card-shadow">
        <h4 className="text-lg font-semibold text-gray-800 mb-2">Escore Utilizado</h4>
        <p className="text-gray-700">{escore}</p>
        <p className="text-sm text-gray-500 mt-1">Fonte: {fonte}</p>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <h5 className="font-medium text-yellow-800">Importante</h5>
            <p className="text-sm text-yellow-700 mt-1">
              Esta análise é uma ferramenta de apoio à decisão médica baseada em escores clínicos
              validados. Os resultados devem ser interpretados por um profissional de saúde
              qualificado e não substituem o julgamento clínico ou exames complementares.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
