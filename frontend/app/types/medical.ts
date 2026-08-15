// Tipos TypeScript para o contrato da API CardioRisk (ver backend/main.py)

export interface EntradaRapida {
  idade: number
  sexo: 'masculino' | 'feminino'
  peso: number
  altura: number
  pas: number
  usa_anti_hipertensivo: boolean
  tabagismo: boolean
  diabetes: boolean
  dor_peito: boolean
  falta_ar: boolean
  fadiga: boolean
  tontura: boolean
}

export interface EntradaPrevent extends EntradaRapida {
  colesterol_total: number
  hdl: number
  egfr: number
  usa_estatina: boolean
}

export interface Contribuicao {
  fator: string
  valor: number
  contribuicao: number
}

export interface RespostaRisco {
  tipo: 'resultado'
  categoria_risco: 'Baixo Risco' | 'Médio Risco' | 'Alto Risco'
  risco_10_anos: number
  risco_30_anos: number | null
  risco_truncado: boolean
  bmi: number
  classificacao_bmi: string
  contribuicoes: Contribuicao[]
  escore: string
  fonte: string
  timestamp: string
}

export interface RespostaBloqueio {
  tipo: 'bloqueio'
  motivo: 'sintomas' | 'faixa_etaria'
  mensagem: string
}

export type RespostaAvaliacao = RespostaRisco | RespostaBloqueio

export interface APIError {
  detail: string
}
