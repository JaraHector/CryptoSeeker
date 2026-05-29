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


def add_pi_cycle(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega las dos medias móviles del Pi Cycle Top Indicator al DataFrame diario.

    El Pi Cycle Top es un indicador técnico que históricamente ha marcado los
    tops de los bull markets de Bitcoin con precisión de días:
      - Cuando la SMA_111 cruza POR ENCIMA de la 2×SMA_350 → señal de top de ciclo
      - Mientras la SMA_111 esté por debajo de 2×SMA_350 → bull market en progreso
      - La brecha entre ambas líneas indica cuán lejos estamos del techo histórico

    Requiere al menos 350 velas (usa limit=400 en get_ohlcv para tener margen).

    Args:
        df: DataFrame con columna 'close'. Debe tener 350+ filas para que SMA_350 sea válida.

    Returns:
        El mismo DataFrame con columnas nuevas: 'SMA_111', 'SMA_350', 'PI_CYCLE_2X350'.
    """
    df["SMA_111"]          = df["close"].rolling(window=111).mean()
    df["SMA_350"]          = df["close"].rolling(window=350).mean()
    df["PI_CYCLE_2X350"]   = df["SMA_350"] * 2  # La línea que nunca debe cruzar SMA_111 en bull
    return df


def get_sma200w_slope(df_weekly: pd.DataFrame, lookback_weeks: int = 4) -> str:
    """
    Determina si la SMA200 weekly está subiendo o bajando comparando el valor
    actual con el de hace N semanas.

    Una SMA200w subiendo confirma que la tendencia macro de largo plazo sigue
    siendo alcista — es una señal de salud del bull market.
    Una SMA200w bajando indica que la tendencia macro está deteriorándose.

    Args:
        df_weekly:      DataFrame semanal con columna 'SMA_200' ya calculada.
        lookback_weeks: Semanas hacia atrás para comparar (default 4 = 1 mes).

    Returns:
        "SUBIENDO", "BAJANDO" o "SIN_DATOS".
    """
    if "SMA_200" not in df_weekly.columns or len(df_weekly) < lookback_weeks + 1:
        return "SIN_DATOS"

    sma_ahora    = df_weekly["SMA_200"].iloc[-1]
    sma_anterior = df_weekly["SMA_200"].iloc[-(lookback_weeks + 1)]

    if pd.isna(sma_ahora) or pd.isna(sma_anterior):
        return "SIN_DATOS"

    return "SUBIENDO" if sma_ahora > sma_anterior else "BAJANDO"


def get_ath_distance(df_weekly: pd.DataFrame, precio_actual: float) -> dict:
    """
    Calcula la distancia del precio actual respecto al ATH histórico dentro
    del historial disponible (210 semanas ≈ 4 años, cubre ciclos 2021 y 2024).

    En un bull market sano, el ATH del ciclo anterior actúa como soporte.
    Romper por debajo del ATH previo es señal de daño estructural.

    Args:
        df_weekly:      DataFrame semanal con columna 'high'.
        precio_actual:  Precio spot actual de BTC.

    Returns:
        Diccionario con ath_usd y distancia_pct (negativa = bajo el ATH).
    """
    if "high" not in df_weekly.columns or df_weekly.empty:
        return {"ath_usd": None, "ath_distancia_pct": None}

    ath = float(df_weekly["high"].max())
    distancia_pct = round((precio_actual - ath) / ath * 100, 2)  # negativo = bajo ATH

    return {
        "ath_usd":           round(ath, 2),
        "ath_distancia_pct": distancia_pct,
    }


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

    rsi14        = latest.get("RSI_14")
    sma111       = latest.get("SMA_111")
    pi_2x350     = latest.get("PI_CYCLE_2X350")

    result = {
        "precio_actual":        round(price, 2),
        "sma_50":               round(sma50, 2)   if pd.notna(sma50)   else None,
        "sma_200":              round(sma200, 2)  if pd.notna(sma200)  else None,
        "distancia_sma50_pct":  round(get_sma_distance(price, sma50),   2) if pd.notna(sma50)  else None,
        "distancia_sma200_pct": round(get_sma_distance(price, sma200),  2) if pd.notna(sma200) else None,
        "rsi_14":               round(rsi14, 2) if rsi14 is not None and pd.notna(rsi14) else None,
    }

    # Pi Cycle: incluir solo si las columnas están presentes en el DataFrame
    if pd.notna(sma111) if sma111 is not None else False:
        result["pi_sma111"]    = round(float(sma111), 2)
    if pd.notna(pi_2x350) if pi_2x350 is not None else False:
        result["pi_2x350"]     = round(float(pi_2x350), 2)

    return result
