import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

st.set_page_config(
    page_title="Futproject.V1 Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #0f1923 50%, #0d1117 100%);
    }

    .main-header {
        background: linear-gradient(135deg, #1a2332 0%, #243447 100%);
        border: 1px solid #2d3f55;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        margin: 4px 0 0;
        color: #8899aa;
        font-size: 0.95rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #1a2332 0%, #1e2d42 100%);
        border: 1px solid #2d3f55;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        border-color: #00d4ff55;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,212,255,0.08);
    }
    .metric-label {
        color: #8899aa;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #e2e8f0;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
    }
    .metric-sub {
        color: #00d4ff;
        font-size: 0.8rem;
        margin-top: 4px;
    }

    .badge-ok {
        background: #0d4a2e;
        color: #4ade80;
        border: 1px solid #166534;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-warn {
        background: #3d2f00;
        color: #facc15;
        border: 1px solid #713f12;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .section-title {
        color: #00d4ff;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #2d3f55;
    }

    .pred-card {
        background: linear-gradient(135deg, #1a2332, #1e2d42);
        border-radius: 16px;
        border: 1px solid #2d3f55;
        padding: 28px;
        text-align: center;
        margin-top: 16px;
    }
    .pred-result {
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .pred-palpite {
        color: #4ade80;
        font-size: 1.1rem;
        font-weight: 600;
    }

    .log-box {
        background: #0d1117;
        border: 1px solid #2d3f55;
        border-radius: 10px;
        padding: 16px 20px;
        font-family: 'JetBrains Mono', 'Fira Mono', monospace;
        font-size: 0.82rem;
        color: #7ee787;
        max-height: 320px;
        overflow-y: auto;
        white-space: pre-wrap;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0099cc, #0066aa);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 10px 28px;
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #00b8e6, #0077bb);
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0,153,204,0.4);
    }
    .stSelectbox > div > div {
        background: #1a2332;
        border: 1px solid #2d3f55;
        border-radius: 10px;
        color: #e2e8f0;
    }
    .stSuccess, .stError, .stInfo, .stWarning {
        border-radius: 10px;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1923 0%, #0d1117 100%);
        border-right: 1px solid #2d3f55;
    }
    div[data-testid="stTab"] {
        color: #8899aa;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = os.path.join(BASE_DIR, 'db', 'database.sqlite')
MODELO_PATH = os.path.join(BASE_DIR, 'src', 'models', 'random_forest_brasileirao.pkl')


@st.cache_data(ttl=30)
def get_db_stats():
    if not os.path.exists(DB_PATH):
        return None
    try:
        conn = sqlite3.connect(DB_PATH)
        total = pd.read_sql_query("SELECT COUNT(*) as n FROM jogos", conn)['n'][0]
        ultima = pd.read_sql_query("SELECT MAX(data_jogo) as d FROM jogos", conn)['d'][0]
        temporadas = pd.read_sql_query(
            "SELECT campeonato, COUNT(*) as jogos FROM jogos GROUP BY campeonato ORDER BY campeonato", conn
        )
        tem_modelo = pd.read_sql_query(
            "SELECT COUNT(*) as n FROM sqlite_master WHERE type='table' AND name='dataset_modelo'", conn
        )['n'][0] > 0
        dataset_rows = 0
        if tem_modelo:
            dataset_rows = pd.read_sql_query("SELECT COUNT(*) as n FROM dataset_modelo", conn)['n'][0]
        conn.close()
        return {
            "total_jogos": int(total),
            "ultima_data": ultima,
            "temporadas": temporadas,
            "tem_modelo": os.path.exists(MODELO_PATH),
            "dataset_rows": int(dataset_rows),
        }
    except Exception as e:
        return {"erro": str(e)}


@st.cache_data(ttl=60)
def get_times():
    if not os.path.exists(DB_PATH):
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        m = pd.read_sql_query("SELECT DISTINCT mandante as time FROM jogos", conn)
        v = pd.read_sql_query("SELECT DISTINCT visitante as time FROM jogos", conn)
        conn.close()
        times = pd.concat([m, v]).drop_duplicates().sort_values('time')
        return times['time'].tolist()
    except Exception:
        return []


@st.cache_data(ttl=30)
def get_metricas_modelo():
    cache_path = os.path.join(BASE_DIR, 'db', 'metricas.json')
    if os.path.exists(cache_path):
        import json
        with open(cache_path, 'r') as f:
            return json.load(f)
    return None


@st.cache_data
def get_ultimos_jogos(n=20):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT campeonato, data_jogo, mandante, gols_mandante, gols_visitante, visitante "
            "FROM jogos ORDER BY data_jogo DESC LIMIT ?", conn, params=(n,)
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


st.markdown("""
<div class="main-header">
    <div>
        <h1>⚽ Futproject.V1</h1>
        <p>Dashboard de controle · Brasileirão ML Pipeline</p>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠  Visão Geral",
    "⚙️  Executar Pipeline",
    "📊  Métricas do Modelo",
    "🔮  Predição",
])

with tab1:
    stats = get_db_stats()

    if stats is None:
        st.warning("Banco de dados não encontrado. Execute o pipeline para criar o banco.")
    elif "erro" in stats:
        st.error(f"Erro ao ler banco: {stats['erro']}")
    else:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⚽ Total de Jogos</div>
                <div class="metric-value">{stats['total_jogos']:,}</div>
                <div class="metric-sub">registros no banco</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📅 Último Jogo</div>
                <div class="metric-value" style="font-size:1.3rem">{stats['ultima_data'] or 'N/A'}</div>
                <div class="metric-sub">data mais recente</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            n_temp = len(stats['temporadas'])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🗓️ Temporadas</div>
                <div class="metric-value">{n_temp}</div>
                <div class="metric-sub">campeonatos</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            modelo_status = '<span class="badge-ok">✅ Pronto</span>' if stats['tem_modelo'] else '<span class="badge-warn">⚠️ Não treinado</span>'
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🤖 Modelo ML</div>
                <div class="metric-value" style="font-size:1rem;margin-top:8px">{modelo_status}</div>
                <div class="metric-sub">{stats['dataset_rows']:,} amostras treinadas</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col_a, col_b = st.columns([1.2, 1])

        with col_a:
            st.markdown('<div class="section-title">📊 Jogos por Temporada</div>', unsafe_allow_html=True)
            df_temp = stats['temporadas']
            fig = go.Figure(go.Bar(
                x=df_temp['campeonato'],
                y=df_temp['jogos'],
                marker=dict(
                    color=df_temp['jogos'],
                    colorscale=[[0, '#0d4a6e'], [1, '#00d4ff']],
                    line=dict(color='rgba(0,212,255,0.2)', width=1)
                ),
                text=df_temp['jogos'],
                textposition='outside',
                textfont=dict(color='#e2e8f0', size=13, family='Inter')
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                height=280,
                xaxis=dict(tickfont=dict(color='#8899aa', size=11), gridcolor='#1a2332', linecolor='#2d3f55'),
                yaxis=dict(tickfont=dict(color='#8899aa', size=11), gridcolor='#1a2332', showgrid=True),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<div class="section-title">🕐 Últimos Jogos</div>', unsafe_allow_html=True)
            df_jogos = get_ultimos_jogos(8)
            if not df_jogos.empty:
                for _, row in df_jogos.iterrows():
                    placar = f"{row['gols_mandante']} × {row['gols_visitante']}"
                    st.markdown(f"""
                    <div style="background:#1a2332;border:1px solid #2d3f55;border-radius:8px;
                                padding:10px 14px;margin-bottom:6px;display:grid;
                                grid-template-columns:1fr auto 1fr;align-items:center;font-size:0.82rem;">
                        <span style="color:#c9d1d9;text-align:right;padding-right:12px">{row['mandante']}</span>
                        <span style="color:#00d4ff;font-weight:800;font-size:1rem;text-align:center;min-width:60px">{placar}</span>
                        <span style="color:#c9d1d9;text-align:left;padding-left:12px">{row['visitante']}</span>
                    </div>
                    """, unsafe_allow_html=True)


with tab2:
    st.markdown('<div class="section-title">⚙️ Controle do Pipeline</div>', unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    if 'log_msgs' not in st.session_state:
        st.session_state.log_msgs = []

    def append_log(msg):
        st.session_state.log_msgs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    with col_btn1:
        st.markdown("**🕷️ Atualizar Dados**")
        st.caption("Scraping do FBref + salvar no banco")
        if st.button("Executar Scraping", key="btn_scraping"):
            st.session_state.log_msgs = []
            append_log("Iniciando scraping...")
            with st.spinner("Extraindo dados do FBref..."):
                try:
                    from src.scraper.parser import executar_extracao
                    resultado = executar_extracao(log_fn=append_log)
                    append_log(f"✅ Concluído! {resultado['total']} jogos processados.")
                    get_db_stats.clear()
                    get_ultimos_jogos.clear()
                    st.success(f"✅ {resultado['total']} jogos salvos/verificados!")
                except Exception as e:
                    append_log(f"❌ Erro: {e}")
                    st.error(f"Erro: {e}")

    with col_btn2:
        st.markdown("**🔧 Preparar Features**")
        st.caption("Limpeza e engenharia de dados")
        if st.button("Executar Feature Engineering", key="btn_features"):
            st.session_state.log_msgs = []
            append_log("Iniciando feature engineering...")
            with st.spinner("Processando features..."):
                try:
                    from src.features.feature_engineering import preparar_dados
                    X, y = preparar_dados(log_fn=append_log)
                    st.session_state['X'] = X
                    st.session_state['y'] = y
                    append_log(f"✅ Dataset: {X.shape[0]} amostras, {X.shape[1]} features")
                    st.success(f"✅ Dataset pronto: {X.shape[0]} amostras!")
                except Exception as e:
                    append_log(f"❌ Erro: {e}")
                    st.error(f"Erro: {e}")

    with col_btn3:
        st.markdown("**🤖 Treinar Modelo**")
        st.caption("Treina o Random Forest e salva o .pkl")
        if st.button("Executar Treino", key="btn_treino"):
            st.session_state.log_msgs = []
            append_log("Iniciando treino do modelo...")
            with st.spinner("Treinando modelo..."):
                try:
                    from src.models.train import treinar_modelo
                    X = st.session_state.get('X')
                    y = st.session_state.get('y')
                    resultado = treinar_modelo(X, y, log_fn=append_log)
                    st.session_state['metricas'] = resultado

                    import json
                    metricas_json = {
                        "accuracy": resultado['accuracy'],
                        "report": resultado['report'],
                        "confusion_matrix": resultado['confusion_matrix'],
                        "target_names": resultado['target_names'],
                        "trained_at": datetime.now().isoformat(),
                    }
                    os.makedirs(os.path.join(BASE_DIR, 'db'), exist_ok=True)
                    with open(os.path.join(BASE_DIR, 'db', 'metricas.json'), 'w') as f:
                        json.dump(metricas_json, f)

                    get_metricas_modelo.clear()
                    get_db_stats.clear()
                    append_log(f"✅ Modelo treinado! Acurácia: {resultado['accuracy']*100:.2f}%")
                    st.success(f"✅ Acurácia: {resultado['accuracy']*100:.2f}%")
                except Exception as e:
                    append_log(f"❌ Erro: {e}")
                    st.error(f"Erro: {e}")

    st.markdown("---")

    st.markdown("**🚀 Pipeline Completo**")
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        skip_scraping = st.checkbox("Pular scraping (usar dados existentes)", value=False)
    with col_p2:
        run_full = st.button("▶  Executar Pipeline Completo", key="btn_full")

    if run_full:
        st.session_state.log_msgs = []
        progress = st.progress(0, text="Iniciando pipeline...")

        with st.spinner("Pipeline em execução..."):
            try:
                if not skip_scraping:
                    append_log("═══ ETAPA 1/3 — Extração de Dados ═══")
                    progress.progress(5, "Etapa 1/3 — Scraping...")
                    from src.scraper.parser import executar_extracao
                    resultado = executar_extracao(log_fn=append_log)
                    append_log(f"✅ {resultado['total']} jogos processados")
                else:
                    append_log("═══ ETAPA 1/3 — Scraping PULADO ═══")

                progress.progress(33, "Etapa 2/3 — Feature Engineering...")
                append_log("\n═══ ETAPA 2/3 — Feature Engineering ═══")
                from src.features.feature_engineering import preparar_dados
                X, y = preparar_dados(log_fn=append_log)
                st.session_state['X'] = X
                st.session_state['y'] = y

                progress.progress(66, "Etapa 3/3 — Treino do Modelo...")
                append_log("\n═══ ETAPA 3/3 — Treino do Modelo ═══")
                from src.models.train import treinar_modelo
                resultado_treino = treinar_modelo(X, y, log_fn=append_log)
                st.session_state['metricas'] = resultado_treino

                import json
                metricas_json = {
                    "accuracy": resultado_treino['accuracy'],
                    "report": resultado_treino['report'],
                    "confusion_matrix": resultado_treino['confusion_matrix'],
                    "target_names": resultado_treino['target_names'],
                    "trained_at": datetime.now().isoformat(),
                }
                os.makedirs(os.path.join(BASE_DIR, 'db'), exist_ok=True)
                with open(os.path.join(BASE_DIR, 'db', 'metricas.json'), 'w') as f:
                    json.dump(metricas_json, f)

                progress.progress(100, "✅ Pipeline concluído!")
                get_db_stats.clear()
                get_metricas_modelo.clear()
                get_ultimos_jogos.clear()
                append_log(f"\n🏆 Pipeline finalizado! Acurácia: {resultado_treino['accuracy']*100:.2f}%")
                st.success(f"🏆 Pipeline completo! Acurácia: {resultado_treino['accuracy']*100:.2f}%")

            except Exception as e:
                progress.progress(100, "❌ Erro")
                append_log(f"❌ Erro: {e}")
                st.error(f"Erro no pipeline: {e}")

    if st.session_state.log_msgs:
        st.markdown('<div class="section-title">📋 Log de Execução</div>', unsafe_allow_html=True)
        log_text = "\n".join(st.session_state.log_msgs)
        st.markdown(f'<div class="log-box">{log_text}</div>', unsafe_allow_html=True)


with tab3:
    st.markdown('<div class="section-title">📊 Métricas do Modelo Random Forest</div>', unsafe_allow_html=True)

    metricas = st.session_state.get('metricas') or get_metricas_modelo()

    if metricas is None:
        st.info("Nenhuma métrica disponível. Treine o modelo na aba **⚙️ Executar Pipeline**.")
    else:
        acc = metricas.get('accuracy', 0)
        report = metricas.get('report', {})
        cm = metricas.get('confusion_matrix', [])
        target_names = metricas.get('target_names', ['Visitante', 'Empate', 'Mandante'])
        trained_at = metricas.get('trained_at', 'Desconhecido')

        col_acc, col_info, col_spacer = st.columns([1, 1.5, 1])
        with col_acc:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center">
                <div class="metric-label">🎯 Acurácia Geral</div>
                <div class="metric-value" style="font-size:3rem;color:#00d4ff">{acc*100:.1f}%</div>
                <div class="metric-sub">no conjunto de teste (20%)</div>
            </div>
            """, unsafe_allow_html=True)
        with col_info:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🕐 Treinado em</div>
                <div class="metric-value" style="font-size:0.95rem;margin-top:8px;color:#c9d1d9">
                    {trained_at[:19].replace('T',' ') if trained_at != 'Desconhecido' else 'N/A'}
                </div>
                <br>
                <div class="metric-label">🌳 Modelo</div>
                <div class="metric-value" style="font-size:0.9rem;color:#c9d1d9">Random Forest · 200 árvores</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col_rep, col_cm = st.columns(2)

        with col_rep:
            st.markdown('<div class="section-title">📋 Relatório por Classe</div>', unsafe_allow_html=True)
            classes_data = []
            for class_name in target_names:
                if class_name in report:
                    r = report[class_name]
                    classes_data.append({
                        "Classe": class_name,
                        "Precisão": f"{r.get('precision', 0)*100:.1f}%",
                        "Recall": f"{r.get('recall', 0)*100:.1f}%",
                        "F1-Score": f"{r.get('f1-score', 0)*100:.1f}%",
                        "Suporte": int(r.get('support', 0)),
                    })
            if classes_data:
                df_rep = pd.DataFrame(classes_data)
                st.dataframe(
                    df_rep.set_index('Classe'),
                    use_container_width=True,
                    height=160,
                )

            if classes_data:
                f1_vals = [float(d['F1-Score'].replace('%', '')) for d in classes_data]
                fig_f1 = go.Figure(go.Bar(
                    x=[d['Classe'] for d in classes_data],
                    y=f1_vals,
                    marker=dict(
                        color=f1_vals,
                        colorscale=[[0, '#7c3aed'], [0.5, '#0099cc'], [1, '#00d4ff']],
                    ),
                    text=[f"{v:.1f}%" for v in f1_vals],
                    textposition='outside',
                    textfont=dict(color='#e2e8f0', size=12)
                ))
                fig_f1.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=20, b=0), height=200,
                    yaxis=dict(range=[0, 110], tickfont=dict(color='#8899aa'), gridcolor='#1a2332'),
                    xaxis=dict(tickfont=dict(color='#8899aa', size=10)),
                    title=dict(text="F1-Score por Classe", font=dict(color='#8899aa', size=12)),
                )
                st.plotly_chart(fig_f1, use_container_width=True)

        with col_cm:
            st.markdown('<div class="section-title">🔢 Matriz de Confusão</div>', unsafe_allow_html=True)
            if cm:
                cm_array = [[row[i] if i < len(row) else 0 for i in range(3)] for row in cm]
                fig_cm = go.Figure(go.Heatmap(
                    z=cm_array,
                    x=target_names,
                    y=target_names,
                    colorscale=[[0, '#0d1117'], [0.5, '#0d4a6e'], [1, '#00d4ff']],
                    text=cm_array,
                    texttemplate='<b>%{text}</b>',
                    textfont=dict(color='white', size=16),
                    showscale=False,
                ))
                fig_cm.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=20, b=0), height=320,
                    xaxis=dict(title=dict(text='Previsto', font=dict(color='#8899aa')), tickfont=dict(color='#8899aa', size=10)),
                    yaxis=dict(title=dict(text='Real', font=dict(color='#8899aa')), tickfont=dict(color='#8899aa', size=10)),
                )
                st.plotly_chart(fig_cm, use_container_width=True)


with tab4:
    st.markdown('<div class="section-title">🔮 Previsão de Partida</div>', unsafe_allow_html=True)

    times = get_times()

    if not times:
        st.warning("Nenhum time encontrado. Execute o scraping e o feature engineering primeiro.")
    elif not os.path.exists(MODELO_PATH):
        st.warning("Modelo não treinado. Execute o treino na aba **⚙️ Executar Pipeline**.")
    else:
        col_sel1, col_vs, col_sel2 = st.columns([2, 0.4, 2])

        with col_sel1:
            mandante = st.selectbox(
                "🏟️ Time Mandante",
                options=times,
                index=0,
                key="sel_mandante"
            )
        with col_vs:
            st.markdown("<div style='text-align:center;padding-top:36px;color:#8899aa;font-weight:700;font-size:1.2rem'>VS</div>", unsafe_allow_html=True)
        with col_sel2:
            default_visitante = min(1, len(times) - 1)
            visitante = st.selectbox(
                "✈️ Time Visitante",
                options=times,
                index=default_visitante,
                key="sel_visitante"
            )

        st.markdown("")
        col_pred_btn, _ = st.columns([1, 3])
        with col_pred_btn:
            prever = st.button("🔮  Prever Resultado", key="btn_prever")

        if prever:
            if mandante == visitante:
                st.error("Selecione times diferentes!")
            else:
                with st.spinner("Consultando o oráculo..."):
                    try:
                        from src.models.predict import realizar_predicao
                        resultado = realizar_predicao(mandante, visitante)

                        prob_m = resultado['prob_mandante'] * 100
                        prob_e = resultado['prob_empate'] * 100
                        prob_v = resultado['prob_visitante'] * 100

                        st.markdown(f"""
                        <div class="pred-card">
                            <div class="pred-result">{mandante}  ×  {visitante}</div>
                            <div class="pred-palpite">⭐ {resultado['palpite']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("")

                        categorias = [
                            f"⚽ {mandante}",
                            "🤝 Empate",
                            f"✈️ {visitante}",
                        ]
                        probs = [prob_m, prob_e, prob_v]
                        cores = ['#00d4ff', '#7c3aed', '#f97316']

                        fig_prob = go.Figure()
                        for cat, prob, cor in zip(categorias, probs, cores):
                            fig_prob.add_trace(go.Bar(
                                name=cat,
                                x=[cat],
                                y=[prob],
                                marker_color=cor,
                                text=[f"{prob:.1f}%"],
                                textposition='outside',
                                textfont=dict(size=16, color='white', family='Inter'),
                                width=0.5,
                            ))

                        fig_prob.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=0, r=0, t=20, b=0),
                            height=320,
                            showlegend=False,
                            yaxis=dict(
                                range=[0, 105],
                                ticksuffix='%',
                                tickfont=dict(color='#8899aa'),
                                gridcolor='#1a2332',
                            ),
                            xaxis=dict(tickfont=dict(color='#e2e8f0', size=13)),
                            bargap=0.4,
                        )

                        st.plotly_chart(fig_prob, use_container_width=True)

                        m1, m2, m3 = st.columns(3)
                        m1.metric(f"🏟️ {mandante}", f"{prob_m:.1f}%")
                        m2.metric("🤝 Empate", f"{prob_e:.1f}%")
                        m3.metric(f"✈️ {visitante}", f"{prob_v:.1f}%")

                    except (FileNotFoundError, ValueError) as e:
                        st.error(f"❌ {e}")
                    except Exception as e:
                        st.error(f"Erro inesperado: {e}")
