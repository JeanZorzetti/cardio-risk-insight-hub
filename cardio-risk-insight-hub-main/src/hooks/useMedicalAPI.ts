import { useState } from 'react';
import { toast } from '@/hooks/use-toast';

interface PatientData {
  idade: number;
  genero: string;
  tipo_sanguineo: string;
  pressao_sistolica: number;
  pressao_diastolica: number;
  freq_cardiaca: number;
  peso: number;
  altura: number;
  colesterol: number;
  glicose: number;
  num_medicamentos: number;
  visitas_anuais: number;
  dor_peito: boolean;
  falta_ar: boolean;
  fadiga: boolean;
  tontura: boolean;
}

interface Predicao {
  categoria_risco: string;
  probabilidade: number;
  score_risco: number;
  confianca: number;
  bmi: number;
  classificacao_bmi: string;
  classificacao_pressao: string;
}

interface FatorExplicacao {
  fator: string;
  valor: number | string;
  impacto: number;
  interpretacao: string;
}

interface Explicacoes {
  fatores_risco: FatorExplicacao[];
  fatores_protecao: FatorExplicacao[];
  interpretacao_geral: string;
  recomendacoes: string[];
}

interface APIResponse {
  predicao: Predicao;
  explicacoes: Explicacoes;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://cardioapi.roilabs.com.br';

export function useMedicalAPI() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<APIResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzePatient = async (patientData: PatientData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/analise-completa`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData),
      });

      if (!response.ok) {
        throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
      }

      const data: APIResponse = await response.json();
      setResult(data);
      
      toast({
        title: "Análise Concluída",
        description: `Risco identificado: ${data.predicao.categoria_risco}`,
      });

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      
      // Simular dados de exemplo se a API não estiver disponível
      if (errorMessage.includes('fetch')) {
        const mockResult = generateMockResult(patientData);
        setResult(mockResult);
        
        toast({
          title: "Modo Demonstração",
          description: "API não disponível. Exibindo dados simulados.",
          variant: "destructive",
        });
        
        return mockResult;
      }
      
      toast({
        title: "Erro na Análise",
        description: errorMessage,
        variant: "destructive",
      });
      
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getExamplePatient = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/exemplo-paciente`);
      
      if (!response.ok) {
        throw new Error('Erro ao buscar exemplo');
      }
      
      return await response.json();
    } catch (err) {
      // Retornar exemplo fixo se API não disponível
      return {
        idade: 55,
        genero: "Masculino",
        tipo_sanguineo: "O+",
        pressao_sistolica: 140,
        pressao_diastolica: 90,
        freq_cardiaca: 75,
        peso: 80,
        altura: 1.75,
        colesterol: 220,
        glicose: 110,
        num_medicamentos: 2,
        visitas_anuais: 3,
        dor_peito: true,
        falta_ar: false,
        fadiga: true,
        tontura: false,
      };
    }
  };

  return {
    loading,
    result,
    error,
    analyzePatient,
    getExamplePatient,
    clearResult: () => setResult(null),
    clearError: () => setError(null),
  };
}

// Função para gerar dados simulados (quando API não disponível)
function generateMockResult(patientData: PatientData): APIResponse {
  const bmi = patientData.peso / (patientData.altura * patientData.altura);
  
  // Lógica simples para determinar risco baseado nos dados
  let riskScore = 0;
  
  // Fatores de idade
  if (patientData.idade > 60) riskScore += 0.3;
  else if (patientData.idade > 45) riskScore += 0.15;
  
  // Pressão arterial
  if (patientData.pressao_sistolica > 140) riskScore += 0.25;
  else if (patientData.pressao_sistolica > 120) riskScore += 0.1;
  
  // BMI
  if (bmi > 30) riskScore += 0.2;
  else if (bmi > 25) riskScore += 0.1;
  
  // Sintomas
  if (patientData.dor_peito) riskScore += 0.15;
  if (patientData.fadiga) riskScore += 0.1;
  if (patientData.falta_ar) riskScore += 0.12;
  
  // Determinar categoria
  let categoria_risco: string;
  if (riskScore > 0.6) categoria_risco = "Alto Risco";
  else if (riskScore > 0.3) categoria_risco = "Médio Risco";
  else categoria_risco = "Baixo Risco";

  return {
    predicao: {
      categoria_risco,
      probabilidade: Math.min(riskScore + 0.1, 0.95),
      score_risco: riskScore,
      confianca: 0.85,
      bmi: Number(bmi.toFixed(1)),
      classificacao_bmi: bmi > 30 ? "Obesidade" : bmi > 25 ? "Sobrepeso" : "Normal",
      classificacao_pressao: patientData.pressao_sistolica > 140 ? "Hipertensão Estágio 1" : "Normal"
    },
    explicacoes: {
      fatores_risco: [
        {
          fator: "Pressão Sistólica",
          valor: patientData.pressao_sistolica,
          impacto: patientData.pressao_sistolica > 140 ? 0.04 : 0.01,
          interpretacao: `Pressão sistólica de ${patientData.pressao_sistolica} mmHg ${patientData.pressao_sistolica > 140 ? 'está elevada' : 'está normal'}`
        },
        {
          fator: "Idade",
          valor: patientData.idade,
          impacto: patientData.idade > 60 ? 0.03 : 0.015,
          interpretacao: `Idade de ${patientData.idade} anos ${patientData.idade > 60 ? 'representa fator de risco significativo' : 'é moderada'}`
        },
        {
          fator: "IMC",
          valor: bmi.toFixed(1),
          impacto: bmi > 30 ? 0.025 : bmi > 25 ? 0.015 : 0.005,
          interpretacao: `IMC de ${bmi.toFixed(1)} kg/m² indica ${bmi > 30 ? 'obesidade' : bmi > 25 ? 'sobrepeso' : 'peso normal'}`
        }
      ].filter(f => f.impacto > 0.01),
      fatores_protecao: [
        {
          fator: "Frequência Cardíaca",
          valor: patientData.freq_cardiaca,
          impacto: patientData.freq_cardiaca < 80 ? -0.01 : 0,
          interpretacao: `Frequência cardíaca de ${patientData.freq_cardiaca} bpm está adequada`
        }
      ].filter(f => f.impacto < 0),
      interpretacao_geral: `Análise baseada em ${Object.keys(patientData).length} parâmetros clínicos. O modelo identificou ${categoria_risco.toLowerCase()} com base principalmente na combinação de fatores como idade, pressão arterial e composição corporal. Recomenda-se acompanhamento médico adequado ao nível de risco identificado.`,
      recomendacoes: categoria_risco === "Alto Risco" ? [
        "🚨 Consulta cardiológica urgente em 7 dias",
        "📊 Exames complementares (ECG, ecocardiograma)",
        "💊 Revisão medicamentosa imediata",
        "🏃‍♂️ Programa de exercícios supervisionado",
        "🥗 Consulta nutricional para dieta cardioprotetora"
      ] : categoria_risco === "Médio Risco" ? [
        "👨‍⚕️ Consulta cardiológica em 30 dias",
        "📊 Exames laboratoriais de controle",
        "🏃‍♂️ Programa de exercícios moderados",
        "🥗 Orientação nutricional",
        "🔄 Monitoramento pressórico regular"
      ] : [
        "✅ Manter consultas preventivas anuais",
        "🏃‍♂️ Atividade física regular",
        "🥗 Dieta equilibrada",
        "🚭 Manter estilo de vida saudável"
      ]
    }
  };
}