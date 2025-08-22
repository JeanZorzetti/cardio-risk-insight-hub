'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'react-hot-toast'
import { Loader2, User, Activity, FlaskConical, Stethoscope } from 'lucide-react'
import { PacienteInput, AnaliseResponse } from '../types/medical'
import { analisarPaciente } from '../utils/api'

interface PatientFormProps {
  onAnalysisComplete: (result: AnaliseResponse) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function PatientForm({ onAnalysisComplete, isLoading, setIsLoading }: PatientFormProps) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<PacienteInput>({
    defaultValues: {
      idade: 45,
      genero: 'Masculino',
      tipo_sanguineo: 'O+',
      pressao_sistolica: 120,
      pressao_diastolica: 80,
      freq_cardiaca: 70,
      peso: 75,
      altura: 1.70,
      colesterol: 200,
      glicose: 100,
      num_medicamentos: 0,
      visitas_anuais: 1,
      dor_peito: false,
      falta_ar: false,
      fadiga: false,
      tontura: false
    }
  })

  const watchedData = watch()
  const bmi = watchedData.peso / (watchedData.altura ** 2)

  const onSubmit = async (data: PacienteInput) => {
    setIsLoading(true)
    try {
      const result = await analisarPaciente(data)
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
              Gênero
            </label>
            <select
              {...register('genero', { required: 'Gênero é obrigatório' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Masculino">Masculino</option>
              <option value="Feminino">Feminino</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo Sanguíneo
            </label>
            <select
              {...register('tipo_sanguineo', { required: 'Tipo sanguíneo é obrigatório' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="A+">A+</option>
              <option value="A-">A-</option>
              <option value="B+">B+</option>
              <option value="B-">B-</option>
              <option value="AB+">AB+</option>
              <option value="AB-">AB-</option>
              <option value="O+">O+</option>
              <option value="O-">O-</option>
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
              {...register('pressao_sistolica', { 
                required: 'Pressão sistólica é obrigatória',
                min: { value: 60, message: 'Valor mínimo é 60 mmHg' },
                max: { value: 300, message: 'Valor máximo é 300 mmHg' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.pressao_sistolica && <p className="text-red-500 text-xs mt-1">{errors.pressao_sistolica.message}</p>}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pressão Diastólica (mmHg)
            </label>
            <input
              type="number"
              {...register('pressao_diastolica', { 
                required: 'Pressão diastólica é obrigatória',
                min: { value: 30, message: 'Valor mínimo é 30 mmHg' },
                max: { value: 200, message: 'Valor máximo é 200 mmHg' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.pressao_diastolica && <p className="text-red-500 text-xs mt-1">{errors.pressao_diastolica.message}</p>}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Frequência Cardíaca (bpm)
            </label>
            <input
              type="number"
              {...register('freq_cardiaca', { 
                required: 'Frequência cardíaca é obrigatória',
                min: { value: 30, message: 'Valor mínimo é 30 bpm' },
                max: { value: 200, message: 'Valor máximo é 200 bpm' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.freq_cardiaca && <p className="text-red-500 text-xs mt-1">{errors.freq_cardiaca.message}</p>}
          </div>
        </div>
      </div>

      {/* Dados Antropométricos */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700">Dados Antropométricos</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              BMI Calculado
            </label>
            <div className="px-3 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-700">
              {bmi.toFixed(2)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {bmi < 18.5 ? 'Abaixo do peso' :
               bmi < 25 ? 'Peso normal' :
               bmi < 30 ? 'Sobrepeso' : 'Obesidade'}
            </p>
          </div>
        </div>
      </div>

      {/* Dados Laboratoriais */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
          <FlaskConical className="w-5 h-5" />
          Exames Laboratoriais
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Colesterol Total (mg/dL)
            </label>
            <input
              type="number"
              {...register('colesterol', { 
                required: 'Colesterol é obrigatório',
                min: { value: 50, message: 'Valor mínimo é 50 mg/dL' },
                max: { value: 500, message: 'Valor máximo é 500 mg/dL' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.colesterol && <p className="text-red-500 text-xs mt-1">{errors.colesterol.message}</p>}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Glicose (mg/dL)
            </label>
            <input
              type="number"
              {...register('glicose', { 
                required: 'Glicose é obrigatória',
                min: { value: 50, message: 'Valor mínimo é 50 mg/dL' },
                max: { value: 400, message: 'Valor máximo é 400 mg/dL' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.glicose && <p className="text-red-500 text-xs mt-1">{errors.glicose.message}</p>}
          </div>
        </div>
      </div>

      {/* Histórico Médico */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
          <Stethoscope className="w-5 h-5" />
          Histórico Médico
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Número de Medicamentos
            </label>
            <input
              type="number"
              {...register('num_medicamentos', { 
                required: 'Número de medicamentos é obrigatório',
                min: { value: 0, message: 'Valor mínimo é 0' },
                max: { value: 20, message: 'Valor máximo é 20' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Visitas Médicas por Ano
            </label>
            <input
              type="number"
              {...register('visitas_anuais', { 
                required: 'Visitas anuais é obrigatório',
                min: { value: 0, message: 'Valor mínimo é 0' },
                max: { value: 50, message: 'Valor máximo é 50' }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
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
              Analisar Risco Cardiovascular
            </>
          )}
        </button>
      </div>
    </form>
  )
}