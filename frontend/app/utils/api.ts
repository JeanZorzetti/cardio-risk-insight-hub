import axios, { AxiosError } from 'axios'
import { PacienteInput, AnaliseResponse, APIError } from '../types/medical'

// Configuração base da API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://cardioapi.roilabs.com.br'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 segundos
})

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIError>) => {
    console.error('API Error:', error)
    
    if (error.code === 'ECONNABORTED') {
      throw new Error('Timeout: A requisição demorou muito para responder')
    }
    
    if (error.response) {
      // Erro da API (4xx, 5xx)
      const message = error.response.data?.detail || 
                     `Erro ${error.response.status}: ${error.response.statusText}`
      throw new Error(message)
    } else if (error.request) {
      // Erro de rede
      throw new Error('Erro de conexão: Verifique sua internet ou se a API está funcionando')
    } else {
      // Outro tipo de erro
      throw new Error('Erro inesperado: ' + error.message)
    }
  }
)

// Função para verificar se a API está funcionando
export const checkAPIHealth = async (): Promise<boolean> => {
  try {
    await api.get('/health')
    return true
  } catch (error) {
    console.error('Health check failed:', error)
    return false
  }
}

// Função para analisar um paciente
export const analisarPaciente = async (dados: PacienteInput): Promise<AnaliseResponse> => {
  try {
    const response = await api.post<AnaliseResponse>('/analise-completa', dados)
    return response.data
  } catch (error) {
    console.error('Erro ao analisar paciente:', error)
    throw error
  }
}

// Função para obter exemplos de pacientes
export const obterExemplosPacientes = async () => {
  try {
    const response = await api.get('/exemplo-paciente')
    return response.data
  } catch (error) {
    console.error('Erro ao obter exemplos:', error)
    throw error
  }
}

// Função auxiliar para validar URL da API
export const validateAPIUrl = (url: string): boolean => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// Função para testar conectividade
export const testConnection = async (): Promise<{ success: boolean; message: string; url: string }> => {
  try {
    const response = await api.get('/')
    return {
      success: true,
      message: 'Conexão estabelecida com sucesso',
      url: API_BASE_URL
    }
  } catch (error: any) {
    return {
      success: false,
      message: error.message || 'Erro ao conectar com a API',
      url: API_BASE_URL
    }
  }
}

export { API_BASE_URL }