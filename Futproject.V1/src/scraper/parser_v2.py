import sqlite3
import time
import pandas as pd
import os
from io import StringIO
from driver_factory import criar_driver


def conectar_banco():
    if not os.path.exists('db'):
        os.makedirs('db')
    conn = sqlite3.connect('db/database.sqlite')
    cursor = conn.cursor()
    # Adicionamos UNIQUE em campeonato, data, mandante e visitante para evitar duplicatas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campeonato TEXT,
            data_jogo TEXT,
            mandante TEXT,
            visitante TEXT,
            gols_mandante INTEGER,
            gols_visitante INTEGER,
            UNIQUE(campeonato, data_jogo, mandante, visitante)
        )
    ''')
    conn.commit()
    return conn


def salvar_jogos_no_banco(conn, lista_jogos):
    cursor = conn.cursor()
    # INSERT OR IGNORE garante que jogos antigos não sejam duplicados
    cursor.executemany('''
        INSERT OR IGNORE INTO jogos (campeonato, data_jogo, mandante, visitante, gols_mandante, gols_visitante)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', lista_jogos)
    conn.commit()


def extrair_temporada(driver, url, ano):
    print(f"--- Extraindo Temporada {ano} ---")
    driver.get(url)
    time.sleep(5)

    # Rolagem para carregar a tabela (Lazy Loading)
    driver.execute_script("window.scrollTo(0, 1000);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    html_content = driver.page_source
    try:
        all_tables = pd.read_html(StringIO(html_content), attrs={'class': 'stats_table'})
        df_jogos = None
        for table in all_tables:
            cols = [str(c).lower() for c in table.columns]
            if ('home' in cols or 'mandante' in cols) and ('score' in cols or 'placar' in cols):
                df_jogos = table
                break

        if df_jogos is None: return []

        # Identificação dinâmica de colunas
        col_data = [c for c in df_jogos.columns if 'date' in str(c).lower() or 'data' in str(c).lower()][0]
        col_m = [c for c in df_jogos.columns if 'home' in str(c).lower() or 'mandante' in str(c).lower()][0]
        col_v = [c for c in df_jogos.columns if 'away' in str(c).lower() or 'visitante' in str(c).lower()][0]
        col_p = [c for c in df_jogos.columns if 'score' in str(c).lower() or 'placar' in str(c).lower()][0]

        df_jogos = df_jogos.dropna(subset=[col_p])
        df_jogos = df_jogos[~df_jogos[col_p].astype(str).str.contains('Score|Placar', case=False)]

        lista_temp = []
        for _, row in df_jogos.iterrows():
            placar = str(row[col_p]).replace('–', '-').replace('x', '-')
            if '-' in placar:
                g_m, g_v = placar.split('-')
                lista_temp.append((f'Brasileirao_{ano}', str(row[col_data]), str(row[col_m]),
                                   str(row[col_v]), int(g_m.strip()), int(g_v.strip())))
        return lista_temp
    except Exception as e:
        print(f"Erro no ano {ano}: {e}")
        return []


if __name__ == "__main__":
    conn = conectar_banco()
    driver = criar_driver()

    # Lista de temporadas para criar o "Big Data"
    # O FBref muda levemente a URL para anos passados
    temporadas = {
        2024: "https://fbref.com/pt/comps/24/2024/horario/2024-Serie-A-Resultados-e-Calendarios",
        2025: "https://fbref.com/pt/comps/24/2025/horario/2025-Serie-A-Resultados-e-Calendarios",
        2026: "https://fbref.com/pt/comps/24/horario/Serie-A-Resultados-e-Calendarios"
    }

    for ano, url in temporadas.items():
        dados = extrair_temporada(driver, url, ano)
        if dados:
            salvar_jogos_no_banco(conn, dados)
            print(f"✅ {len(dados)} jogos processados para {ano}")

    driver.quit()
    conn.close()
    print("\n🚀 Base de dados histórica atualizada!")