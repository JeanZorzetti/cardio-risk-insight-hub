import axios, { AxiosError } from 'axios'
import { EntradaRapida, RespostaAvaliacao, APIError } from '../types/medical'

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

// Modo rápido (Framingham office-based, sem exames)
export const calcularRiscoRapido = async (dados: EntradaRapida): Promise<RespostaAvaliacao> => {
  const response = await api.post<RespostaAvaliacao>('/risco/rapido', dados)
  return response.data
}

export { API_BASE_URL }
