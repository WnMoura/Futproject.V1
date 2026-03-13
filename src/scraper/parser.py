import sqlite3
import time
import pandas as pd
import os
from io import StringIO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'db', 'database.sqlite')

TEMPORADAS = {
    2024: "https://fbref.com/pt/comps/24/2024/horario/2024-Serie-A-Resultados-e-Calendarios",
    2025: "https://fbref.com/pt/comps/24/2025/horario/2025-Serie-A-Resultados-e-Calendarios",
    2026: "https://fbref.com/pt/comps/24/horario/Serie-A-Resultados-e-Calendarios",
}


def conectar_banco():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
    cursor.executemany('''
        INSERT OR IGNORE INTO jogos (campeonato, data_jogo, mandante, visitante, gols_mandante, gols_visitante)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', lista_jogos)
    conn.commit()


def extrair_temporada(driver, url, ano):
    print(f"  → Extraindo Temporada {ano}...")
    driver.get(url)
    time.sleep(5)
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

        if df_jogos is None:
            return []

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
                partes = placar.split('-')
                if len(partes) == 2:
                    try:
                        g_m, g_v = int(partes[0].strip()), int(partes[1].strip())
                        lista_temp.append((
                            f'Brasileirao_{ano}',
                            str(row[col_data]),
                            str(row[col_m]),
                            str(row[col_v]),
                            g_m, g_v
                        ))
                    except ValueError:
                        pass
        return lista_temp
    except Exception as e:
        print(f"  ⚠️  Erro no ano {ano}: {e}")
        return []


def executar_extracao(log_fn=None) -> dict:
    from src.scraper.driver_factory import criar_driver

    def log(msg):
        print(msg)
        if log_fn:
            log_fn(msg)

    log("🚀 Iniciando extração de dados do FBref...")
    conn = conectar_banco()
    driver = criar_driver()

    resultados = {}
    total_novos = 0
    try:
        for ano, url in TEMPORADAS.items():
            dados = extrair_temporada(driver, url, ano)
            if dados:
                salvar_jogos_no_banco(conn, dados)
                resultados[ano] = len(dados)
                total_novos += len(dados)
                log(f"  ✅ {len(dados)} jogos processados para {ano}")
            else:
                resultados[ano] = 0
                log(f"  ⚠️  Nenhum dado novo para {ano}")
    finally:
        driver.quit()
        conn.close()

    log(f"\n✅ Extração concluída! {total_novos} jogos salvos/verificados.")
    return {"total": total_novos, "por_temporada": resultados}


if __name__ == "__main__":
    executar_extracao()
