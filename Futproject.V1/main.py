from src.scraper.parser import executar_extracao
from src.features.feature_engineering import preparar_dados
from src.models.train import treinar_modelo

executar_extracao()

X, y = preparar_dados()

treinar_modelo(X, y)