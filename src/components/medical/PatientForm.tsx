import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { User, Heart, Activity, Scale, TestTube, Calendar, AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

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

interface PatientFormProps {
  onSubmit: (data: PatientData) => void;
  loading: boolean;
}

export default function PatientForm({ onSubmit, loading }: PatientFormProps) {
  const [formData, setFormData] = useState<PatientData>({
    idade: 45,
    genero: "",
    tipo_sanguineo: "",
    pressao_sistolica: 120,
    pressao_diastolica: 80,
    freq_cardiaca: 72,
    peso: 70,
    altura: 1.70,
    colesterol: 200,
    glicose: 100,
    num_medicamentos: 0,
    visitas_anuais: 1,
    dor_peito: false,
    falta_ar: false,
    fadiga: false,
    tontura: false,
  });

  const [bmi, setBmi] = useState<number>(0);

  const updateField = (field: keyof PatientData, value: any) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    
    // Calcular BMI automaticamente
    if (field === 'peso' || field === 'altura') {
      if (newData.peso && newData.altura) {
        const calculatedBmi = newData.peso / (newData.altura * newData.altura);
        setBmi(Number(calculatedBmi.toFixed(1)));
      }
    }
  };

  const getBmiStatus = () => {
    if (bmi === 0) return { text: "Calcular", color: "secondary" };
    if (bmi < 18.5) return { text: "Baixo Peso", color: "risk-medium" };
    if (bmi < 25) return { text: "Normal", color: "risk-low" };
    if (bmi < 30) return { text: "Sobrepeso", color: "risk-medium" };
    return { text: "Obesidade", color: "risk-high" };
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const loadExample = () => {
    setFormData({
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
    });
    // Calcular BMI do exemplo
    setBmi(26.1);
  };

  const bmiStatus = getBmiStatus();

  return (
    <Card className="w-full">
      <CardHeader className="bg-medical-primary text-medical-primary-foreground">
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
          Dados do Paciente
        </CardTitle>
        <div className="flex gap-2">
          <Button 
            onClick={loadExample} 
            variant="secondary" 
            size="sm"
            type="button"
          >
            Carregar Exemplo
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dados Básicos */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-medical-primary font-semibold">
              <User className="h-4 w-4" />
              Dados Básicos
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="idade">Idade (anos)</Label>
                <Input
                  id="idade"
                  type="number"
                  min="18"
                  max="120"
                  value={formData.idade}
                  onChange={(e) => updateField('idade', Number(e.target.value))}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="genero">Gênero</Label>
                <Select 
                  value={formData.genero} 
                  onValueChange={(value) => updateField('genero', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Masculino">Masculino</SelectItem>
                    <SelectItem value="Feminino">Feminino</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="tipo_sanguineo">Tipo Sanguíneo</Label>
                <Select 
                  value={formData.tipo_sanguineo} 
                  onValueChange={(value) => updateField('tipo_sanguineo', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="A+">A+</SelectItem>
                    <SelectItem value="A-">A-</SelectItem>
                    <SelectItem value="B+">B+</SelectItem>
                    <SelectItem value="B-">B-</SelectItem>
                    <SelectItem value="AB+">AB+</SelectItem>
                    <SelectItem value="AB-">AB-</SelectItem>
                    <SelectItem value="O+">O+</SelectItem>
                    <SelectItem value="O-">O-</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <Separator />

          {/* Dados Vitais */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-medical-primary font-semibold">
              <Heart className="h-4 w-4" />
              Dados Vitais
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="pressao_sistolica">Pressão Sistólica (mmHg)</Label>
                <Input
                  id="pressao_sistolica"
                  type="number"
                  min="70"
                  max="250"
                  value={formData.pressao_sistolica}
                  onChange={(e) => updateField('pressao_sistolica', Number(e.target.value))}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="pressao_diastolica">Pressão Diastólica (mmHg)</Label>
                <Input
                  id="pressao_diastolica"
                  type="number"
                  min="40"
                  max="150"
                  value={formData.pressao_diastolica}
                  onChange={(e) => updateField('pressao_diastolica', Number(e.target.value))}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="freq_cardiaca">Frequência Cardíaca (bpm)</Label>
                <Input
                  id="freq_cardiaca"
                  type="number"
                  min="40"
                  max="200"
                  value={formData.freq_cardiaca}
                  onChange={(e) => updateField('freq_cardiaca', Number(e.target.value))}
                  required
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Antropometria */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-medical-primary font-semibold">
              <Scale className="h-4 w-4" />
              Antropometria
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="peso">Peso (kg)</Label>
                <Input
                  id="peso"
                  type="number"
                  min="30"
                  max="300"
                  step="0.1"
                  value={formData.peso}
                  onChange={(e) => updateField('peso', Number(e.target.value))}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="altura">Altura (m)</Label>
                <Input
                  id="altura"
                  type="number"
                  min="1.0"
                  max="2.5"
                  step="0.01"
                  value={formData.altura}
                  onChange={(e) => updateField('altura', Number(e.target.value))}
                  required
                />
              </div>
              
              <div>
                <Label>IMC Calculado</Label>
                <div className="flex items-center gap-2 mt-2">
                  <Badge 
                    variant="outline" 
                    className={`${bmiStatus.color === 'risk-high' ? 'border-risk-high text-risk-high' : 
                      bmiStatus.color === 'risk-medium' ? 'border-risk-medium text-risk-medium' : 
                      bmiStatus.color === 'risk-low' ? 'border-risk-low text-risk-low' : 
                      'border-muted text-muted-foreground'}`}
                  >
                    {bmi > 0 ? `${bmi} kg/m²` : '0.0 kg/m²'}
                  </Badge>
                  <Badge 
                    variant="outline"
                    className={`${bmiStatus.color === 'risk-high' ? 'border-risk-high text-risk-high' : 
                      bmiStatus.color === 'risk-medium' ? 'border-risk-medium text-risk-medium' : 
                      bmiStatus.color === 'risk-low' ? 'border-risk-low text-risk-low' : 
                      'border-muted text-muted-foreground'}`}
                  >
                    {bmiStatus.text}
                  </Badge>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* Exames Laboratoriais */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-medical-primary font-semibold">
              <TestTube className="h-4 w-4" />
              Exames Laboratoriais
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="colesterol">Colesterol Total (mg/dL)</Label>
                <Input
                  id="colesterol"
                  type="number"
                  min="100"
                  max="500"
                  value={formData.colesterol}
                  onChange={(e) => updateField('colesterol', Number(e.target.value))}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="glicose">Glicose (mg/dL)</Label>
                <Input
                  id="glicose"
                  type="number"
                  min="50"
                  max="400"
                  value={formData.glicose}
                  onChange={(e) => updateField('glicose', Number(e.target.value))}
                  required
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Histórico Médico */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-medical-primary font-semibold">
              <Calendar className="h-4 w-4" />
              Histórico Médico
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="num_medicamentos">Número de Medicamentos</Label>
                <Input
                  id="num_medicamentos"
                  type="number"
                  min="0"
                  max="20"
                  value={formData.num_medicamentos}
                  onChange={(e) => updateField('num_medicamentos', Number(e.target.value))}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="visitas_anuais">Visitas Médicas/Ano</Label>
                <Input
                  id="visitas_anuais"
                  type="number"
                  min="0"
                  max="50"
                  value={formData.visitas_anuais}
                  onChange={(e) => updateField('visitas_anuais', Number(e.target.value))}
                  required
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Sintomas */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-medical-primary font-semibold">
              <AlertTriangle className="h-4 w-4" />
              Sintomas Atuais
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="dor_peito"
                  checked={formData.dor_peito}
                  onCheckedChange={(checked) => updateField('dor_peito', !!checked)}
                />
                <Label htmlFor="dor_peito">Dor no peito</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="falta_ar"
                  checked={formData.falta_ar}
                  onCheckedChange={(checked) => updateField('falta_ar', !!checked)}
                />
                <Label htmlFor="falta_ar">Falta de ar</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="fadiga"
                  checked={formData.fadiga}
                  onCheckedChange={(checked) => updateField('fadiga', !!checked)}
                />
                <Label htmlFor="fadiga">Fadiga</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="tontura"
                  checked={formData.tontura}
                  onCheckedChange={(checked) => updateField('tontura', !!checked)}
                />
                <Label htmlFor="tontura">Tontura</Label>
              </div>
            </div>
          </div>

          <Separator />

          {/* Botão de Análise */}
          <div className="pt-4">
            <Button 
              type="submit" 
              className="w-full bg-medical-primary hover:bg-medical-secondary text-medical-primary-foreground"
              disabled={loading}
              size="lg"
            >
              <Activity className="mr-2 h-4 w-4" />
              {loading ? "Analisando Risco Cardíaco..." : "Analisar Risco Cardíaco"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}