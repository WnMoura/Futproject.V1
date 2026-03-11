import sqlite3
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def treinar_e_avaliar():
    # Conecta no banco que usamos na engenharia de dados
    conn = sqlite3.connect('db/database.sqlite')

    # Ajustamos a Query para os NOVOS nomes de colunas do 02_feature_engineering.py
    query = """
        SELECT 
            pontos_m, 
            gols_feitos_m, 
            gols_sofridos_m, 
            pontos_v, 
            gols_feitos_v, 
            gols_sofridos_v,
            alvo_resultado
        FROM dataset_modelo
    """

    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    # X: Variáveis preditivas | y: Alvo (0, 1, 2)
    X = df.drop(columns=['alvo_resultado'])
    y = df['alvo_resultado']

    # Divisão treino/teste (usando shuffle=True para misturar os anos)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"Iniciando treino com {len(X_train)} jogos...")

    # Modelo configurado para lidar com 3 classes
    modelo = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    modelo.fit(X_train, y_train)

    # Teste
    previsoes = modelo.predict(X_test)

    print("\n=== RESULTADOS DO MODELO MULTICLASSE ===")
    print(f"Acurácia Geral: {accuracy_score(y_test, previsoes) * 100:.2f}%")

    print("\nRelatório de Classificação:")
    # 0: Visitante, 1: Empate, 2: Mandante
    target_names = ['Vitória Visitante (0)', 'Empate (1)', 'Vitória Mandante (2)']
    print(classification_report(y_test, previsoes, target_names=target_names))

    return modelo


if __name__ == "__main__":
    modelo_final = treinar_e_avaliar()

    # Garante que a pasta existe e salva o modelo
    pasta_modelo = 'src/models'
    if not os.path.exists(pasta_modelo):
        os.makedirs(pasta_modelo)

    caminho_modelo = os.path.join(pasta_modelo, 'random_forest_brasileirao.pkl')
    joblib.dump(modelo_final, caminho_modelo)

    print(f"\n✅ Modelo multiclasse salvo com sucesso em: {caminho_modelo}")