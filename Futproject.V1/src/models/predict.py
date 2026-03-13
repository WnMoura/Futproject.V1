import pandas as pd
import sqlite3
import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'db', 'database.sqlite')
MODELO_PATH = os.path.join(BASE_DIR, 'src', 'models', 'random_forest_brasileirao.pkl')


def buscar_times_disponiveis() -> list:
    conn = sqlite3.connect(DB_PATH)
    try:
        mandantes = pd.read_sql_query("SELECT DISTINCT mandante as time FROM jogos", conn)
        visitantes = pd.read_sql_query("SELECT DISTINCT visitante as time FROM jogos", conn)
        times = pd.concat([mandantes, visitantes]).drop_duplicates().sort_values('time')
        return times['time'].tolist()
    finally:
        conn.close()


def buscar_stats(time_nome: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT pontos_m as p, gols_feitos_m as gf, gols_sofridos_m as gs, data_jogo
        FROM dataset_modelo WHERE mandante LIKE '%{time_nome}%'
        UNION
        SELECT pontos_v as p, gols_feitos_v as gf, gols_sofridos_v as gs, data_jogo
        FROM dataset_modelo WHERE visitante LIKE '%{time_nome}%'
        ORDER BY data_jogo DESC LIMIT 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def realizar_predicao(mandante: str, visitante: str) -> dict:
    if not os.path.exists(MODELO_PATH):
        raise FileNotFoundError("Modelo não encontrado. Execute o treino primeiro.")

    modelo = joblib.load(MODELO_PATH)

    s_m = buscar_stats(mandante)
    s_v = buscar_stats(visitante)

    if s_m.empty or s_v.empty:
        times_faltando = []
        if s_m.empty:
            times_faltando.append(mandante)
        if s_v.empty:
            times_faltando.append(visitante)
        raise ValueError(f"Dados insuficientes para: {', '.join(times_faltando)}")

    entrada = pd.DataFrame([[
        s_m['p'].values[0], s_m['gf'].values[0], s_m['gs'].values[0],
        s_v['p'].values[0], s_v['gf'].values[0], s_v['gs'].values[0]
    ]], columns=['pontos_m', 'gols_feitos_m', 'gols_sofridos_m',
                 'pontos_v', 'gols_feitos_v', 'gols_sofridos_v'])

    prob = modelo.predict_proba(entrada)[0]
    classes = ["Vitória do Visitante", "Empate", "Vitória do Mandante"]
    palpite = classes[modelo.predict(entrada)[0]]

    return {
        "mandante": mandante,
        "visitante": visitante,
        "prob_mandante": float(prob[2]),
        "prob_empate": float(prob[1]),
        "prob_visitante": float(prob[0]),
        "palpite": palpite,
    }


if __name__ == "__main__":
    tm = input("Mandante: ")
    tv = input("Visitante: ")
    resultado = realizar_predicao(tm, tv)
    print(f"\n🔮 Palpite: {resultado['palpite']}")
    print(f"🏟️  Vitória {resultado['mandante']}: {resultado['prob_mandante'] * 100:.2f}%")
    print(f"🤝  Empate: {resultado['prob_empate'] * 100:.2f}%")
    print(f"🚀  Vitória {resultado['visitante']}: {resultado['prob_visitante'] * 100:.2f}%")