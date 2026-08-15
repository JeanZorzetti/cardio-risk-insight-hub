'use client'

import { useForm } from 'react-hook-form'
import { toast } from 'react-hot-toast'
import { Loader2, User, Activity, Stethoscope } from 'lucide-react'
import { EntradaRapida, RespostaAvaliacao } from '../types/medical'
import { calcularRiscoRapido } from '../utils/api'

interface PatientFormProps {
  onAnalysisComplete: (result: RespostaAvaliacao) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function PatientForm({ onAnalysisComplete, isLoading, setIsLoading }: PatientFormProps) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<EntradaRapida>({
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
      tontura: false
    }
  })

  const watchedData = watch()
  const bmi = watchedData.peso / (watchedData.altura ** 2)

  const onSubmit = async (data: EntradaRapida) => {
    setIsLoading(true)
    try {
      const result = await calcularRiscoRapido(data)
      onAnalysisComplete(result)
      toast.success('Análise realizada com sucesso!')
    } catch (error: any) {
      console.error('Erro na análise:', error)
      toast.error(error.message || 'Erro ao realizar análise')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      {/* Dados Demográficos */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
          <User className="w-5 h-5" />
          Dados Demográficos
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Idade
            </label>
            <input
              type="number"
              {...register('idade', {
                required: 'Idade é obrigatória',
                min: { value: 18, message: 'Idade mínima é 18 anos' },
                max: { value: 120, message: 'Idade máxima é 120 anos' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.idade && <p className="text-red-500 text-xs mt-1">{errors.idade.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sexo
            </label>
            <select
              {...register('sexo', { required: 'Sexo é obrigatório' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="masculino">Masculino</option>
              <option value="feminino">Feminino</option>
            </select>
          </div>
        </div>
      </div>

      {/* Dados Vitais */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Dados Vitais
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pressão Sistólica (mmHg)
            </label>
            <input
              type="number"
              {...register('pas', {
                required: 'Pressão sistólica é obrigatória',
                min: { value: 60, message: 'Valor mínimo é 60 mmHg' },
                max: { value: 300, message: 'Valor máximo é 300 mmHg' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.pas && <p className="text-red-500 text-xs mt-1">{errors.pas.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Peso (kg)
            </label>
            <input
              type="number"
              step="0.1"
              {...register('peso', {
                required: 'Peso é obrigatório',
                min: { value: 20, message: 'Peso mínimo é 20 kg' },
                max: { value: 300, message: 'Peso máximo é 300 kg' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.peso && <p className="text-red-500 text-xs mt-1">{errors.peso.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Altura (m)
            </label>
            <input
              type="number"
              step="0.01"
              {...register('altura', {
                required: 'Altura é obrigatória',
                min: { value: 1.0, message: 'Altura mínima é 1.0 m' },
                max: { value: 2.5, message: 'Altura máxima é 2.5 m' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.altura && <p className="text-red-500 text-xs mt-1">{errors.altura.message}</p>}
          </div>
        </div>
        <div className="px-3 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-700 inline-block">
          BMI calculado: {isFinite(bmi) ? bmi.toFixed(2) : '—'}
        </div>
      </div>

      {/* Histórico e Fatores de Risco */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
          <Stethoscope className="w-5 h-5" />
          Histórico e Fatores de Risco
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              {...register('usa_anti_hipertensivo')}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="text-sm text-gray-700">Em tratamento para hipertensão</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              {...register('tabagismo')}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="text-sm text-gray-700">Fumante atual</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              {...register('diabetes')}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="text-sm text-gray-700">Diabetes</span>
          </label>
        </div>
      </div>

      {/* Sintomas */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700">Sintomas Atuais</h3>
        <div className="grid grid-cols-2 gap-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              {...register('dor_peito')}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="text-sm text-gray-700">Dor no Peito</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              {...register('falta_ar')}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="text-sm text-gray-700">Falta de Ar</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              {...register('fadiga')}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="text-sm text-gray-700">Fadiga</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              {...register('tontura')}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="text-sm text-gray-700">Tontura</span>
          </label>
        </div>
      </div>

      {/* Submit Button */}
      <div className="pt-6 border-t border-gray-200">
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Analisando...
            </>
          ) : (
            <>
              <Activity className="w-5 h-5" />
              Calcular Risco Cardiovascular
            </>
          )}
        </button>
      </div>
    </form>
  )
}
