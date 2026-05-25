"""
Módulo de conexión con Binance.
Usa la librería ccxt para traer candles (OHLCV) de cualquier par de trading.
No requiere API key para datos públicos de mercado.
"""

import ccxt
import pandas as pd


def get_exchange():
    """
    Crea y devuelve una instancia del exchange Binance.
    La instancia se reutiliza para todas las consultas.
    """
    return ccxt.binance()


def get_ohlcv(symbol: str, timeframe: str = "1d", limit: int = 250) -> pd.DataFrame:
    """
    Trae las velas históricas (OHLCV) de un par de trading.

    Args:
        symbol:    Par a consultar. Ej: 'BTC/USDT', 'ETH/BTC'
        timeframe: Período de cada vela. Ej: '1d' (diaria), '1w' (semanal), '4h'
        limit:     Cantidad de velas a traer. 250 días = ~8 meses de historia diaria.

    Returns:
        DataFrame con columnas: fecha, open, high, low, close, volume
    """
    exchange = get_exchange()

    # Pedimos las velas al exchange
    raw_candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    # Convertimos la lista de listas en un DataFrame con nombres de columnas claros
    df = pd.DataFrame(raw_candles, columns=["fecha", "open", "high", "low", "close", "volume"])

    # El timestamp viene en milisegundos desde Unix epoch, lo convertimos a fecha legible
    df["fecha"] = pd.to_datetime(df["fecha"], unit="ms")

    # Usamos la fecha como índice del DataFrame para facilitar el análisis temporal
    df.set_index("fecha", inplace=True)

    return df
