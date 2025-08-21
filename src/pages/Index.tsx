import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Heart, Brain, FileText, RotateCcw, Stethoscope } from "lucide-react";
import PatientForm from "@/components/medical/PatientForm";
import RiskGauge from "@/components/medical/RiskGauge";
import ShapExplanations from "@/components/medical/ShapExplanations";
import MedicalRecommendations from "@/components/medical/MedicalRecommendations";
import { useMedicalAPI } from "@/hooks/useMedicalAPI";

const Index = () => {
  const { loading, result, analyzePatient, clearResult } = useMedicalAPI();
  const [showResults, setShowResults] = useState(false);

  const handlePatientSubmit = async (patientData: any) => {
    try {
      await analyzePatient(patientData);
      setShowResults(true);
    } catch (error) {
      console.error('Erro na análise:', error);
    }
  };

  const handleNewAnalysis = () => {
    setShowResults(false);
    clearResult();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-medical-primary/5 to-background">
      {/* Header */}
      <header className="bg-medical-primary text-medical-primary-foreground shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-white/10 p-3 rounded-full">
                <Heart className="h-8 w-8" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">CardioCare AI</h1>
                <p className="text-sm opacity-90">Sistema de Análise de Risco Cardíaco</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="bg-white/10 text-white border-white/30">
                <Brain className="h-3 w-3 mr-1" />
                IA Médica
              </Badge>
              
              {showResults && (
                <Button 
                  onClick={handleNewAnalysis}
                  variant="outline"
                  className="bg-white/10 border-white/30 text-white hover:bg-white/20"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Nova Análise
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {!showResults ? (
          /* Formulário de Entrada */
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-medical-primary mb-2">
                Análise de Risco Cardíaco com IA
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Sistema avançado de análise de risco cardiovascular usando Machine Learning 
                com explicabilidade SHAP completa. Insira os dados do paciente para uma 
                avaliação precisa e recomendações personalizadas.
              </p>
            </div>

            <PatientForm onSubmit={handlePatientSubmit} loading={loading} />

            {/* Informações sobre o Sistema */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6 text-center">
                  <Brain className="h-12 w-12 text-medical-primary mx-auto mb-4" />
                  <h3 className="font-semibold mb-2">IA Explicável</h3>
                  <p className="text-sm text-muted-foreground">
                    Análises com explicações SHAP detalhadas para transparência total
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6 text-center">
                  <Stethoscope className="h-12 w-12 text-medical-primary mx-auto mb-4" />
                  <h3 className="font-semibold mb-2">Precisão Médica</h3>
                  <p className="text-sm text-muted-foreground">
                    Baseado em diretrizes cardiológicas e dados clínicos validados
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6 text-center">
                  <FileText className="h-12 w-12 text-medical-primary mx-auto mb-4" />
                  <h3 className="font-semibold mb-2">Relatórios Completos</h3>
                  <p className="text-sm text-muted-foreground">
                    Recomendações acionáveis e relatórios exportáveis
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          /* Resultados da Análise */
          result && (
            <div className="max-w-7xl mx-auto">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-medical-primary mb-2">
                  Resultado da Análise
                </h2>
                <p className="text-muted-foreground">
                  Análise completa baseada em inteligência artificial com explicabilidade total
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Coluna Esquerda - Resultados Principais */}
                <div className="space-y-6">
                  <RiskGauge
                    categoria_risco={result.predicao.categoria_risco}
                    probabilidade={result.predicao.probabilidade}
                    score_risco={result.predicao.score_risco}
                    confianca={result.predicao.confianca}
                  />
                  
                  <MedicalRecommendations
                    recomendacoes={result.explicacoes.recomendacoes}
                    categoria_risco={result.predicao.categoria_risco}
                    bmi={result.predicao.bmi}
                    classificacao_bmi={result.predicao.classificacao_bmi}
                    classificacao_pressao={result.predicao.classificacao_pressao}
                  />
                </div>

                {/* Coluna Direita - Explicações */}
                <div>
                  <ShapExplanations
                    fatores_risco={result.explicacoes.fatores_risco}
                    fatores_protecao={result.explicacoes.fatores_protecao}
                    interpretacao_geral={result.explicacoes.interpretacao_geral}
                  />
                </div>
              </div>
            </div>
          )
        )}
      </main>

      {/* Footer */}
      <footer className="bg-medical-primary/10 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-2">
              CardioCare AI - Sistema de Análise de Risco Cardíaco
            </p>
            <p className="text-xs text-muted-foreground">
              Desenvolvido para apoio ao diagnóstico médico. Sempre consulte um profissional de saúde qualificado.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
