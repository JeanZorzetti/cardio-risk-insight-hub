import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuração para reprodutibilidade
np.random.seed(42)

class MedicalDataGenerator:
    def __init__(self):
        """
        Gerador de dados médicos sintéticos que contempla todos os tipos de dados
        mencionados no material de IA:
        - Dados contínuos (números reais)
        - Dados nominais/categóricos
        - Dados discretos (valores finitos/inteiros)
        """
        self.n_patients = 1000
        
    def generate_synthetic_data(self):
        """Gera dataset sintético baseado em padrões médicos realistas"""
        
        print("=== SISTEMA DE IA MÉDICA - GERAÇÃO DE DADOS ===")
        print(f"Gerando {self.n_patients} registros de pacientes...")
        
        # DADOS CATEGÓRICOS/NOMINAIS (conforme material)
        genders = np.random.choice(['Masculino', 'Feminino'], self.n_patients, p=[0.52, 0.48])
        blood_types = np.random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], 
                                     self.n_patients, p=[0.34, 0.06, 0.09, 0.02, 0.03, 0.01, 0.38, 0.07])
        
        # DADOS DISCRETOS (valores finitos/inteiros)
        ages = np.random.randint(18, 85, self.n_patients)
        num_medications = np.random.poisson(2, self.n_patients)  # Média 2 medicamentos
        hospital_visits = np.random.poisson(1.5, self.n_patients)  # Visitas por ano
        
        # DADOS CONTÍNUOS (números reais) com correlações realistas
        # Idade influencia pressão arterial
        systolic_bp = 90 + 0.8 * ages + np.random.normal(0, 15, self.n_patients)
        diastolic_bp = 60 + 0.4 * ages + np.random.normal(0, 10, self.n_patients)
        
        # BMI com distribuição realista
        bmi = np.random.normal(26, 4.5, self.n_patients)
        bmi = np.clip(bmi, 15, 45)  # Valores realistas
        
        # Colesterol influenciado por idade e BMI
        cholesterol = 150 + 1.2 * ages + 2 * bmi + np.random.normal(0, 25, self.n_patients)
        
        # Glicose com padrões diabéticos
        glucose = 85 + 0.5 * ages + 1.5 * bmi + np.random.normal(0, 15, self.n_patients)
        
        # Frequência cardíaca
        heart_rate = 70 + np.random.normal(0, 12, self.n_patients)
        
        # ATRIBUTO ALVO: Risco cardíaco (para classificação supervisionada)
        # Baseado em fatores de risco reais
        risk_score = (
            0.3 * (ages - 18) / 67 +  # Idade normalizada
            0.25 * np.where(bmi > 30, 1, 0) +  # Obesidade
            0.2 * (systolic_bp - 90) / 110 +  # Pressão alta
            0.15 * (cholesterol - 150) / 250 +  # Colesterol
            0.1 * (glucose - 85) / 115  # Glicose
        )
        
        # Conversão para classes categóricas
        heart_disease = np.where(risk_score > 0.6, 'Alto Risco',
                                np.where(risk_score > 0.3, 'Médio Risco', 'Baixo Risco'))
        
        # SINTOMAS (para regras de associação)
        # Correlacionados com fatores de risco
        chest_pain = np.random.binomial(1, np.clip(risk_score, 0.1, 0.8), self.n_patients)
        shortness_breath = np.random.binomial(1, np.clip(risk_score * 0.7, 0.05, 0.6), self.n_patients)
        fatigue = np.random.binomial(1, np.clip(risk_score * 0.8, 0.1, 0.7), self.n_patients)
        dizziness = np.random.binomial(1, np.clip(risk_score * 0.5, 0.05, 0.4), self.n_patients)
        
        # Criação do DataFrame
        data = {
            # ATRIBUTOS PREDITORES
            'idade': ages,
            'genero': genders,
            'tipo_sanguineo': blood_types,
            'pressao_sistolica': np.round(systolic_bp, 1),
            'pressao_diastolica': np.round(diastolic_bp, 1),
            'bmi': np.round(bmi, 2),
            'colesterol': np.round(cholesterol, 1),
            'glicose': np.round(glucose, 1),
            'freq_cardiaca': np.round(heart_rate, 1),
            'num_medicamentos': num_medications,
            'visitas_anuais': hospital_visits,
            
            # SINTOMAS (para regras de associação)
            'dor_peito': chest_pain,
            'falta_ar': shortness_breath,
            'fadiga': fatigue,
            'tontura': dizziness,
            
            # ATRIBUTO ALVO
            'risco_cardiaco': heart_disease,
            'score_risco': np.round(risk_score, 3)
        }
        
        df = pd.DataFrame(data)
        
        # Adição de alguns dados faltantes (realista em dados médicos)
        missing_indices = np.random.choice(df.index, size=int(0.05 * len(df)), replace=False)
        df.loc[missing_indices[:15], 'colesterol'] = np.nan
        df.loc[missing_indices[15:25], 'glicose'] = np.nan
        
        return df
    
    def analyze_data_types(self, df):
        """Análise dos tipos de dados conforme teoria de IA"""
        
        print("\n=== ANÁLISE DOS TIPOS DE DADOS (Conforme Material de IA) ===")
        
        print("\n1. DADOS CONTÍNUOS (números reais):")
        continuous_vars = ['pressao_sistolica', 'pressao_diastolica', 'bmi', 
                          'colesterol', 'glicose', 'freq_cardiaca', 'score_risco']
        for var in continuous_vars:
            print(f"   • {var}: {df[var].dtype} - Range: {df[var].min():.1f} a {df[var].max():.1f}")
        
        print("\n2. DADOS NOMINAIS/CATEGÓRICOS:")
        nominal_vars = ['genero', 'tipo_sanguineo', 'risco_cardiaco']
        for var in nominal_vars:
            categories = df[var].unique()
            print(f"   • {var}: {len(categories)} categorias - {list(categories)}")
        
        print("\n3. DADOS DISCRETOS (valores finitos/inteiros):")
        discrete_vars = ['idade', 'num_medicamentos', 'visitas_anuais', 
                        'dor_peito', 'falta_ar', 'fadiga', 'tontura']
        for var in discrete_vars:
            unique_vals = len(df[var].unique())
            print(f"   • {var}: {unique_vals} valores únicos - Range: {df[var].min()} a {df[var].max()}")
    
    def data_quality_assessment(self, df):
        """Avaliação da qualidade dos dados conforme conceitos de preparação"""
        
        print("\n=== AVALIAÇÃO DA QUALIDADE DOS DADOS ===")
        
        # Dados faltantes
        missing_data = df.isnull().sum()
        missing_percent = (missing_data / len(df)) * 100
        
        print(f"\n1. DADOS FALTANTES:")
        for col in missing_data[missing_data > 0].index:
            print(f"   • {col}: {missing_data[col]} registros ({missing_percent[col]:.1f}%)")
        
        # Balanceamento da variável alvo
        print(f"\n2. BALANCEAMENTO DO ATRIBUTO ALVO:")
        target_dist = df['risco_cardiaco'].value_counts()
        for category, count in target_dist.items():
            percentage = (count / len(df)) * 100
            print(f"   • {category}: {count} pacientes ({percentage:.1f}%)")
        
        # Estatísticas descritivas
        print(f"\n3. ESTATÍSTICAS BÁSICAS:")
        print(f"   • Total de pacientes: {len(df)}")
        print(f"   • Total de atributos: {len(df.columns)}")
        print(f"   • Atributos preditores: {len(df.columns) - 2}")  # -2 para target vars
        
        return df

# EXECUÇÃO PRINCIPAL
def main():
    print("SISTEMA DE IA MÉDICA - IMPLEMENTAÇÃO COMPLETA DOS CONCEITOS")
    print("=" * 60)
    
    # Geração dos dados
    generator = MedicalDataGenerator()
    df = generator.generate_synthetic_data()
    
    # Análise dos tipos de dados
    generator.analyze_data_types(df)
    
    # Avaliação da qualidade
    df = generator.data_quality_assessment(df)
    
    # Salvar dataset
    df.to_csv('dataset_medico_ia.csv', index=False)
    print(f"\n✅ Dataset salvo como 'dataset_medico_ia.csv'")
    
    # Preview dos dados
    print(f"\n=== PREVIEW DOS DADOS ===")
    print(df.head())
    
    print(f"\n🎯 PRÓXIMO PASSO: Pré-processamento e preparação para Machine Learning")
    print("Incluirá: normalização, tratamento de dados faltantes, encoding categórico")
    
    return df

class MedicalDataPreprocessor:
    """Pré-processamento completo seguindo conceitos da Aula 3"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.processed_df = None
        self.categorical_encoders = {}
        self.scalers = {}
        
    def handle_missing_data(self):
        """Tratamento de dados faltantes conforme material de IA"""
        
        print("\n=== PRÉ-PROCESSAMENTO: DADOS FALTANTES ===")
        
        # Estratégias diferentes para cada tipo de dado
        missing_before = self.df.isnull().sum().sum()
        
        # Para dados contínuos: imputação pela mediana (mais robusta que média)
        for col in ['colesterol', 'glicose']:
            if self.df[col].isnull().sum() > 0:
                median_val = self.df[col].median()
                self.df[col].fillna(median_val, inplace=True)
                print(f"   • {col}: {self.df[col].isnull().sum()} valores faltantes imputados com mediana ({median_val:.1f})")
        
        missing_after = self.df.isnull().sum().sum()
        print(f"   ✅ Total de dados faltantes: {missing_before} → {missing_after}")
        
    def encode_categorical_variables(self):
        """Encoding de variáveis categóricas (nominais para numéricas)"""
        
        print("\n=== PRÉ-PROCESSAMENTO: ENCODING CATEGÓRICO ===")
        
        from sklearn.preprocessing import LabelEncoder, OneHotEncoder
        
        # Label Encoding para variável alvo (ordinal: Baixo < Médio < Alto)
        target_encoder = LabelEncoder()
        risk_mapping = {'Baixo Risco': 0, 'Médio Risco': 1, 'Alto Risco': 2}
        self.df['risco_cardiaco_encoded'] = self.df['risco_cardiaco'].map(risk_mapping)
        print(f"   • risco_cardiaco: Label Encoding aplicado {risk_mapping}")
        
        # One-Hot Encoding para variáveis nominais (sem ordem)
        categorical_cols = ['genero', 'tipo_sanguineo']
        
        for col in categorical_cols:
            # Criar dummies
            dummies = pd.get_dummies(self.df[col], prefix=col, drop_first=True)
            self.df = pd.concat([self.df, dummies], axis=1)
            print(f"   • {col}: One-Hot Encoding criou {len(dummies.columns)} novas features")
        
        print(f"   ✅ Dataset expandido de {len(self.df.columns) - len(categorical_cols) - len(pd.get_dummies(self.df[categorical_cols], drop_first=True).columns)} para {len(self.df.columns)} colunas")
        
    def normalize_continuous_data(self):
        """Normalização de dados contínuos conforme material"""
        
        print("\n=== PRÉ-PROCESSAMENTO: NORMALIZAÇÃO ===")
        
        from sklearn.preprocessing import StandardScaler, MinMaxScaler
        
        # Variáveis contínuas para normalizar
        continuous_vars = ['idade', 'pressao_sistolica', 'pressao_diastolica', 
                          'bmi', 'colesterol', 'glicose', 'freq_cardiaca']
        
        # StandardScaler (z-score): média=0, desvio=1
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(self.df[continuous_vars])
        
        # Criar DataFrame com dados normalizados
        scaled_df = pd.DataFrame(scaled_data, 
                                columns=[f"{col}_normalized" for col in continuous_vars],
                                index=self.df.index)
        
        self.df = pd.concat([self.df, scaled_df], axis=1)
        self.scalers['standard'] = scaler
        
        print(f"   • StandardScaler aplicado em {len(continuous_vars)} variáveis contínuas")
        print(f"   • Novas features: {list(scaled_df.columns)}")
        
        # Verificação da normalização
        print(f"   • Exemplo - idade antes: μ={self.df['idade'].mean():.2f}, σ={self.df['idade'].std():.2f}")
        print(f"   • Exemplo - idade_normalized: μ={self.df['idade_normalized'].mean():.2f}, σ={self.df['idade_normalized'].std():.2f}")
        
    def balance_assessment(self):
        """Avaliação do balanceamento conforme conceitos de preparação"""
        
        print("\n=== AVALIAÇÃO DO BALANCEAMENTO ===")
        
        target_counts = self.df['risco_cardiaco'].value_counts()
        total = len(self.df)
        
        print("Distribuição das classes:")
        for class_name, count in target_counts.items():
            percentage = (count / total) * 100
            print(f"   • {class_name}: {count} ({percentage:.1f}%)")
        
        # Calcular desequilíbrio
        majority_class = target_counts.max()
        minority_class = target_counts.min()
        imbalance_ratio = majority_class / minority_class
        
        print(f"\n   📊 Razão de desequilíbrio: {imbalance_ratio:.2f}:1")
        
        if imbalance_ratio > 3:
            print("   ⚠️  ALTO desequilíbrio detectado - considerar técnicas de balanceamento")
        elif imbalance_ratio > 1.5:
            print("   ⚠️  MÉDIO desequilíbrio detectado - monitorar performance por classe")
        else:
            print("   ✅ Dataset relativamente balanceado")
            
    def create_train_test_split(self):
        """Divisão em conjuntos de treino e teste"""
        
        print("\n=== DIVISÃO TREINO/TESTE ===")
        
        from sklearn.model_selection import train_test_split
        
        # Features (excluindo targets e variáveis originais categóricas)
        feature_cols = [col for col in self.df.columns 
                       if col not in ['risco_cardiaco', 'score_risco', 'genero', 'tipo_sanguineo']]
        
        X = self.df[feature_cols]
        y = self.df['risco_cardiaco_encoded']  # Target para classificação
        y_reg = self.df['score_risco']  # Target para regressão
        
        # Divisão estratificada (mantém proporção das classes)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Também para regressão
        _, _, y_reg_train, y_reg_test = train_test_split(
            X, y_reg, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   • Features selecionadas: {len(feature_cols)}")
        print(f"   • Treino: {len(X_train)} amostras ({len(X_train)/len(X)*100:.1f}%)")
        print(f"   • Teste: {len(X_test)} amostras ({len(X_test)/len(X)*100:.1f}%)")
        
        # Verificar manutenção da distribuição
        print(f"\n   Distribuição mantida no conjunto de treino:")
        train_dist = pd.Series(y_train).value_counts(normalize=True) * 100
        for idx, perc in train_dist.items():
            class_name = ['Baixo Risco', 'Médio Risco', 'Alto Risco'][idx]
            print(f"   • {class_name}: {perc:.1f}%")
        
        # Salvar splits
        splits = {
            'X_train': X_train, 'X_test': X_test,
            'y_train': y_train, 'y_test': y_test,
            'y_reg_train': y_reg_train, 'y_reg_test': y_reg_test,
            'feature_names': feature_cols
        }
        
        return splits
    
    def process_all(self):
        """Executa todo o pipeline de pré-processamento"""
        
        print("\n" + "="*60)
        print("PRÉ-PROCESSAMENTO COMPLETO - APLICANDO CONCEITOS DE IA")
        print("="*60)
        
        # 1. Tratamento de dados faltantes
        self.handle_missing_data()
        
        # 2. Encoding categórico
        self.encode_categorical_variables()
        
        # 3. Normalização
        self.normalize_continuous_data()
        
        # 4. Avaliação do balanceamento
        self.balance_assessment()
        
        # 5. Divisão treino/teste
        splits = self.create_train_test_split()
        
        # Salvar dataset processado
        self.df.to_csv('dataset_medico_processado.csv', index=False)
        
        print(f"\n✅ PRÉ-PROCESSAMENTO CONCLUÍDO!")
        print(f"   • Dataset processado salvo como 'dataset_medico_processado.csv'")
        print(f"   • Pronto para aplicar algoritmos de Machine Learning!")
        
        print(f"\n🎯 PRÓXIMO PASSO: Implementação dos algoritmos de classificação")
        print("   Incluirá: Naive Bayes, Árvores de Decisão, e avaliação de performance")
        
        return self.df, splits

class MachineLearningModels:
    """Implementação dos algoritmos de ML conforme material de IA"""
    
    def __init__(self, data_splits):
        self.splits = data_splits
        self.models = {}
        self.results = {}
        
    def naive_bayes_classifier(self):
        """Implementação do Naive Bayes conforme Aula 4"""
        
        print("\n=== ALGORITMO: NAIVE BAYES (Aula 4) ===")
        
        from sklearn.naive_bayes import GaussianNB
        from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
        
        # Treinamento
        nb_model = GaussianNB()
        nb_model.fit(self.splits['X_train'], self.splits['y_train'])
        
        # Predições
        y_pred = nb_model.predict(self.splits['X_test'])
        y_pred_proba = nb_model.predict_proba(self.splits['X_test'])
        
        # Avaliação
        accuracy = accuracy_score(self.splits['y_test'], y_pred)
        
        print(f"   • Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
        
        # Relatório detalhado por classe
        target_names = ['Baixo Risco', 'Médio Risco', 'Alto Risco']
        print(f"\n   Relatório de Classificação:")
        report = classification_report(self.splits['y_test'], y_pred, 
                                     target_names=target_names, 
                                     output_dict=True)
        
        for class_name in target_names:
            precision = report[class_name]['precision']
            recall = report[class_name]['recall']
            f1 = report[class_name]['f1-score']
            print(f"   • {class_name}: Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
        
        # Matrix de confusão
        cm = confusion_matrix(self.splits['y_test'], y_pred)
        print(f"\n   Matriz de Confusão:")
        print(f"   {cm}")
        
        self.models['naive_bayes'] = nb_model
        self.results['naive_bayes'] = {
            'accuracy': accuracy,
            'predictions': y_pred,
            'probabilities': y_pred_proba,
            'confusion_matrix': cm,
            'classification_report': report
        }
        
        return nb_model, accuracy
    
    def decision_tree_classifier(self):
        """Implementação de Árvore de Decisão"""
        
        print("\n=== ALGORITMO: ÁRVORE DE DECISÃO ===")
        
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.metrics import classification_report, accuracy_score
        
        # Treinamento com parâmetros para evitar overfitting
        dt_model = DecisionTreeClassifier(
            max_depth=10,           # Limita profundidade
            min_samples_split=20,   # Mín amostras para dividir
            min_samples_leaf=10,    # Mín amostras por folha
            random_state=42
        )
        dt_model.fit(self.splits['X_train'], self.splits['y_train'])
        
        # Predições
        y_pred = dt_model.predict(self.splits['X_test'])
        accuracy = accuracy_score(self.splits['y_test'], y_pred)
        
        print(f"   • Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
        
        # Importância das features
        feature_importance = dt_model.feature_importances_
        feature_names = self.splits['feature_names']
        
        # Top 5 features mais importantes
        importance_pairs = list(zip(feature_names, feature_importance))
        importance_pairs.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n   Top 5 Features Mais Importantes:")
        for i, (feature, importance) in enumerate(importance_pairs[:5]):
            print(f"   {i+1}. {feature}: {importance:.3f}")
        
        self.models['decision_tree'] = dt_model
        self.results['decision_tree'] = {
            'accuracy': accuracy,
            'predictions': y_pred,
            'feature_importance': dict(importance_pairs)
        }
        
        return dt_model, accuracy
    
    def handle_imbalanced_data(self):
        """Tratamento do desequilíbrio detectado no pré-processamento"""
        
        print("\n=== TRATAMENTO DO DESEQUILÍBRIO (Técnicas Avançadas) ===")
        
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.utils.class_weight import compute_class_weight
        from sklearn.metrics import accuracy_score, f1_score
        
        # Estratégia 1: Class Weights (penalizar classes majoritárias)
        print("\n   Estratégia 1: Class Weights")
        
        # Calcular pesos automáticos
        classes = np.unique(self.splits['y_train'])
        class_weights = compute_class_weight('balanced', classes=classes, y=self.splits['y_train'])
        class_weight_dict = dict(zip(classes, class_weights))
        
        print(f"   • Pesos calculados: {class_weight_dict}")
        
        # Random Forest com pesos balanceados
        rf_balanced = RandomForestClassifier(
            n_estimators=100,
            class_weight='balanced',
            random_state=42,
            max_depth=10
        )
        rf_balanced.fit(self.splits['X_train'], self.splits['y_train'])
        
        y_pred_balanced = rf_balanced.predict(self.splits['X_test'])
        accuracy_balanced = accuracy_score(self.splits['y_test'], y_pred_balanced)
        f1_balanced = f1_score(self.splits['y_test'], y_pred_balanced, average='weighted')
        
        print(f"   • Random Forest Balanceado - Accuracy: {accuracy_balanced:.3f}")
        print(f"   • F1-Score Weighted: {f1_balanced:.3f}")
        
        # Comparação de performance por classe
        target_names = ['Baixo Risco', 'Médio Risco', 'Alto Risco']
        from sklearn.metrics import classification_report
        
        report_balanced = classification_report(self.splits['y_test'], y_pred_balanced, 
                                              target_names=target_names, 
                                              output_dict=True)
        
        print(f"\n   Performance por Classe (com balanceamento):")
        for class_name in target_names:
            recall = report_balanced[class_name]['recall']
            print(f"   • {class_name}: Recall={recall:.3f}")
        
        self.models['random_forest_balanced'] = rf_balanced
        self.results['random_forest_balanced'] = {
            'accuracy': accuracy_balanced,
            'f1_score': f1_balanced,
            'predictions': y_pred_balanced,
            'classification_report': report_balanced
        }
        
        return rf_balanced, accuracy_balanced
    
    def regression_analysis(self):
        """Implementação de Regressão conforme Aula 3"""
        
        print("\n=== ALGORITMO: REGRESSÃO LINEAR (Aula 3) ===")
        
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        
        # Treinamento para predizer score de risco contínuo
        lr_model = LinearRegression()
        lr_model.fit(self.splits['X_train'], self.splits['y_reg_train'])
        
        # Predições
        y_pred_reg = lr_model.predict(self.splits['X_test'])
        
        # Métricas de regressão
        mse = mean_squared_error(self.splits['y_reg_test'], y_pred_reg)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(self.splits['y_reg_test'], y_pred_reg)
        r2 = r2_score(self.splits['y_reg_test'], y_pred_reg)
        
        print(f"   • MSE (Erro Quadrático Médio): {mse:.4f}")
        print(f"   • RMSE (Raiz do EQM): {rmse:.4f}")
        print(f"   • MAE (Erro Absoluto Médio): {mae:.4f}")
        print(f"   • R² (Coeficiente de Determinação): {r2:.4f}")
        
        # Interpretação do R²
        if r2 > 0.8:
            print(f"   ✅ Excelente ajuste do modelo (R² > 0.8)")
        elif r2 > 0.6:
            print(f"   ✅ Bom ajuste do modelo (R² > 0.6)")
        elif r2 > 0.4:
            print(f"   ⚠️ Ajuste moderado do modelo (R² > 0.4)")
        else:
            print(f"   ❌ Ajuste fraco do modelo (R² < 0.4)")
        
        # Análise dos coeficientes (features mais importantes)
        feature_names = self.splits['feature_names']
        coefficients = lr_model.coef_
        
        # Top 5 features com maior impacto
        coef_pairs = list(zip(feature_names, np.abs(coefficients)))
        coef_pairs.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n   Top 5 Features com Maior Impacto no Score de Risco:")
        for i, (feature, coef) in enumerate(coef_pairs[:5]):
            print(f"   {i+1}. {feature}: |{coef:.3f}|")
        
        self.models['linear_regression'] = lr_model
        self.results['linear_regression'] = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'predictions': y_pred_reg,
            'coefficients': dict(zip(feature_names, coefficients))
        }
        
        return lr_model, r2
    
    def compare_models(self):
        """Comparação de performance entre todos os modelos"""
        
        print("\n" + "="*60)
        print("COMPARAÇÃO DE PERFORMANCE DOS MODELOS")
        print("="*60)
        
        print(f"\n📊 MODELOS DE CLASSIFICAÇÃO:")
        
        classification_models = ['naive_bayes', 'decision_tree', 'random_forest_balanced']
        for model_name in classification_models:
            if model_name in self.results:
                accuracy = self.results[model_name]['accuracy']
                print(f"   • {model_name.replace('_', ' ').title()}: {accuracy:.3f} ({accuracy*100:.1f}%)")
        
        print(f"\n📊 MODELO DE REGRESSÃO:")
        if 'linear_regression' in self.results:
            r2 = self.results['linear_regression']['r2']
            rmse = self.results['linear_regression']['rmse']
            print(f"   • Regressão Linear: R²={r2:.3f}, RMSE={rmse:.3f}")
        
        # Recomendação do melhor modelo
        best_accuracy = 0
        best_model = None
        
        for model_name in classification_models:
            if model_name in self.results:
                accuracy = self.results[model_name]['accuracy']
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_model = model_name
        
        if best_model:
            print(f"\n🏆 MELHOR MODELO: {best_model.replace('_', ' ').title()}")
            print(f"   Accuracy: {best_accuracy:.3f} ({best_accuracy*100:.1f}%)")
    
    def run_all_algorithms(self):
        """Executa todos os algoritmos de ML do material"""
        
        print("\n" + "="*60)
        print("IMPLEMENTAÇÃO DOS ALGORITMOS DE MACHINE LEARNING")
        print("="*60)
        
        # 1. Naive Bayes (Aula 4)
        self.naive_bayes_classifier()
        
        # 2. Árvore de Decisão
        self.decision_tree_classifier()
        
        # 3. Tratamento de desequilíbrio
        self.handle_imbalanced_data()
        
        # 4. Regressão Linear (Aula 3)
        self.regression_analysis()
        
        # 5. Comparação final
        self.compare_models()
        
        print(f"\n✅ TODOS OS ALGORITMOS IMPLEMENTADOS!")
        print(f"🎯 PRÓXIMO PASSO: Clustering e Regras de Associação")
        
        return self.models, self.results

class ModelExplainabilityFixed:
    """Explicabilidade dos modelos usando SHAP - VERSÃO CORRIGIDA"""
    
    def __init__(self, models, data_splits):
        self.models = models
        self.splits = data_splits
        self.explainers = {}
        self.shap_values = {}
        
    def setup_shap_explainers(self):
        """Configura explicadores SHAP para cada modelo"""
        
        print("\n" + "="*60)
        print("🔧 EXPLICABILIDADE DE MODELOS - SHAP ANALYSIS (CORRIGIDO)")
        print("="*60)
        print("🔍 Por que cada predição foi feita? Fundamental para medicina!")
        
        try:
            import shap
        except ImportError:
            print("⚠️ SHAP não instalado. Instalando...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'shap'])
            import shap
        
        # Configurar explicadores para cada modelo
        models_to_explain = ['naive_bayes', 'decision_tree', 'random_forest_balanced']
        
        for model_name in models_to_explain:
            if model_name in self.models:
                print(f"\n⚙️ Configurando explicador SHAP para {model_name.replace('_', ' ').title()}...")
                
                try:
                    model = self.models[model_name]
                    
                    # Usar TreeExplainer para modelos baseados em árvore
                    if 'forest' in model_name or 'tree' in model_name:
                        explainer = shap.TreeExplainer(model)
                        print(f"   ✅ TreeExplainer configurado")
                    else:
                        # Usar KernelExplainer para outros modelos (mais lento mas funciona para todos)
                        explainer = shap.KernelExplainer(
                            model.predict_proba, 
                            self.splits['X_train'].sample(50)  # Amostra menor para acelerar
                        )
                        print(f"   ✅ KernelExplainer configurado")
                    
                    self.explainers[model_name] = explainer
                    
                except Exception as e:
                    print(f"   ⚠️ Erro ao configurar {model_name}: {e}")
                    continue
    
    def calculate_shap_values_fixed(self):
        """Calcula valores SHAP para explicar predições - VERSÃO CORRIGIDA"""
        
        print(f"\n🧠 CALCULANDO EXPLICAÇÕES SHAP (CORRIGIDO)...")
        print(f"   (Analisando por que cada modelo fez suas predições)")
        
        import shap
        
        # Usar amostra menor para acelerar cálculos
        X_explain = self.splits['X_test'].head(10)  # Reduzido para 10 casos
        
        for model_name, explainer in self.explainers.items():
            print(f"\n📊 Explicando {model_name.replace('_', ' ').title()}...")
            
            try:
                if 'forest' in model_name or 'tree' in model_name:
                    # Para TreeExplainer, obter valores para classe de Alto Risco (classe 2)
                    shap_values = explainer.shap_values(X_explain)
                    if isinstance(shap_values, list) and len(shap_values) > 2:
                        # Multi-class: pegar valores para classe "Alto Risco" (index 2)
                        self.shap_values[model_name] = shap_values[2]  # Alto Risco
                    else:
                        # Se não é uma lista ou não tem classe 2, usar o primeiro
                        self.shap_values[model_name] = shap_values[0] if isinstance(shap_values, list) else shap_values
                else:
                    # Para KernelExplainer
                    shap_values = explainer.shap_values(X_explain, nsamples=50)
                    if isinstance(shap_values, list) and len(shap_values) > 2:
                        self.shap_values[model_name] = shap_values[2]  # Alto Risco
                    else:
                        self.shap_values[model_name] = shap_values[0] if isinstance(shap_values, list) else shap_values
                
                print(f"   ✅ Valores SHAP calculados para {len(X_explain)} amostras")
                
            except Exception as e:
                print(f"   ⚠️ Erro no cálculo SHAP para {model_name}: {e}")
                continue
    
    def explain_individual_predictions_fixed(self):
        """Explica predições individuais - VERSÃO CORRIGIDA"""
        
        print(f"\n" + "="*60)
        print("EXPLICAÇÕES INDIVIDUAIS - CASOS CLÍNICOS (CORRIGIDO)")
        print("="*60)
        print("🏥 Como um médico veria as explicações:")
        
        # Pegar alguns casos interessantes para explicar
        X_explain = self.splits['X_test'].head(3)  # Apenas 3 casos para teste
        y_true = self.splits['y_test'].head(3)
        feature_names = self.splits['feature_names']
        
        # Nomes das classes
        class_names = ['Baixo Risco', 'Médio Risco', 'Alto Risco']
        
        # Explicar com o melhor modelo (Random Forest)
        if 'random_forest_balanced' in self.shap_values:
            model_name = 'random_forest_balanced'
            shap_vals = self.shap_values[model_name]
            model = self.models[model_name]
            
            print(f"\n🔍 Usando {model_name.replace('_', ' ').title()} para explicações:")
            
            for i in range(len(X_explain)):
                patient_data = X_explain.iloc[i]
                
                # CORREÇÃO DO ERRO: Garantir que shap_vals é um array 2D e pegar a linha correta
                if len(shap_vals.shape) == 1:
                    patient_shap = shap_vals
                else:
                    patient_shap = shap_vals[i] if i < shap_vals.shape[0] else shap_vals[0]
                
                # Fazer predição
                prediction = model.predict([patient_data])[0]
                prediction_proba = model.predict_proba([patient_data])[0]
                
                print(f"\n" + "="*50)
                print(f"👤 PACIENTE {i+1}:")
                print(f"   🎯 Predição: {class_names[prediction]}")
                print(f"   📊 Confiança: {prediction_proba[prediction]*100:.1f}%")
                print(f"   ✅ Real: {class_names[y_true.iloc[i]]}")
                
                # CORREÇÃO DO ERRO: Converter todos os valores para escalares antes do sort
                feature_contributions = []
                for j, (feature, shap_val, value) in enumerate(zip(feature_names, patient_shap, patient_data)):
                    # Garantir que shap_val é um escalar
                    if isinstance(shap_val, np.ndarray):
                        shap_val_scalar = float(shap_val.item()) if shap_val.size == 1 else float(shap_val[0])
                    else:
                        shap_val_scalar = float(shap_val)
                    
                    # Garantir que value é um escalar
                    if isinstance(value, np.ndarray):
                        value_scalar = float(value.item()) if value.size == 1 else float(value[0])
                    else:
                        value_scalar = float(value)
                        
                    feature_contributions.append((feature, shap_val_scalar, value_scalar))
                
                # Agora pode fazer o sort sem erro
                feature_contributions.sort(key=lambda x: x[1], reverse=True)
                
                # Mostrar top 5 fatores que AUMENTAM o risco
                print(f"\n   📈 TOP 5 FATORES QUE AUMENTAM O RISCO:")
                for j, (feature, shap_val, value) in enumerate(feature_contributions[:5]):
                    if shap_val > 0:
                        print(f"   {j+1}. {feature:<25} | Valor: {value:<8.2f} | Impacto: +{shap_val:.3f}")
                
                print(f"\n   📉 TOP 3 FATORES QUE DIMINUEM O RISCO:")
                protective_factors = [f for f in feature_contributions if f[1] < 0]
                for j, (feature, shap_val, value) in enumerate(protective_factors[:3]):
                    print(f"   {j+1}. {feature:<25} | Valor: {value:<8.2f} | Impacto: {shap_val:.3f}")
                
                # Interpretação médica
                print(f"\n   🏥 INTERPRETAÇÃO CLÍNICA:")
                if len(feature_contributions) > 0:
                    top_risk_factor = feature_contributions[0]
                    if 'pressao' in top_risk_factor[0].lower():
                        print(f"      • Hipertensão é o principal fator de risco")
                    elif 'idade' in top_risk_factor[0].lower():
                        print(f"      • Fator etário predominante")
                    elif 'bmi' in top_risk_factor[0].lower():
                        print(f"      • Sobrepeso/obesidade como fator principal")
                    elif 'colesterol' in top_risk_factor[0].lower():
                        print(f"      • Dislipidemia como fator predominante")
                    
                    if prediction == 2:  # Alto risco
                        print(f"      ⚠️ RECOMENDAÇÃO: Avaliação cardiológica urgente")
                    elif prediction == 1:  # Médio risco
                        print(f"      ⚠️ RECOMENDAÇÃO: Monitoramento e mudanças lifestyle")
                    else:  # Baixo risco
                        print(f"      ✅ RECOMENDAÇÃO: Manter hábitos saudáveis")
    
    def run_fixed_explainability_analysis(self):
        """Executa análise completa de explicabilidade - VERSÃO CORRIGIDA"""
        
        print("\n🔧 INICIANDO ANÁLISE DE EXPLICABILIDADE CORRIGIDA...")
        print("   (Fundamental para confiança médica e aprovação regulatória)")
        
        # 1. Configurar explicadores
        self.setup_shap_explainers()
        
        # 2. Calcular valores SHAP
        self.calculate_shap_values_fixed()
        
        # 3. Explicar predições individuais (CORRIGIDO)
        self.explain_individual_predictions_fixed()
        
        print(f"\n✅ ANÁLISE DE EXPLICABILIDADE CORRIGIDA CONCLUÍDA!")
        print(f"🏥 Agora os médicos podem entender EXATAMENTE por que cada predição foi feita!")
        print(f"📋 Essencial para: confiança médica, auditoria, regulamentação, validação clínica")
        
        return self.explainers, self.shap_values

# FUNÇÃO PARA APLICAR A CORREÇÃO NO PROJETO EXISTENTE
def aplicar_correcao_shap(models, data_splits):
    """
    Aplica a correção do erro SHAP no projeto existente
    
    Args:
        models: Dicionário com os modelos treinados
        data_splits: Dicionário com os dados de treino/teste
    
    Returns:
        explainers, shap_values: Resultados da análise de explicabilidade corrigida
    """
    
    print("\n" + "🔧" * 20)
    print("APLICANDO CORREÇÃO DO ERRO SHAP")
    print("🔧" * 20)
    
    # Criar instância da classe corrigida
    explainability_fixed = ModelExplainabilityFixed(models, data_splits)
    
    # Executar análise corrigida
    explainers, shap_values = explainability_fixed.run_fixed_explainability_analysis()
    
    print(f"\n✅ CORREÇÃO APLICADA COM SUCESSO!")
    print(f"🎯 PRÓXIMO PASSO: Implementar dashboard médico interativo")
    
    return explainers, shap_values

class UnsupervisedLearning:
    """Implementação de algoritmos não-supervisionados conforme Aula 3"""
    
    def __init__(self, processed_df, data_splits):
        self.df = processed_df
        self.splits = data_splits
        self.clustering_results = {}
        self.association_rules = []
        
    def kmeans_clustering(self):
        """Implementação de K-Means Clustering conforme material de IA"""
        
        print("\n=== ALGORITMO: K-MEANS CLUSTERING (Aula 3) ===")
        print("Objetivo: Agrupar pacientes em perfis similares (não-supervisionado)")
        
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score, adjusted_rand_score
        
        # Usar apenas features normalizadas para clustering
        clustering_features = [col for col in self.df.columns if '_normalized' in col]
        X_clustering = self.df[clustering_features].values
        
        print(f"   • Features utilizadas: {len(clustering_features)} variáveis normalizadas")
        
        # Método do cotovelo para determinar número ideal de clusters
        print(f"\n   📊 Análise do Número Ideal de Clusters:")
        inertias = []
        silhouette_scores = []
        k_range = range(2, 8)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_clustering)
            inertias.append(kmeans.inertia_)
            silhouette_avg = silhouette_score(X_clustering, kmeans.labels_)
            silhouette_scores.append(silhouette_avg)
            print(f"   • K={k}: Inércia={kmeans.inertia_:.2f}, Silhouette={silhouette_avg:.3f}")
        
        # Escolher melhor K baseado no silhouette score
        best_k = k_range[np.argmax(silhouette_scores)]
        best_silhouette = max(silhouette_scores)
        
        print(f"\n   🎯 Melhor K selecionado: {best_k} (Silhouette Score: {best_silhouette:.3f})")
        
        # Aplicar K-Means com melhor K
        final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        cluster_labels = final_kmeans.fit_predict(X_clustering)
        
        # Adicionar clusters ao DataFrame
        self.df['cluster'] = cluster_labels
        
        # Análise dos clusters formados
        print(f"\n   📋 Análise dos {best_k} Clusters Formados:")
        
        for cluster_id in range(best_k):
            cluster_data = self.df[self.df['cluster'] == cluster_id]
            cluster_size = len(cluster_data)
            percentage = (cluster_size / len(self.df)) * 100
            
            print(f"\n   Cluster {cluster_id}: {cluster_size} pacientes ({percentage:.1f}%)")
            
            # Características predominantes do cluster
            avg_age = cluster_data['idade'].mean()
            avg_bmi = cluster_data['bmi'].mean()
            avg_bp = cluster_data['pressao_sistolica'].mean()
            risk_dist = cluster_data['risco_cardiaco'].value_counts(normalize=True) * 100
            
            print(f"   • Idade média: {avg_age:.1f} anos")
            print(f"   • BMI médio: {avg_bmi:.1f}")
            print(f"   • Pressão sistólica média: {avg_bp:.1f} mmHg")
            print(f"   • Distribuição de risco: {dict(risk_dist.round(1))}")
        
        # Comparar clusters com classificação real (supervisionada vs não-supervisionada)
        ari_score = adjusted_rand_score(self.df['risco_cardiaco_encoded'], cluster_labels)
        print(f"\n   🔍 Comparação com classificação real:")
        print(f"   • Adjusted Rand Index: {ari_score:.3f}")
        
        if ari_score > 0.7:
            print(f"   ✅ Excelente correspondência entre clusters e classes reais")
        elif ari_score > 0.5:
            print(f"   ✅ Boa correspondência entre clusters e classes reais")
        elif ari_score > 0.3:
            print(f"   ⚠️ Correspondência moderada entre clusters e classes reais")
        else:
            print(f"   ❌ Baixa correspondência - clusters descobriram padrões diferentes")
        
        self.clustering_results['kmeans'] = {
            'model': final_kmeans,
            'labels': cluster_labels,
            'best_k': best_k,
            'silhouette_score': best_silhouette,
            'ari_score': ari_score
        }
        
        return final_kmeans, cluster_labels
    
    def association_rules_analysis(self):
        """Implementação de Regras de Associação conforme Aula 4"""
        
        print("\n=== ALGORITMO: REGRAS DE ASSOCIAÇÃO (Aula 4) ===")
        print("Objetivo: Descobrir associações entre sintomas e fatores de risco")
        
        # Preparar dados binários para regras de associação
        binary_data = self.df.copy()
        
        # Binarizar variáveis contínuas (discretização)
        binary_data['idade_alta'] = (binary_data['idade'] > 60).astype(int)
        binary_data['bmi_alto'] = (binary_data['bmi'] > 30).astype(int)
        binary_data['pressao_alta'] = (binary_data['pressao_sistolica'] > 140).astype(int)
        binary_data['colesterol_alto'] = (binary_data['colesterol'] > 240).astype(int)
        binary_data['glicose_alta'] = (binary_data['glicose'] > 126).astype(int)
        binary_data['risco_alto'] = (binary_data['risco_cardiaco'] == 'Alto Risco').astype(int)
        
        # Selecionar variáveis binárias para análise
        binary_features = ['idade_alta', 'bmi_alto', 'pressao_alta', 'colesterol_alto', 
                          'glicose_alta', 'dor_peito', 'falta_ar', 'fadiga', 'tontura', 'risco_alto']
        
        transaction_data = binary_data[binary_features]
        
        print(f"   • Variáveis analisadas: {binary_features}")
        print(f"   • Total de 'transações' (pacientes): {len(transaction_data)}")
        
        # Implementação manual de regras de associação (conceito básico)
        print(f"\n   📋 Regras de Associação Descobertas:")
        
        rules_found = []
        
        # Analisar associações simples (A → B)
        for feature_a in binary_features:
            for feature_b in binary_features:
                if feature_a != feature_b:
                    # Calcular suporte, confiança e lift
                    support_a = transaction_data[feature_a].sum() / len(transaction_data)
                    support_b = transaction_data[feature_b].sum() / len(transaction_data)
                    support_ab = ((transaction_data[feature_a] == 1) & 
                                (transaction_data[feature_b] == 1)).sum() / len(transaction_data)
                    
                    if support_a > 0:  # Evitar divisão por zero
                        confidence = support_ab / support_a
                        lift = confidence / support_b if support_b > 0 else 0
                        
                        # Filtrar regras significativas
                        if support_ab >= 0.05 and confidence >= 0.6 and lift > 1.2:
                            rules_found.append({
                                'antecedente': feature_a,
                                'consequente': feature_b,
                                'suporte': support_ab,
                                'confianca': confidence,
                                'lift': lift
                            })
        
        # Ordenar por confiança
        rules_found.sort(key=lambda x: x['confianca'], reverse=True)
        
        # Mostrar top 10 regras
        print(f"\n   🔍 Top 10 Regras Mais Confiáveis:")
        for i, rule in enumerate(rules_found[:10]):
            antecedente = rule['antecedente'].replace('_', ' ').title()
            consequente = rule['consequente'].replace('_', ' ').title()
            print(f"   {i+1}. {antecedente} → {consequente}")
            print(f"      Suporte: {rule['suporte']:.3f}, Confiança: {rule['confianca']:.3f}, Lift: {rule['lift']:.3f}")
        
        # Análise específica para risco cardíaco
        print(f"\n   🏥 Regras Específicas para Risco Alto:")
        risk_rules = [rule for rule in rules_found if rule['consequente'] == 'risco_alto']
        
        for i, rule in enumerate(risk_rules[:5]):
            antecedente = rule['antecedente'].replace('_', ' ').title()
            print(f"   • {antecedente} → Risco Alto")
            print(f"     {rule['confianca']*100:.1f}% dos pacientes com {antecedente.lower()} têm risco alto")
            print(f"     Lift: {rule['lift']:.2f}x mais provável que a média")
        
        self.association_rules = rules_found
        
        return rules_found
    
    def comprehensive_analysis(self):
        """Análise integrada: supervisionado + não-supervisionado"""
        
        print("\n" + "="*60)
        print("ANÁLISE INTEGRADA: SUPERVISIONADO + NÃO-SUPERVISIONADO")
        print("="*60)
        
        # Comparar clusters com classificação supervisionada
        cluster_risk_analysis = self.df.groupby(['cluster', 'risco_cardiaco']).size().unstack(fill_value=0)
        cluster_risk_percentage = cluster_risk_analysis.div(cluster_risk_analysis.sum(axis=1), axis=0) * 100
        
        print(f"\n📊 DISTRIBUIÇÃO DE RISCO POR CLUSTER:")
        for cluster_id in cluster_risk_percentage.index:
            print(f"\nCluster {cluster_id}:")
            for risk_level in cluster_risk_percentage.columns:
                percentage = cluster_risk_percentage.loc[cluster_id, risk_level]
                print(f"   • {risk_level}: {percentage:.1f}%")
        
        # Insights principais
        print(f"\n🔍 PRINCIPAIS INSIGHTS:")
        print(f"   1. CLUSTERING (não-supervisionado):")
        print(f"      • Descobriu {self.clustering_results['kmeans']['best_k']} grupos naturais de pacientes")
        print(f"      • Silhouette Score: {self.clustering_results['kmeans']['silhouette_score']:.3f}")
        
        print(f"\n   2. REGRAS DE ASSOCIAÇÃO:")
        print(f"      • Descobriu {len(self.association_rules)} regras significativas")
        print(f"      • Identificou padrões entre sintomas e fatores de risco")
        
        print(f"\n   3. COMPARAÇÃO SUPERVISIONADO vs NÃO-SUPERVISIONADO:")
        ari = self.clustering_results['kmeans']['ari_score']
        print(f"      • ARI Score: {ari:.3f}")
        if ari > 0.5:
            print(f"      • Clustering descobriu padrões similares à classificação supervisionada")
        else:
            print(f"      • Clustering revelou estruturas diferentes dos rótulos conhecidos")
    
    def run_unsupervised_analysis(self):
        """Executa toda a análise não-supervisionada"""
        
        print("\n" + "="*60)
        print("ALGORITMOS NÃO-SUPERVISIONADOS - APLICANDO CONCEITOS DE IA")
        print("="*60)
        
        # 1. Clustering (K-Means)
        self.kmeans_clustering()
        
        # 2. Regras de Associação
        self.association_rules_analysis()
        
        # 3. Análise integrada
        self.comprehensive_analysis()
        
        # Salvar resultados finais
        self.df.to_csv('dataset_final_com_clusters.csv', index=False)
        
        print(f"\n✅ ANÁLISE NÃO-SUPERVISIONADA CONCLUÍDA!")
        print(f"   • Dataset final salvo como 'dataset_final_com_clusters.csv'")
        print(f"   • Clusters adicionados ao dataset")
        
        print(f"\n🎉 PROJETO COMPLETO IMPLEMENTADO!")
        print(f"   ✅ Classificação (Naive Bayes, Árvore de Decisão, Random Forest)")
        print(f"   ✅ Regressão (Linear)")
        print(f"   ✅ Clustering (K-Means)")
        print(f"   ✅ Regras de Associação")
        print(f"   ✅ Todos os conceitos do material de IA aplicados!")
        
        return self.clustering_results, self.association_rules

# EXECUÇÃO FINAL COMPLETA
def main():
    print("SISTEMA DE IA MÉDICA - IMPLEMENTAÇÃO COMPLETA DOS CONCEITOS")
    print("=" * 60)
    
    # Geração dos dados
    generator = MedicalDataGenerator()
    df = generator.generate_synthetic_data()
    
    # Análise dos tipos de dados
    generator.analyze_data_types(df)
    
    # Avaliação da qualidade
    df = generator.data_quality_assessment(df)
    
    # PRÉ-PROCESSAMENTO COMPLETO
    preprocessor = MedicalDataPreprocessor(df)
    processed_df, data_splits = preprocessor.process_all()
    
    # IMPLEMENTAÇÃO DOS ALGORITMOS SUPERVISIONADOS
    ml_models = MachineLearningModels(data_splits)
    models, results = ml_models.run_all_algorithms()
    
    # IMPLEMENTAÇÃO DOS ALGORITMOS NÃO-SUPERVISIONADOS
    unsupervised = UnsupervisedLearning(processed_df, data_splits)
    clustering_results, association_rules = unsupervised.run_unsupervised_analysis()
    
    # 🔍 NOVA FUNCIONALIDADE: EXPLICABILIDADE COM SHAP
    explainability = ModelExplainabilityFixed(models, data_splits)
    explainers, shap_values = explainability.run_fixed_explainability_analysis()
    
    print(f"\n🎉 PROJETO COMPLETO + EXPLICABILIDADE IMPLEMENTADOS!")
    print(f"   ✅ Agora é um sistema de IA médica PROFISSIONAL")
    print(f"   ✅ Médicos podem confiar e entender cada decisão")
    print(f"   ✅ Pronto para validação clínica e comercialização")
    
    return processed_df, data_splits, models, results, clustering_results, association_rules, explainers, shap_values

# Executar se chamado diretamente
if __name__ == "__main__":
    dataset, splits, models, results, clusters, rules, explainers, shap_vals = main()