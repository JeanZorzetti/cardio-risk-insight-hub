import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  FileText, 
  Calendar, 
  Activity, 
  Utensils, 
  Stethoscope, 
  TestTube, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Download
} from "lucide-react";

interface MedicalRecommendationsProps {
  recomendacoes: string[];
  categoria_risco: string;
  bmi: number;
  classificacao_bmi: string;
  classificacao_pressao: string;
}

export default function MedicalRecommendations({ 
  recomendacoes, 
  categoria_risco, 
  bmi, 
  classificacao_bmi, 
  classificacao_pressao 
}: MedicalRecommendationsProps) {
  const getRiskConfig = () => {
    const riskLevel = categoria_risco.toLowerCase();
    
    if (riskLevel.includes('alto')) {
      return {
        color: 'risk-high',
        bgColor: 'bg-risk-high',
        textColor: 'text-risk-high',
        borderColor: 'border-risk-high',
        urgency: 'URGENTE',
        icon: AlertTriangle,
        description: 'Ação médica imediata necessária'
      };
    } else if (riskLevel.includes('médio') || riskLevel.includes('medio')) {
      return {
        color: 'risk-medium',
        bgColor: 'bg-risk-medium',
        textColor: 'text-risk-medium',
        borderColor: 'border-risk-medium',
        urgency: 'MONITORAMENTO',
        icon: Clock,
        description: 'Acompanhamento médico regular'
      };
    } else {
      return {
        color: 'risk-low',
        bgColor: 'bg-risk-low',
        textColor: 'text-risk-low',
        borderColor: 'border-risk-low',
        urgency: 'PREVENÇÃO',
        icon: CheckCircle,
        description: 'Manter cuidados preventivos'
      };
    }
  };

  const config = getRiskConfig();
  const IconComponent = config.icon;

  const getRecommendationIcon = (recomendacao: string) => {
    const texto = recomendacao.toLowerCase();
    
    if (texto.includes('consulta') || texto.includes('cardiolog')) return Stethoscope;
    if (texto.includes('exame') || texto.includes('laborat')) return TestTube;
    if (texto.includes('exerc') || texto.includes('atividade')) return Activity;
    if (texto.includes('dieta') || texto.includes('aliment')) return Utensils;
    if (texto.includes('agend') || texto.includes('retorno')) return Calendar;
    
    return FileText;
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExport = () => {
    // Simular export para PDF - seria integrado com biblioteca de PDF
    const data = {
      categoria_risco,
      bmi,
      classificacao_bmi,
      classificacao_pressao,
      recomendacoes,
      timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `relatorio-risco-cardiaco-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Métricas Complementares */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TestTube className="h-5 w-5" />
            Métricas Complementares
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">IMC</span>
                <Badge variant="outline">{bmi.toFixed(1)} kg/m²</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Classificação BMI</span>
                <Badge 
                  variant="outline"
                  className={`${
                    classificacao_bmi.toLowerCase().includes('normal') ? 'border-risk-low text-risk-low' :
                    classificacao_bmi.toLowerCase().includes('sobrepeso') ? 'border-risk-medium text-risk-medium' :
                    'border-risk-high text-risk-high'
                  }`}
                >
                  {classificacao_bmi}
                </Badge>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">Pressão Arterial</span>
                <Badge 
                  variant="outline"
                  className={`${
                    classificacao_pressao.toLowerCase().includes('normal') ? 'border-risk-low text-risk-low' :
                    classificacao_pressao.toLowerCase().includes('estágio 1') ? 'border-risk-medium text-risk-medium' :
                    'border-risk-high text-risk-high'
                  }`}
                >
                  {classificacao_pressao}
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recomendações Médicas */}
      <Card className={`border-2 ${config.borderColor}`}>
        <CardHeader className={`${config.bgColor} text-white`}>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center gap-2">
                <IconComponent className="h-5 w-5" />
                Recomendações Médicas
              </CardTitle>
              <div className="flex items-center gap-2 mt-2">
                <Badge 
                  variant="outline" 
                  className="bg-white/20 text-white border-white/30"
                >
                  {config.urgency}
                </Badge>
                <span className="text-sm opacity-90">
                  {config.description}
                </span>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={handlePrint}
                variant="outline"
                size="sm"
                className="bg-white/10 border-white/30 text-white hover:bg-white/20"
              >
                <FileText className="h-4 w-4 mr-1" />
                Imprimir
              </Button>
              <Button 
                onClick={handleExport}
                variant="outline"
                size="sm"
                className="bg-white/10 border-white/30 text-white hover:bg-white/20"
              >
                <Download className="h-4 w-4 mr-1" />
                Exportar
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-6">
          {recomendacoes.length > 0 ? (
            <div className="space-y-4">
              {recomendacoes.map((recomendacao, index) => {
                const RecommendationIcon = getRecommendationIcon(recomendacao);
                
                return (
                  <div 
                    key={index} 
                    className={`border-l-4 ${config.borderColor} bg-muted/30 p-4 rounded-r-lg`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`${config.bgColor} p-2 rounded-full`}>
                        <RecommendationIcon className="h-4 w-4 text-white" />
                      </div>
                      
                      <div className="flex-1">
                        <p className="text-sm font-medium leading-relaxed">
                          {recomendacao}
                        </p>
                      </div>
                      
                      <Badge 
                        variant="outline" 
                        className={`${config.textColor} ${config.borderColor} text-xs`}
                      >
                        #{index + 1}
                      </Badge>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <CheckCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>Nenhuma recomendação específica necessária no momento</p>
              <p className="text-xs mt-1">Continue com cuidados preventivos regulares</p>
            </div>
          )}
          
          {/* Footer com disclaimer */}
          <div className="mt-6 pt-4 border-t">
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5" />
                <div className="text-xs text-amber-800">
                  <p className="font-semibold mb-1">Aviso Médico Importante:</p>
                  <p>
                    Esta análise é baseada em inteligência artificial e deve ser usada apenas como 
                    ferramenta de apoio ao diagnóstico médico. Sempre consulte um profissional de 
                    saúde qualificado para avaliação clínica completa.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center mt-4 text-xs text-muted-foreground">
            Relatório gerado em {new Date().toLocaleString('pt-BR')}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}