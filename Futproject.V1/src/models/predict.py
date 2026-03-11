import pandas as pd
import sqlite3
import joblib
import os


def buscar_stats(time_nome):
    conn = sqlite3.connect('db/database.sqlite')
    # Usamos apelidos (as p, as gf, as gs) IGUAIS nas duas partes do UNION
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


def realizar_predicao():
    # Localiza o arquivo .pkl na mesma pasta do script
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_modelo = os.path.join(diretorio, 'random_forest_brasileirao.pkl')

    if not os.path.exists(caminho_modelo):
        print("❌ Modelo (.pkl) não encontrado. Certifique-se de rodar o train.py primeiro.")
        return

    modelo = joblib.load(caminho_modelo)

    print("\n🔮 --- ORÁCULO MULTICLASSE V2 (ESTÁVEL) --- 🔮")
    tm = input("Mandante: ")
    tv = input("Visitante: ")

    s_m = buscar_stats(tm)
    s_v = buscar_stats(tv)

    if s_m.empty or s_v.empty:
        print("⚠️ Dados insuficientes. Verifique se o nome do time está correto no banco.")
        return

    # Organiza os dados exatamente como o modelo espera receber
    entrada = pd.DataFrame([[
        s_m['p'].values[0], s_m['gf'].values[0], s_m['gs'].values[0],
        s_v['p'].values[0], s_v['gf'].values[0], s_v['gs'].values[0]
    ]], columns=['pontos_m', 'gols_feitos_m', 'gols_sofridos_m',
                 'pontos_v', 'gols_feitos_v', 'gols_sofridos_v'])

    # Probabilidades para: [0: Vitória Visitante, 1: Empate, 2: Vitória Mandante]
    prob = modelo.predict_proba(entrada)[0]

    print(f"\n📊 --- ANÁLISE DE PROBABILIDADES ---")
    print(f"🏟️  Vitória {tm}: {prob[2] * 100:.2f}%")
    print(f"🤝  Empate: {prob[1] * 100:.2f}%")
    print(f"🚀  Vitória {tv}: {prob[0] * 100:.2f}%")

    # Veredito final baseado na maior probabilidade
    classes = ["Vitória do Visitante", "Empate", "Vitória do Mandante"]
    palpite = classes[modelo.predict(entrada)[0]]
    print(f"\n⭐ Palpite do Oráculo: {palpite}")


if __name__ == "__main__":
    realizar_predicao()