import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Heart, TrendingUp, Shield, AlertTriangle } from "lucide-react";

interface RiskGaugeProps {
  categoria_risco: string;
  probabilidade: number;
  score_risco: number;
  confianca: number;
}

export default function RiskGauge({ categoria_risco, probabilidade, score_risco, confianca }: RiskGaugeProps) {
  const getRiskConfig = () => {
    const riskLevel = categoria_risco.toLowerCase();
    
    if (riskLevel.includes('alto')) {
      return {
        color: 'risk-high',
        bgColor: 'bg-risk-high',
        textColor: 'text-risk-high',
        icon: AlertTriangle,
        description: 'Risco elevado requer atenção médica imediata'
      };
    } else if (riskLevel.includes('médio') || riskLevel.includes('medio')) {
      return {
        color: 'risk-medium',
        bgColor: 'bg-risk-medium',
        textColor: 'text-risk-medium',
        icon: TrendingUp,
        description: 'Risco moderado requer monitoramento regular'
      };
    } else {
      return {
        color: 'risk-low',
        bgColor: 'bg-risk-low',
        textColor: 'text-risk-low',
        icon: Shield,
        description: 'Risco baixo, continue cuidados preventivos'
      };
    }
  };

  const config = getRiskConfig();
  const IconComponent = config.icon;
  const probabilidadePercent = Math.round(probabilidade * 100);
  const scorePercent = Math.round(score_risco * 100);
  const confiancaPercent = Math.round(confianca * 100);

  return (
    <Card className="w-full">
      <CardHeader className={`${config.bgColor} text-white`}>
        <CardTitle className="flex items-center gap-2">
          <Heart className="h-5 w-5" />
          Resultado da Análise
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-6">
        <div className="space-y-6">
          {/* Categoria Principal */}
          <div className="text-center space-y-3">
            <div className="flex justify-center">
              <IconComponent className={`h-16 w-16 ${config.textColor}`} />
            </div>
            
            <div>
              <h2 className={`text-3xl font-bold ${config.textColor}`}>
                {categoria_risco.toUpperCase()}
              </h2>
              <p className="text-muted-foreground mt-1">
                {config.description}
              </p>
            </div>
            
            <Badge 
              variant="outline" 
              className={`text-lg px-4 py-1 border-2 ${config.textColor}`}
            >
              {probabilidadePercent}% de probabilidade
            </Badge>
          </div>

          {/* Gauge Visual */}
          <div className="space-y-4">
            <div className="relative">
              {/* Barra de Risco Principal */}
              <div className="w-full h-6 bg-gradient-to-r from-risk-low via-risk-medium to-risk-high rounded-full overflow-hidden">
                <div 
                  className="h-full bg-white/30 transition-all duration-1000 ease-out"
                  style={{ width: `${probabilidadePercent}%` }}
                />
              </div>
              
              {/* Marcador */}
              <div 
                className="absolute top-0 h-6 w-1 bg-white shadow-lg transition-all duration-1000 ease-out"
                style={{ left: `${probabilidadePercent}%`, transform: 'translateX(-50%)' }}
              />
              
              {/* Labels */}
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>0% Baixo</span>
                <span>30%</span>
                <span>70%</span>
                <span>100% Alto</span>
              </div>
            </div>
          </div>

          {/* Métricas Detalhadas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Score de Risco</span>
                <span className="font-semibold">{scorePercent}%</span>
              </div>
              <Progress value={scorePercent} className="h-2" />
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Confiança do Modelo</span>
                <span className="font-semibold">{confiancaPercent}%</span>
              </div>
              <Progress value={confiancaPercent} className="h-2" />
            </div>
          </div>

          {/* Timestamp */}
          <div className="text-center pt-2 border-t">
            <p className="text-xs text-muted-foreground">
              Análise realizada em {new Date().toLocaleString('pt-BR')}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}