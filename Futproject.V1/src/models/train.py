import sqlite3
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'db', 'database.sqlite')
MODELO_PATH = os.path.join(BASE_DIR, 'src', 'models', 'random_forest_brasileirao.pkl')


def treinar_modelo(X=None, y=None, log_fn=None) -> dict:
    def log(msg):
        print(msg)
        if log_fn:
            log_fn(msg)

    log("🤖 Iniciando treino do modelo...")

    if X is None or y is None:
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT pontos_m, gols_feitos_m, gols_sofridos_m,
                   pontos_v, gols_feitos_v, gols_sofridos_v, alvo_resultado
            FROM dataset_modelo
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        X = df.drop(columns=['alvo_resultado'])
        y = df['alvo_resultado']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    log(f"  → Treinando com {len(X_train)} jogos | Testando com {len(X_test)} jogos...")

    modelo = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    modelo.fit(X_train, y_train)

    previsoes = modelo.predict(X_test)
    acc = accuracy_score(y_test, previsoes)

    target_names = ['Vitória Visitante', 'Empate', 'Vitória Mandante']
    report = classification_report(y_test, previsoes, target_names=target_names, output_dict=True)
    report_str = classification_report(y_test, previsoes, target_names=target_names)
    cm = confusion_matrix(y_test, previsoes)

    log(f"\n  ✅ Acurácia: {acc * 100:.2f}%")
    log(f"\n  Relatório:\n{report_str}")

    os.makedirs(os.path.dirname(MODELO_PATH), exist_ok=True)
    joblib.dump(modelo, MODELO_PATH)
    log(f"  💾 Modelo salvo em: {MODELO_PATH}")

    return {
        "accuracy": acc,
        "report": report,
        "report_str": report_str,
        "confusion_matrix": cm.tolist(),
        "modelo": modelo,
        "target_names": target_names,
    }


if __name__ == "__main__":
    resultado = treinar_modelo()
    print(f"\nAcurácia final: {resultado['accuracy'] * 100:.2f}%")