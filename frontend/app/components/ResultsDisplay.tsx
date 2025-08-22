'use client'

import { ArrowLeft, AlertTriangle, CheckCircle, Info, TrendingUp, User } from 'lucide-react'
import { AnaliseResponse } from '../types/medical'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface ResultsDisplayProps {
  result: AnaliseResponse
  onNewAnalysis: () => void
}

export default function ResultsDisplay({ result, onNewAnalysis }: ResultsDisplayProps) {
  const { predicao, explicacoes } = result

  // Determinar cor e ícone baseado no risco
  const getRiskStyle = (categoria: string) => {
    switch (categoria) {
      case 'Alto Risco':
        return {
          color: 'text-red-700',
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: AlertTriangle,
          iconColor: 'text-red-500'
        }
      case 'Medio Risco':
        return {
          color: 'text-yellow-700',
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: Info,
          iconColor: 'text-yellow-500'
        }
      default:
        return {
          color: 'text-green-700',
          bg: 'bg-green-50',
          border: 'border-green-200',
          icon: CheckCircle,
          iconColor: 'text-green-500'
        }
    }
  }

  const riskStyle = getRiskStyle(predicao.categoria_risco)
  const RiskIcon = riskStyle.icon

  // Dados para o gráfico de barras (fatores de risco)
  const chartData = explicacoes.fatores_risco.slice(0, 5).map(fator => ({
    nome: fator.fator,
    impacto: Math.abs(fator.impacto),
    valor: typeof fator.valor === 'number' ? fator.valor : 1
  }))

  // Dados para o gráfico de pizza (distribuição de risco)
  const pieData = [
    { name: 'Baixo Risco', value: predicao.categoria_risco === 'Baixo Risco' ? predicao.probabilidade * 100 : 25, color: '#22c55e' },
    { name: 'Médio Risco', value: predicao.categoria_risco === 'Medio Risco' ? predicao.probabilidade * 100 : 35, color: '#eab308' },
    { name: 'Alto Risco', value: predicao.categoria_risco === 'Alto Risco' ? predicao.probabilidade * 100 : 40, color: '#ef4444' }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-gray-800">Resultado da Análise</h2>
        <button
          onClick={onNewAnalysis}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Nova Análise
        </button>
      </div>

      {/* Risk Summary Card */}
      <div className={`p-6 rounded-lg border-2 ${riskStyle.bg} ${riskStyle.border}`}>
        <div className="flex items-start gap-4">
          <RiskIcon className={`w-12 h-12 ${riskStyle.iconColor}`} />
          <div className="flex-1">
            <h3 className={`text-2xl font-bold ${riskStyle.color}`}>
              {predicao.categoria_risco}
            </h3>
            <p className={`text-lg ${riskStyle.color} opacity-80`}>
              Probabilidade: {(predicao.probabilidade * 100).toFixed(1)}%
            </p>
            <p className={`text-sm ${riskStyle.color} opacity-70 mt-2`}>
              Confiança do modelo: {(predicao.confianca * 100).toFixed(1)}%
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Score de Risco</p>
            <p className="text-3xl font-bold text-gray-800">{predicao.score_risco.toFixed(3)}</p>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg card-shadow">
          <div className="flex items-center gap-3 mb-2">
            <User className="w-6 h-6 text-blue-500" />
            <h4 className="text-sm font-medium text-gray-600">BMI</h4>
          </div>
          <p className="text-2xl font-bold text-gray-800">{predicao.bmi}</p>
          <p className="text-sm text-gray-500">{predicao.classificacao_bmi}</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg card-shadow">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-6 h-6 text-red-500" />
            <h4 className="text-sm font-medium text-gray-600">Pressão</h4>
          </div>
          <p className="text-2xl font-bold text-gray-800">{predicao.classificacao_pressao}</p>
          <p className="text-sm text-gray-500">Classificação atual</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg card-shadow">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-6 h-6 text-yellow-500" />
            <h4 className="text-sm font-medium text-gray-600">Fatores de Risco</h4>
          </div>
          <p className="text-2xl font-bold text-gray-800">{explicacoes.fatores_risco.length}</p>
          <p className="text-sm text-gray-500">Identificados</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg card-shadow">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <h4 className="text-sm font-medium text-gray-600">Fatores Protetivos</h4>
          </div>
          <p className="text-2xl font-bold text-gray-800">{explicacoes.fatores_protecao.length}</p>
          <p className="text-sm text-gray-500">Identificados</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Bar Chart - Risk Factors */}
        <div className="bg-white p-6 rounded-lg card-shadow">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">Principais Fatores de Risco</h4>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="nome" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [value.toFixed(3), 'Impacto']}
                  labelFormatter={(label) => `Fator: ${label}`}
                />
                <Bar dataKey="impacto" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-gray-500">
              Nenhum fator de risco significativo identificado
            </div>
          )}
        </div>

        {/* Pie Chart - Risk Distribution */}
        <div className="bg-white p-6 rounded-lg card-shadow">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">Distribuição de Probabilidade</h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Probabilidade']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Explanations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Risk Factors */}
        {explicacoes.fatores_risco.length > 0 && (
          <div className="bg-white p-6 rounded-lg card-shadow">
            <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              Fatores que Aumentam o Risco
            </h4>
            <div className="space-y-4">
              {explicacoes.fatores_risco.map((fator, index) => (
                <div key={index} className="border-l-4 border-red-500 pl-4">
                  <div className="flex justify-between items-start mb-1">
                    <h5 className="font-medium text-gray-800">{fator.fator}</h5>
                    <span className="text-sm font-bold text-red-600">
                      +{fator.impacto.toFixed(3)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">Valor: {fator.valor}</p>
                  <p className="text-sm text-gray-700">{fator.interpretacao}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Protective Factors */}
        {explicacoes.fatores_protecao.length > 0 && (
          <div className="bg-white p-6 rounded-lg card-shadow">
            <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              Fatores Protetivos
            </h4>
            <div className="space-y-4">
              {explicacoes.fatores_protecao.map((fator, index) => (
                <div key={index} className="border-l-4 border-green-500 pl-4">
                  <div className="flex justify-between items-start mb-1">
                    <h5 className="font-medium text-gray-800">{fator.fator}</h5>
                    <span className="text-sm font-bold text-green-600">
                      {fator.impacto.toFixed(3)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">Valor: {fator.valor}</p>
                  <p className="text-sm text-gray-700">{fator.interpretacao}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* General Interpretation */}
      <div className="bg-white p-6 rounded-lg card-shadow">
        <h4 className="text-lg font-semibold text-gray-800 mb-4">Interpretação Geral</h4>
        <p className="text-gray-700 leading-relaxed">{explicacoes.interpretacao_geral}</p>
      </div>

      {/* Recommendations */}
      <div className="bg-white p-6 rounded-lg card-shadow">
        <h4 className="text-lg font-semibold text-gray-800 mb-4">Recomendações Médicas</h4>
        <ul className="space-y-2">
          {explicacoes.recomendacoes.map((recomendacao, index) => (
            <li key={index} className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-gray-700">{recomendacao}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <h5 className="font-medium text-yellow-800">Importante</h5>
            <p className="text-sm text-yellow-700 mt-1">
              Esta análise é uma ferramenta de apoio à decisão médica baseada em inteligência artificial. 
              Os resultados devem ser interpretados por um profissional de saúde qualificado e não 
              substituem o julgamento clínico ou exames complementares.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}