# Futproject.V1 ⚽🤖

Pipeline completo de **Machine Learning** e **Web Scraping** para prever resultados de partidas do **Brasileirão** (Série A).

O projeto extrai dados históricos do [FBref](https://fbref.com/), processa features estatísticas, treina um modelo Random Forest e disponibiliza tudo em um **dashboard interativo**.

## Features ✨

- **Web Scraping Automatizado** — Extração de resultados do Brasileirão (2024–2026) via Selenium + BeautifulSoup em modo headless
- **Banco SQLite** — Armazenamento local sem duplicatas (`db/database.sqlite`)
- **Feature Engineering** — Médias móveis de pontos, gols feitos/sofridos nos últimos 5 jogos
- **Random Forest Classifier** — Predição multiclasse: vitória mandante, empate ou vitória visitante
- **Pipeline Unificado** — Um único `main.py` executa scraping → features → treino
- **Dashboard Streamlit** — Interface web com visão geral, execução do pipeline, métricas e predição

## Estrutura do Projeto 📁

```
Futproject.V1/
├── dashboard.py              # Dashboard Streamlit (4 abas)
├── main.py                   # Pipeline CLI unificado
├── requirements.txt
└── src/
    ├── features/
    │   └── feature_engineering.py
    ├── models/
    │   ├── predict.py
    │   └── train.py
    └── scraper/
        ├── driver_factory.py
        └── parser.py
```

## Setup ⚙️

```bash
git clone https://github.com/WnMoura/Futproject.V1.git
cd Futproject.V1
python -m venv .venv
source .venv/bin/activate
pip install -r Futproject.V1/requirements.txt
```

> **Requisito:** Google Chrome instalado (o ChromeDriver é gerenciado automaticamente).

## Uso 🚀

### Pipeline via Terminal

```bash
python Futproject.V1/main.py                  # Pipeline completo (scraping + treino)
python Futproject.V1/main.py --skip-scraping  # Pula scraping, usa dados existentes
python Futproject.V1/main.py --predict        # Predição interativa no terminal
```

### Dashboard Web

```bash
cd Futproject.V1
streamlit run dashboard.py
```

Abra `http://localhost:8501` no navegador. O dashboard oferece:

| Aba | Funcionalidade |
|-----|---------------|
| 🏠 Visão Geral | Total de jogos, última atualização, gráfico por temporada, últimos placares |
| ⚙️ Pipeline | Botões para executar cada etapa ou o pipeline completo com log em tempo real |
| 📊 Métricas | Acurácia, F1-Score por classe, matriz de confusão |
| 🔮 Predição | Selecionar times via dropdown e ver probabilidades com gráfico |

## Tecnologias 🛠️

| Categoria | Tecnologia |
|-----------|-----------|
| Linguagem | Python 3.12 |
| ML | Scikit-Learn, Joblib |
| Dados | Pandas, NumPy, SQLite3 |
| Scraping | Selenium, BeautifulSoup4, Undetected ChromeDriver |
| Dashboard | Streamlit, Plotly |

## Licença 📄

Projeto para fins educacionais e de pesquisa.
