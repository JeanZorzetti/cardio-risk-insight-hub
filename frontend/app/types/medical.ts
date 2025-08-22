// Tipos TypeScript para o sistema médico

export interface PacienteInput {
  idade: number
  genero: 'Masculino' | 'Feminino'
  tipo_sanguineo: 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | 'O+' | 'O-'
  pressao_sistolica: number
  pressao_diastolica: number
  freq_cardiaca: number
  peso: number
  altura: number
  colesterol: number
  glicose: number
  num_medicamentos: number
  visitas_anuais: number
  dor_peito: boolean
  falta_ar: boolean
  fadiga: boolean
  tontura: boolean
}

export interface PredicaoResponse {
  categoria_risco: 'Baixo Risco' | 'Medio Risco' | 'Alto Risco'
  probabilidade: number
  score_risco: number
  confianca: number
  timestamp: string
  bmi: number
  classificacao_bmi: string
  classificacao_pressao: string
}

export interface ExplicacaoSHAP {
  fator: string
  valor: number | string
  impacto: number
  interpretacao: string
  categoria: 'increase_risk' | 'decrease_risk' | 'neutral'
}

export interface ExplicacoesResponse {
  fatores_risco: ExplicacaoSHAP[]
  fatores_protecao: ExplicacaoSHAP[]
  interpretacao_geral: string
  recomendacoes: string[]
}

export interface AnaliseResponse {
  predicao: PredicaoResponse
  explicacoes: ExplicacoesResponse
  dados_processados: {
    entrada: PacienteInput
    calculos: {
      bmi: number
      score_final: number
      fatores_analisados: number
    }
  }
}

export interface APIError {
  detail: string
}