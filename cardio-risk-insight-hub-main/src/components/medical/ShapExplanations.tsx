import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Progress } from "@/components/ui/progress";
import { Brain, ChevronDown, ChevronUp, TrendingUp, TrendingDown, Info, Shield } from "lucide-react";

interface FatorExplicacao {
  fator: string;
  valor: number | string;
  impacto: number;
  interpretacao: string;
}

interface ShapExplanationsProps {
  fatores_risco: FatorExplicacao[];
  fatores_protecao: FatorExplicacao[];
  interpretacao_geral: string;
}

export default function ShapExplanations({ 
  fatores_risco, 
  fatores_protecao, 
  interpretacao_geral 
}: ShapExplanationsProps) {
  const [isRiskOpen, setIsRiskOpen] = useState(true);
  const [isProtectionOpen, setIsProtectionOpen] = useState(false);
  const [isInterpretationOpen, setIsInterpretationOpen] = useState(false);

  const formatImpact = (impacto: number) => {
    return impacto > 0 ? `+${impacto.toFixed(3)}` : `${impacto.toFixed(3)}`;
  };

  const getImpactColor = (impacto: number) => {
    const absImpact = Math.abs(impacto);
    if (absImpact >= 0.03) return impacto > 0 ? "bg-risk-high" : "bg-risk-low";
    if (absImpact >= 0.015) return impacto > 0 ? "bg-risk-medium" : "bg-risk-low";
    return "bg-muted";
  };

  const getImpactWidth = (impacto: number, maxImpact: number) => {
    return Math.abs(impacto) / maxImpact * 100;
  };

  // Encontrar o maior impacto para normalizar as barras
  const allImpacts = [...fatores_risco, ...fatores_protecao].map(f => Math.abs(f.impacto));
  const maxImpact = Math.max(...allImpacts, 0.001); // Evitar divisão por zero

  return (
    <Card className="w-full">
      <CardHeader className="bg-medical-primary text-medical-primary-foreground">
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5" />
          Explicações da IA (SHAP)
        </CardTitle>
        <p className="text-sm opacity-90">
          Entenda como cada fator influencia no risco cardíaco
        </p>
      </CardHeader>
      
      <CardContent className="p-6 space-y-6">
        {/* Fatores de Risco */}
        <Collapsible open={isRiskOpen} onOpenChange={setIsRiskOpen}>
          <CollapsibleTrigger asChild>
            <Button 
              variant="outline" 
              className="w-full justify-between p-4 h-auto"
            >
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-risk-high" />
                <span className="font-semibold">Fatores de Risco</span>
                <Badge variant="outline" className="border-risk-high text-risk-high">
                  {fatores_risco.length} fatores
                </Badge>
              </div>
              {isRiskOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </CollapsibleTrigger>
          
          <CollapsibleContent className="mt-4 space-y-3">
            {fatores_risco.length > 0 ? (
              fatores_risco
                .sort((a, b) => Math.abs(b.impacto) - Math.abs(a.impacto))
                .map((fator, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-semibold text-risk-high">{fator.fator}</h4>
                        <p className="text-sm text-muted-foreground">
                          Valor: <span className="font-medium">{fator.valor}</span>
                        </p>
                      </div>
                      <Badge variant="outline" className="border-risk-high text-risk-high">
                        {formatImpact(fator.impacto)}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Impacto no risco</span>
                        <span>{Math.round(getImpactWidth(fator.impacto, maxImpact))}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-1000 ease-out ${getImpactColor(fator.impacto)}`}
                          style={{ width: `${getImpactWidth(fator.impacto, maxImpact)}%` }}
                        />
                      </div>
                    </div>
                    
                    <p className="text-sm bg-muted p-3 rounded">
                      {fator.interpretacao}
                    </p>
                  </div>
                ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Shield className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Nenhum fator de risco significativo identificado</p>
              </div>
            )}
          </CollapsibleContent>
        </Collapsible>

        {/* Fatores de Proteção */}
        <Collapsible open={isProtectionOpen} onOpenChange={setIsProtectionOpen}>
          <CollapsibleTrigger asChild>
            <Button 
              variant="outline" 
              className="w-full justify-between p-4 h-auto"
            >
              <div className="flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-risk-low" />
                <span className="font-semibold">Fatores de Proteção</span>
                <Badge variant="outline" className="border-risk-low text-risk-low">
                  {fatores_protecao.length} fatores
                </Badge>
              </div>
              {isProtectionOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </CollapsibleTrigger>
          
          <CollapsibleContent className="mt-4 space-y-3">
            {fatores_protecao.length > 0 ? (
              fatores_protecao
                .sort((a, b) => Math.abs(b.impacto) - Math.abs(a.impacto))
                .map((fator, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-semibold text-risk-low">{fator.fator}</h4>
                        <p className="text-sm text-muted-foreground">
                          Valor: <span className="font-medium">{fator.valor}</span>
                        </p>
                      </div>
                      <Badge variant="outline" className="border-risk-low text-risk-low">
                        {formatImpact(fator.impacto)}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Redução do risco</span>
                        <span>{Math.round(getImpactWidth(fator.impacto, maxImpact))}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-1000 ease-out ${getImpactColor(fator.impacto)}`}
                          style={{ width: `${getImpactWidth(fator.impacto, maxImpact)}%` }}
                        />
                      </div>
                    </div>
                    
                    <p className="text-sm bg-muted p-3 rounded">
                      {fator.interpretacao}
                    </p>
                  </div>
                ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Info className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Nenhum fator de proteção significativo identificado</p>
              </div>
            )}
          </CollapsibleContent>
        </Collapsible>

        {/* Interpretação Geral */}
        <Collapsible open={isInterpretationOpen} onOpenChange={setIsInterpretationOpen}>
          <CollapsibleTrigger asChild>
            <Button 
              variant="outline" 
              className="w-full justify-between p-4 h-auto"
            >
              <div className="flex items-center gap-2">
                <Info className="h-4 w-4 text-medical-primary" />
                <span className="font-semibold">Interpretação Geral</span>
              </div>
              {isInterpretationOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </CollapsibleTrigger>
          
          <CollapsibleContent className="mt-4">
            <div className="bg-medical-primary/5 border border-medical-primary/20 rounded-lg p-4">
              <p className="text-sm leading-relaxed whitespace-pre-line">
                {interpretacao_geral}
              </p>
            </div>
          </CollapsibleContent>
        </Collapsible>
      </CardContent>
    </Card>
  );
}