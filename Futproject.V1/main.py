import sys
import os
import time
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.features.feature_engineering import preparar_dados
from src.models.train import treinar_modelo
from src.models.predict import realizar_predicao


def separador(titulo: str):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")


def rodar_pipeline(skip_scraping: bool = False):
    inicio = time.time()
    print("\n⚽  Futproject.V1 — Pipeline Iniciado")
    print(f"{'─'*60}")

    if not skip_scraping:
        separador("ETAPA 1/3 — Extração de Dados (FBref)")
        from src.scraper.parser import executar_extracao
        resultado_scraping = executar_extracao()
        print(f"\n  Total processado: {resultado_scraping['total']} jogos")
    else:
        separador("ETAPA 1/3 — Extração de Dados (PULADA)")
        print("  ➡️  Usando dados já existentes no banco.")

    separador("ETAPA 2/3 — Engenharia de Features")
    X, y = preparar_dados()

    separador("ETAPA 3/3 — Treino do Modelo")
    metricas = treinar_modelo(X, y)

    duracao = time.time() - inicio
    print(f"\n{'='*60}")
    print(f"  ✅ Pipeline concluído em {duracao:.1f}s!")
    print(f"  📊 Acurácia do modelo: {metricas['accuracy'] * 100:.2f}%")
    print(f"{'='*60}\n")


def rodar_predicao():
    separador("🔮 ORÁCULO — Predição de Partida")
    try:
        mandante = input("  Mandante: ").strip()
        visitante = input("  Visitante: ").strip()
        resultado = realizar_predicao(mandante, visitante)
        print(f"\n  📊 Probabilidades:")
        print(f"     🏟️  Vitória {resultado['mandante']}: {resultado['prob_mandante'] * 100:.2f}%")
        print(f"     🤝  Empate:                    {resultado['prob_empate'] * 100:.2f}%")
        print(f"     🚀  Vitória {resultado['visitante']}: {resultado['prob_visitante'] * 100:.2f}%")
        print(f"\n  ⭐  Palpite: {resultado['palpite']}\n")
    except (FileNotFoundError, ValueError) as e:
        print(f"\n  ❌ Erro: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Futproject.V1 — Pipeline de previsão de resultados do Brasileirão"
    )
    parser.add_argument(
        '--skip-scraping', action='store_true',
        help='Pula a etapa de scraping e usa dados já existentes no banco'
    )
    parser.add_argument(
        '--predict', action='store_true',
        help='Executa apenas a predição interativa (requer modelo treinado)'
    )
    args = parser.parse_args()

    if args.predict:
        rodar_predicao()
    else:
        rodar_pipeline(skip_scraping=args.skip_scraping)


if __name__ == "__main__":
    main()