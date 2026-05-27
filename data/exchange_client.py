"""
Cliente genérico para obtener datos de mercado desde cualquier exchange soportado por ccxt.

Diseñado para ser exchange-agnostic: cada coin puede venir de su exchange natural.
  - BTC/USDT → Binance
  - TAO/USDT → Binance
  - VVV/USD  → Coinbase (VVV no cotiza en Binance spot)

Uso:
    df = get_ohlcv(symbol="BTC/USDT", timeframe="1d", limit=250, exchange="binance")
    df = get_ohlcv(symbol="VVV/USD",  timeframe="1d", limit=250, exchange="coinbase")
"""

import ccxt
import pandas as pd

# Exchanges soportados. Agregar nuevos acá si se necesitan.
EXCHANGES_DISPONIBLES = {
    "binance":  ccxt.binance,
    "coinbase": ccxt.coinbase,
    "kraken":   ccxt.kraken,
}


def get_exchange(exchange: str = "binance"):
    """
    Crea y devuelve una instancia del exchange solicitado.

    Args:
        exchange: Nombre del exchange. Opciones: 'binance', 'coinbase', 'kraken'.

    Returns:
        Instancia del exchange ccxt correspondiente.
    """
    exchange_lower = exchange.lower()

    if exchange_lower not in EXCHANGES_DISPONIBLES:
        disponibles = ", ".join(EXCHANGES_DISPONIBLES.keys())
        raise ValueError(f"Exchange '{exchange}' no soportado. Disponibles: {disponibles}")

    return EXCHANGES_DISPONIBLES[exchange_lower]()


def get_ohlcv(
    symbol: str,
    timeframe: str = "1d",
    limit: int = 250,
    exchange: str = "binance",
) -> pd.DataFrame:
    """
    Trae las velas históricas (OHLCV) de un par de trading desde el exchange indicado.

    Args:
        symbol:    Par a consultar. Ej: 'BTC/USDT', 'TAO/USDT', 'VVV/USD'
        timeframe: Período de cada vela. Ej: '1d' (diaria), '1w' (semanal), '4h'
        limit:     Cantidad de velas a traer. 250 días = ~8 meses de historia diaria.
        exchange:  Exchange a usar. Ej: 'binance', 'coinbase', 'kraken'

    Returns:
        DataFrame con columnas: fecha (index), open, high, low, close, volume
    """
    ex = get_exchange(exchange)
    raw_candles = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    df = pd.DataFrame(raw_candles, columns=["fecha", "open", "high", "low", "close", "volume"])
    df["fecha"] = pd.to_datetime(df["fecha"], unit="ms")
    df.set_index("fecha", inplace=True)

    return df
