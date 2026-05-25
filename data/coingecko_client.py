"""
Módulo de conexión con CoinGecko.
Usa la API pública gratuita de CoinGecko para obtener datos de mercado global
que Binance no provee, como market caps totales y por categoría.
No requiere API key en el tier gratuito.
"""

import requests

# URL base de la API pública de CoinGecko
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Lista de stablecoins que excluimos al calcular la dominance ajustada
# Estas son las principales stablecoins por market cap
STABLECOINS = ["tether", "usd-coin", "dai", "first-digital-usd", "ethena-usde", "usdd"]


def get_global_market_data() -> dict:
    """
    Trae los datos globales del mercado cripto desde CoinGecko.
    Incluye: market cap total, dominance por moneda, volumen total, etc.

    Returns:
        Diccionario con los datos globales del mercado.
    """
    url = f"{COINGECKO_BASE_URL}/global"
    response = requests.get(url, timeout=10)

    # Lanzamos un error si la API devolvió un código de error HTTP
    response.raise_for_status()

    # La API devuelve los datos dentro de una clave "data"
    return response.json()["data"]


def get_coins_market_data(coin_ids: list) -> list:
    """
    Trae el market cap y precio actual de una lista de monedas específicas.
    Se usa para obtener el market cap de cada stablecoin individualmente.

    Args:
        coin_ids: Lista de IDs de CoinGecko. Ej: ['tether', 'usd-coin', 'bitcoin']

    Returns:
        Lista de diccionarios con datos de cada moneda.
    """
    url = f"{COINGECKO_BASE_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coin_ids),  # La API acepta múltiples IDs separados por coma
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def get_stablecoin_total_market_cap() -> float:
    """
    Calcula el market cap total sumando las principales stablecoins.
    Este valor se usa para calcular la dominance ajustada de BTC.

    Returns:
        Market cap total de stablecoins en USD.
    """
    coins_data = get_coins_market_data(STABLECOINS)

    # Sumamos el market cap de cada stablecoin, usando 0 si el dato no está disponible
    total = sum(coin.get("market_cap", 0) for coin in coins_data)

    return total
