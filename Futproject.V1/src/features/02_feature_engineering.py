import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'db', 'database.sqlite')


def preparar_dataset_final():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM jogos", conn)

    m = df[['data_jogo', 'mandante', 'gols_mandante', 'gols_visitante']].copy()
    m.columns = ['data_jogo', 'time', 'gols_feitos', 'gols_sofridos']
    v = df[['data_jogo', 'visitante', 'gols_visitante', 'gols_mandante']].copy()
    v.columns = ['data_jogo', 'time', 'gols_feitos', 'gols_sofridos']

    historico = pd.concat([m, v]).sort_values(['time', 'data_jogo'])
    historico['pontos'] = historico.apply(
        lambda r: 3 if r['gols_feitos'] > r['gols_sofridos'] else (1 if r['gols_feitos'] == r['gols_sofridos'] else 0),
        axis=1)

    cols_calc = ['time', 'gols_feitos', 'gols_sofridos', 'pontos']
    stats = historico[cols_calc].groupby('time').rolling(window=5, closed='left').mean().reset_index()

    if 'level_1' in stats.columns:
        stats = stats.drop(columns=['level_1'])

    stats_m = stats.rename(
        columns={'pontos': 'pontos_m', 'gols_feitos': 'gols_feitos_m', 'gols_sofridos': 'gols_sofridos_m',
                 'time': 'time_m'})
    stats_v = stats.rename(
        columns={'pontos': 'pontos_v', 'gols_feitos': 'gols_feitos_v', 'gols_sofridos': 'gols_sofridos_v',
                 'time': 'time_v'})

    stats_m['data_jogo'] = historico['data_jogo'].values
    stats_v['data_jogo'] = historico['data_jogo'].values

    # 3. Cruzamento de dados (Merge)
    df_final = df.merge(stats_m, left_on=['mandante', 'data_jogo'], right_on=['time_m', 'data_jogo'])
    df_final = df_final.merge(stats_v, left_on=['visitante', 'data_jogo'], right_on=['time_v', 'data_jogo'])

    def definir_alvo(row):
        if row['gols_mandante'] > row['gols_visitante']: return 2
        if row['gols_mandante'] == row['gols_visitante']: return 1
        return 0

    df_final['alvo_resultado'] = df_final.apply(definir_alvo, axis=1)

    colunas_modelo = ['mandante', 'visitante', 'data_jogo', 'pontos_m', 'gols_feitos_m', 'gols_sofridos_m', 'pontos_v',
                      'gols_feitos_v', 'gols_sofridos_v', 'alvo_resultado']

    df_modelo = df_final[colunas_modelo].dropna()
    df_modelo.to_sql('dataset_modelo', conn, if_exists='replace', index=False)
    conn.close()
    print(f"✅ Dataset Multiclasse pronto com {len(df_modelo)} jogos!")


if __name__ == "__main__":
    preparar_dataset_final()