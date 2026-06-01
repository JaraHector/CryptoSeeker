"""
Módulo de cálculo de Bitcoin Dominance ajustada.
La dominance estándar incluye stablecoins en el total del mercado,
lo que distorsiona la lectura cuando hay mucho capital refugiado en USDT/USDC.
La dominance ajustada excluye ese capital para mostrar la dominancia real de BTC
sobre las altcoins activas.
"""

from data.coingecko_client import (
    get_global_market_data,
    get_stablecoin_total_market_cap,
    get_btc_market_cap_chart,
    get_global_market_cap_chart,
)


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
        "dominance_standard_pct":   round(btc_dominance_standard, 2),
        "dominance_adjusted_pct":   round(btc_dominance_adjusted, 2),
        "total_market_cap_usd":     total_market_cap,
        "stablecoin_market_cap_usd": stablecoin_market_cap,
        "adjusted_market_cap_usd":  adjusted_total,
    }


def get_btc_dominance_trend() -> dict:
    """
    Calcula la tendencia de la dominance estándar de BTC en los últimos 30 días.

    Compara la dominance de BTC hoy vs hace 30 días usando los histogramas de
    market cap de BTC y del mercado total disponibles en CoinGecko.

    La dirección de la dominance es clave para identificar la fase del ciclo:
      - Dominance SUBIENDO: capital fluyendo a BTC → early bull o bear (refugio)
      - Dominance BAJANDO: capital saliendo de BTC hacia alts → altcoin season (late bull)

    Returns:
        Diccionario con dominance_hoy_pct, dominance_30d_ago_pct y trend (SUBIENDO/BAJANDO/ESTABLE).
    """
    try:
        btc_chart    = get_btc_market_cap_chart(days=31)    # [[timestamp, btc_mcap], ...]
        total_chart  = get_global_market_cap_chart(days=31) # [[timestamp, total_mcap], ...]

        # El índice 0 es el dato más viejo (hace ~30 días), -1 es el más reciente
        btc_mcap_hoy     = btc_chart[-1][1]
        btc_mcap_30d     = btc_chart[0][1]
        total_mcap_hoy   = total_chart[-1][1]
        total_mcap_30d   = total_chart[0][1]

        dominance_hoy    = round(btc_mcap_hoy  / total_mcap_hoy  * 100, 2) if total_mcap_hoy  else None
        dominance_30d    = round(btc_mcap_30d  / total_mcap_30d  * 100, 2) if total_mcap_30d  else None

        if dominance_hoy is not None and dominance_30d is not None:
            diff   = round(dominance_hoy - dominance_30d, 2)
            trend  = "SUBIENDO" if diff > 0.5 else "BAJANDO" if diff < -0.5 else "ESTABLE"
        else:
            diff   = None
            trend  = "SIN_DATOS"

        return {
            "dominance_hoy_pct":   dominance_hoy,
            "dominance_30d_ago_pct": dominance_30d,
            "cambio_30d_pct":      diff,
            "trend":               trend,
        }

    except Exception as e:
        print(f"  Dominance trend no disponible: {e}")
        return {
            "dominance_hoy_pct":   None,
            "dominance_30d_ago_pct": None,
            "cambio_30d_pct":      None,
            "trend":               "SIN_DATOS",
        }
