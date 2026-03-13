# Futproject.V1 ⚽🤖

Pipeline completo de **Machine Learning** e **Web Scraping** para prever resultados de partidas do **Brasileirão** (Série A).

O projeto extrai dados históricos do [FBref](https://fbref.com/), processa features estatísticas, treina um modelo Random Forest e disponibiliza tudo em um **dashboard interativo**.

## Features ✨

- **Web Scraping Automatizado** — Extração de resultados do Brasileirão (2024–2026) via Selenium + BeautifulSoup projetado para contornar proteções Cloudflare/FBref
- **Banco SQLite** — Armazenamento local sem duplicatas (`db/database.sqlite`)
- **Feature Engineering** — Médias móveis de pontos, gols feitos/sofridos nos últimos 5 jogos
- **Random Forest Classifier** — Predição multiclasse: vitória mandante, empate ou vitória visitante
- **Pipeline Unificado** — Um único `main.py` executa scraping → features → treino
- **Dashboard Streamlit** — Interface web com visão geral, execução do pipeline, métricas e predição


## Performance e Métricas 📈

O modelo atual opera com uma **acurácia de 47,9%** em um cenário de **Classificação Multiclasse** (Vitória Mandante, Empate, Vitória Visitante). 

Para interpretar este resultado, é fundamental considerar a base estatística:
- **Baseline (Acaso):** Em um problema de 3 classes, a chance de acerto aleatório é de apenas **33,3%**.
- **Desempenho Real:** O modelo apresenta um ganho de **14,6% acima da aleatoriedade**, demonstrando que as *features* de médias móveis capturam padrões reais de consistência e momento das equipes. 
- **O Desafio do Empate:** Como em qualquer modelo preditivo esportivo, o empate é a classe de maior volatilidade. O foco do projeto é fornecer uma análise probabilística de risco, superando o simples "chute" baseado no favorito.


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
pip install -r requirements.txt
```

> **Requisito:** Google Chrome instalado (o ChromeDriver é gerenciado automaticamente).

## Uso 🚀

### Pipeline via Terminal

```bash
python main.py                  # Pipeline completo (scraping + treino)
python main.py --skip-scraping  # Pula scraping, usa dados existentes
python main.py --predict        # Predição interativa no terminal
```

### Dashboard Web

```bash
streamlit run dashboard.py
```

Abra `http://localhost:8501` no navegador. O dashboard oferece:

| Aba | Funcionalidade |
|-----|---------------|
| 🏠 Visão Geral | Total de jogos, última atualização, gráfico por temporada, últimos placares |
| ⚙️ Pipeline | Botões para executar cada etapa ou o pipeline completo com log em tempo real |
| 📊 Métricas | Acurácia, F1-Score por classe, matriz de confusão |
| 🔮 Predição | Selecionar times via dropdown e ver probabilidades com gráfico |

## Screenshots 📸

<details open>
<summary><b>Visualizar Telas do Dashboard</b></summary>

#### 🏠 Visão Geral
![Visão Geral](assets/visao_geral.png)

#### ⚙️ Executar Pipeline
![Executar Pipeline](assets/pipeline.png)

#### 📊 Métricas do Modelo
![Métricas do Modelo](assets/metricas.png)

#### 🔮 Predição
![Predição](assets/predicao.png)
</details>

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
