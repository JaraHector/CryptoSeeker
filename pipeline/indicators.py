"""
Módulo de cálculo de indicadores técnicos.
Toma un DataFrame con candles OHLCV y agrega columnas con los indicadores calculados.
"""

import pandas as pd


def add_sma(df: pd.DataFrame, periods: list = [50, 200]) -> pd.DataFrame:
    """
    Agrega columnas de SMA (Simple Moving Average) al DataFrame de velas.
    Calcula el promedio de los últimos N cierres para cada período solicitado.

    Args:
        df:      DataFrame con columna 'close' (precio de cierre).
        periods: Lista de períodos a calcular. Por defecto SMA50 y SMA200.

    Returns:
        El mismo DataFrame con columnas nuevas: 'SMA_50', 'SMA_200', etc.
    """
    for period in periods:
        # rolling(N).mean() calcula el promedio móvil de los últimos N valores
        df[f"SMA_{period}"] = df["close"].rolling(window=period).mean()

    return df


def get_sma_distance(current_price: float, sma_value: float) -> float:
    """
    Calcula qué tan lejos está el precio actual de una SMA, expresado en porcentaje.
    Un valor positivo significa que el precio está POR ENCIMA de la SMA.
    Un valor negativo significa que el precio está POR DEBAJO de la SMA.

    Ejemplo:
        precio = $107,000 | SMA200 = $85,000
        distancia = (107,000 - 85,000) / 85,000 * 100 = +25.88%

    Args:
        current_price: Precio actual del activo.
        sma_value:     Valor actual de la SMA.

    Returns:
        Distancia porcentual entre precio y SMA.
    """
    if sma_value == 0:
        return 0.0

    return ((current_price - sma_value) / sma_value) * 100


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Agrega RSI (Relative Strength Index) al DataFrame.
    Usa el suavizado exponencial de Wilder (EWM), que es el estándar del indicador.

    Valores de referencia:
      < 30  → Oversold (sobrevendido): la coin fue muy castigada, posible zona de entrada.
      30–50 → Recuperación desde oversold.
      50–70 → Momentum neutral a positivo.
      > 70  → Overbought (sobrecomprado): no acumular.

    Args:
        df:     DataFrame con columna 'close'.
        period: Período del RSI. Default 14 (estándar de la industria).

    Returns:
        El mismo DataFrame con columna nueva: 'RSI_14' (o 'RSI_{period}').
    """
    delta    = df["close"].diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    df[f"RSI_{period}"] = (100 - (100 / (1 + rs))).round(2)
    return df


def get_latest_indicators(df: pd.DataFrame) -> dict:
    """
    Extrae los valores más recientes del DataFrame ya calculado.
    Devuelve un diccionario limpio con los datos de la última vela.

    Args:
        df: DataFrame con columnas close, SMA_50, SMA_200 ya calculadas.

    Returns:
        Diccionario con precio actual, SMAs y distancias porcentuales.
    """
    # Tomamos la última fila, que corresponde a la vela más reciente
    latest = df.iloc[-1]

    price = latest["close"]
    sma50 = latest.get("SMA_50")
    sma200 = latest.get("SMA_200")

    rsi14 = latest.get("RSI_14")

    return {
        "precio_actual": round(price, 2),
        "sma_50": round(sma50, 2) if pd.notna(sma50) else None,
        "sma_200": round(sma200, 2) if pd.notna(sma200) else None,
        "distancia_sma50_pct": round(get_sma_distance(price, sma50), 2) if pd.notna(sma50) else None,
        "distancia_sma200_pct": round(get_sma_distance(price, sma200), 2) if pd.notna(sma200) else None,
        "rsi_14": round(rsi14, 2) if rsi14 is not None and pd.notna(rsi14) else None,
    }
