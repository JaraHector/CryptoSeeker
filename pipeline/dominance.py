"""
Módulo de cálculo de Bitcoin Dominance ajustada.
La dominance estándar incluye stablecoins en el total del mercado,
lo que distorsiona la lectura cuando hay mucho capital refugiado en USDT/USDC.
La dominance ajustada excluye ese capital para mostrar la dominancia real de BTC
sobre las altcoins activas.
"""

from data.coingecko_client import get_global_market_data, get_stablecoin_total_market_cap


def get_btc_dominance() -> dict:
    """
    Calcula tanto la dominance estándar como la ajustada (sin stablecoins) de BTC.

    Fórmula estándar:   BTC mcap / Total mcap * 100
    Fórmula ajustada:   BTC mcap / (Total mcap - Stablecoin mcap) * 100

    Returns:
        Diccionario con ambos valores de dominance y los market caps usados.
    """
    # Traemos los datos globales del mercado desde CoinGecko
    global_data = get_global_market_data()

    # Market cap total de todo el mercado cripto en USD
    total_market_cap = global_data["total_market_cap"]["usd"]

    # Market cap de BTC en USD
    btc_market_cap = global_data["total_market_cap"].get("btc")

    # CoinGecko nos da la dominance estándar directamente
    btc_dominance_standard = global_data["market_cap_percentage"].get("btc", 0)

    # Para la ajustada, necesitamos el market cap de las stablecoins por separado
    stablecoin_market_cap = get_stablecoin_total_market_cap()

    # Calculamos el total del mercado excluyendo stablecoins
    adjusted_total = total_market_cap - stablecoin_market_cap

    # Calculamos la dominance ajustada usando el market cap real de BTC
    btc_market_cap_usd = total_market_cap * (btc_dominance_standard / 100)
    btc_dominance_adjusted = (btc_market_cap_usd / adjusted_total) * 100 if adjusted_total > 0 else 0

    return {
        "dominance_standard_pct": round(btc_dominance_standard, 2),
        "dominance_adjusted_pct": round(btc_dominance_adjusted, 2),
        "total_market_cap_usd": total_market_cap,
        "stablecoin_market_cap_usd": stablecoin_market_cap,
        "adjusted_market_cap_usd": adjusted_total,
    }
