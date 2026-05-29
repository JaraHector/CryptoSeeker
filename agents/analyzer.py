"""
Módulo de análisis e interpretación de indicadores.
Toma los números del pipeline y genera señales y conclusiones.
En el futuro se integrará un LLM (Claude) para análisis más sofisticados.
"""

# Umbrales SMA200 daily: distancia entre precio y SMA200 daily
ALERTA_ATENCION_DAILY_PCT  = 15.0   # menos del 15% sobre SMA200 daily → atención
ALERTA_CRITICO_DAILY_PCT   = 10.0   # menos del 10% sobre SMA200 daily → crítico

# Umbrales SMA200 weekly para definir la zona de acumulación macro
# ZONA_VIGILANCIA: dentro del 20% — empezar a prestar atención, zona se acerca
# ZONA_ACUMULACION: dentro del 15% — zona real de compra en tranches
# Referencia: con SMA200w ≈ $61k, el 15% corresponde a ~$70k
ZONA_VIGILANCIA_WEEKLY_PCT  = 20.0
ZONA_ACUMULACION_WEEKLY_PCT = 15.0

# Umbrales para altcoins (sin contexto weekly)
ALTCOIN_ZONA_ACUMULACION_PCT = 20.0  # dentro del 20% sobre SMA200 daily = zona de interés
ALTCOIN_RSI_OVERSOLD         = 35.0  # RSI < 35 = sobrevendido, señal de acumulación fuerte
ALTCOIN_RSI_NEUTRO           = 50.0  # RSI < 50 = momentum aún débil


def analizar_btc(indicadores: dict) -> dict:
    """
    Analiza los indicadores de BTC (daily + weekly) y genera señales combinadas.

    Args:
        indicadores: Diccionario con precio, SMAs daily y SMA200 weekly.

    Returns:
        Diccionario con análisis completo: contexto macro, tendencia, señal combinada.
    """
    precio           = indicadores["precio_actual"]
    sma50_daily      = indicadores.get("sma_50_daily")
    sma200_daily     = indicadores.get("sma_200_daily")
    sma200_weekly    = indicadores.get("sma_200_weekly")
    dist_sma50_daily  = indicadores.get("distancia_sma50_daily_pct")
    dist_sma200_daily = indicadores.get("distancia_sma200_daily_pct")
    dist_sma200_weekly = indicadores.get("distancia_sma200_weekly_pct")

    contexto_macro   = _evaluar_contexto_macro(dist_sma200_weekly)
    tendencia_daily  = _evaluar_tendencia_daily(precio, sma50_daily, sma200_daily)
    nivel_alerta     = _evaluar_nivel_alerta_daily(dist_sma200_daily)
    signal_combinada = _evaluar_signal_combinada(contexto_macro, tendencia_daily)

    return {
        "activo":               "BTC",
        "precio_actual":        precio,
        "sma_50_daily":         sma50_daily,
        "sma_200_daily":        sma200_daily,
        "sma_200_weekly":       sma200_weekly,
        "dist_sma50_daily_pct":  dist_sma50_daily,
        "dist_sma200_daily_pct": dist_sma200_daily,
        "dist_sma200_weekly_pct": dist_sma200_weekly,
        "contexto_macro":       contexto_macro,
        "tendencia_daily":      tendencia_daily,
        "nivel_alerta":         nivel_alerta,
        "signal_combinada":     signal_combinada,
        "requiere_atencion":    contexto_macro in ["ZONA_ACUMULACION", "BAJO_SMA200_WEEKLY"],
    }


def analizar_dominance(dominance_data: dict) -> dict:
    """
    Analiza los datos de dominance de BTC y genera una interpretación.
    """
    std = dominance_data["dominance_standard_pct"]
    adj = dominance_data["dominance_adjusted_pct"]
    diferencia = round(adj - std, 2)

    if adj > 60:
        interpretacion = "BTC domina fuertemente el mercado. Altcoins en general débiles."
    elif adj > 55:
        interpretacion = "BTC con dominance alta. Mercado favorable para BTC sobre altcoins."
    elif adj > 50:
        interpretacion = "BTC con leve ventaja sobre altcoins. Mercado en equilibrio."
    else:
        interpretacion = "Altcoins ganando terreno vs BTC. Posible temporada de altcoins."

    # Nota sobre altcoins: relevante cuando se agreguen TAO y Venice
    altcoins_favorable = adj > 55

    return {
        "dominance_standard_pct":  std,
        "dominance_adjusted_pct":  adj,
        "diferencia_pct":          diferencia,
        "interpretacion":          interpretacion,
        "altcoins_favorable":      altcoins_favorable,
    }


def analizar_altcoin(indicadores: dict, config: dict) -> dict:
    """
    Analiza una altcoin usando SMA200 daily, SMA50 daily, RSI(14) y ratio vs BTC.
    La señal es independiente de BTC — cada coin habla por sí misma.
    La decisión de mostrarla depende del contexto macro de BTC (ver notifier.py).

    Args:
        indicadores: Diccionario con precio, SMAs, RSI y opcionalmente ratio_btc.
        config:      Entrada de ALTCOINS en config/altcoins.py.

    Returns:
        Diccionario con análisis completo de la altcoin.
    """
    precio       = indicadores["precio_actual"]
    sma50        = indicadores.get("sma_50")
    sma200       = indicadores.get("sma_200")
    dist_sma200  = indicadores.get("distancia_sma200_pct")
    dist_sma50   = indicadores.get("distancia_sma50_pct")
    rsi          = indicadores.get("rsi_14")
    ratio_btc    = indicadores.get("ratio_btc")
    cambio_ratio = indicadores.get("cambio_ratio_30d_pct")

    signal       = _evaluar_signal_altcoin(precio, sma50, sma200, dist_sma200, rsi)
    zona_rsi     = _evaluar_zona_rsi(rsi)

    ps_ratio          = indicadores.get("ps_ratio")
    revenue_anual_usd = indicadores.get("revenue_anual_usd")
    mcap_usd          = indicadores.get("mcap_usd")
    ps_interpretacion = _interpretar_ps_ratio(ps_ratio)

    return {
        "nombre":              config["nombre"],
        "symbol":              config["symbol"],
        "silenciado":          config.get("silenciado", False),
        "precio_actual":       precio,
        "sma_50_daily":        sma50,
        "sma_200_daily":       sma200,
        "dist_sma50_daily_pct":  dist_sma50,
        "dist_sma200_daily_pct": dist_sma200,
        "rsi_14":              rsi,
        "zona_rsi":            zona_rsi,
        "ratio_btc":           ratio_btc,
        "cambio_ratio_30d_pct": cambio_ratio,
        "ps_ratio":            ps_ratio,
        "revenue_anual_usd":   revenue_anual_usd,
        "mcap_usd":            mcap_usd,
        "ps_interpretacion":   ps_interpretacion,
        "signal":              signal,
    }


def analizar_ciclo_macro(indicadores: dict) -> dict:
    """
    Analiza los indicadores de ciclo macro del mercado crypto.
    Estos indicadores ayudan a identificar en qué fase del ciclo estamos
    (bull market, bear market, transición) más allá del precio puntual.

    Args:
        indicadores: Dict con fear_greed, dominance_trend, sma200w_slope,
                     ath_usd, ath_distancia_pct, pi_sma111, pi_2x350, precio_actual.

    Returns:
        Diccionario con análisis completo de ciclo macro.
    """
    fear_greed      = indicadores.get("fear_greed", {})
    dominance_trend = indicadores.get("dominance_trend", {})
    sma200w_slope   = indicadores.get("sma200w_slope", "SIN_DATOS")
    ath_usd         = indicadores.get("ath_usd")
    ath_dist        = indicadores.get("ath_distancia_pct")
    pi_sma111       = indicadores.get("pi_sma111")
    pi_2x350        = indicadores.get("pi_2x350")

    # Pi Cycle: estado y brecha entre las dos líneas
    pi_estado, pi_gap_pct, pi_alerta = _evaluar_pi_cycle(pi_sma111, pi_2x350)

    return {
        # Fear & Greed
        "fg_valor":          fear_greed.get("valor"),
        "fg_clasificacion":  fear_greed.get("clasificacion"),
        "fg_trend_7d":       fear_greed.get("trend_7d"),
        "fg_valor_7d_ago":   fear_greed.get("valor_7d_ago"),
        # Dominance trend
        "dom_trend":         dominance_trend.get("trend"),
        "dom_cambio_30d":    dominance_trend.get("cambio_30d_pct"),
        "dom_hoy_pct":       dominance_trend.get("dominance_hoy_pct"),
        "dom_30d_ago_pct":   dominance_trend.get("dominance_30d_ago_pct"),
        # SMA200w slope
        "sma200w_slope":     sma200w_slope,
        # ATH distance
        "ath_usd":           ath_usd,
        "ath_distancia_pct": ath_dist,
        # Pi Cycle Top
        "pi_sma111":         pi_sma111,
        "pi_2x350":          pi_2x350,
        "pi_estado":         pi_estado,
        "pi_gap_pct":        pi_gap_pct,
        "pi_alerta":         pi_alerta,
    }


# ── Funciones internas ────────────────────────────────────────────────────────

def _evaluar_contexto_macro(dist_sma200_weekly: float) -> str:
    """
    Evalúa el contexto macro usando la SMA200 weekly con dos niveles de alerta:

    - BAJO_SMA200_WEEKLY: precio bajo la SMA200w — zona extrema, muy rara históricamente
    - ZONA_ACUMULACION:   dentro del 15% sobre SMA200w — zona real de compra en tranches
    - ZONA_VIGILANCIA:    entre 15% y 20% sobre SMA200w — empezar a prestar atención
    - MERCADO_ALTO:       más del 20% sobre SMA200w — no es momento óptimo de acumulación
    """
    if dist_sma200_weekly is None:
        return "SIN_DATOS"
    if dist_sma200_weekly < 0:
        return "BAJO_SMA200_WEEKLY"
    if dist_sma200_weekly <= ZONA_ACUMULACION_WEEKLY_PCT:
        return "ZONA_ACUMULACION"
    if dist_sma200_weekly <= ZONA_VIGILANCIA_WEEKLY_PCT:
        return "ZONA_VIGILANCIA"
    return "MERCADO_ALTO"


def _evaluar_nivel_alerta_daily(dist_sma200_daily: float) -> str:
    """
    Evalúa el nivel de alerta según la distancia a la SMA200 daily.
    """
    if dist_sma200_daily is None:
        return "SIN_DATOS"
    if dist_sma200_daily < 0:
        return "DEBAJO_SMA200_DAILY"
    if dist_sma200_daily <= ALERTA_CRITICO_DAILY_PCT:
        return "CRITICO"
    if dist_sma200_daily <= ALERTA_ATENCION_DAILY_PCT:
        return "ATENCION"
    return "NORMAL"


def _evaluar_tendencia_daily(precio: float, sma50: float, sma200: float) -> str:
    """
    Determina la tendencia comparando precio vs SMA50 y SMA200 daily.
    """
    if sma50 is None or sma200 is None:
        return "SIN_DATOS"

    sobre_sma200 = precio > sma200
    sobre_sma50  = precio > sma50
    sma50_sobre_sma200 = sma50 > sma200

    if sobre_sma50 and sobre_sma200 and sma50_sobre_sma200:
        return "ALCISTA"       # precio > SMA50 > SMA200: tendencia alcista fuerte
    if not sobre_sma50 and not sobre_sma200:
        return "BAJISTA"       # precio < SMA50 y SMA200: tendencia bajista
    if sobre_sma200 and not sobre_sma50:
        return "CORRECCION"    # precio entre SMA50 y SMA200: corrección en tendencia alcista
    return "TRANSICION"


def _evaluar_signal_altcoin(
    precio: float, sma50: float, sma200: float, dist_sma200: float, rsi: float
) -> str:
    """
    Señal de acumulación para altcoins. Sin contexto weekly — solo daily + RSI.

    Lógica:
    - ACUMULAR:             precio dentro del 20% de la SMA200 daily Y recuperando momentum
    - ESPERAR_CONFIRMACION: en zona de acumulación pero precio aún cayendo (RSI débil)
    - FUERA_DE_ZONA:        precio muy por encima de la SMA200 daily, no zona óptima
    """
    if dist_sma200 is None:
        return "SIN_DATOS"

    en_zona = dist_sma200 <= ALTCOIN_ZONA_ACUMULACION_PCT

    if not en_zona:
        return "FUERA_DE_ZONA"

    # En zona de acumulación: el RSI y la relación precio/SMA50 definen si acumular ya
    rsi_recuperando  = rsi is not None and rsi < ALTCOIN_RSI_NEUTRO
    precio_sobre_sma50 = (precio > sma50) if sma50 else False

    if rsi is not None and rsi < ALTCOIN_RSI_OVERSOLD:
        # Extremadamente sobrevendido: acumular independiente del SMA50
        return "ACUMULAR"

    if precio_sobre_sma50 or rsi_recuperando:
        return "ACUMULAR"

    return "ESPERAR_CONFIRMACION"


def _evaluar_zona_rsi(rsi: float) -> str:
    """Clasifica el valor RSI en una zona interpretable."""
    if rsi is None:
        return "SIN_DATOS"
    if rsi < 30:
        return "OVERSOLD_EXTREMO"
    if rsi < ALTCOIN_RSI_OVERSOLD:
        return "OVERSOLD"
    if rsi < ALTCOIN_RSI_NEUTRO:
        return "RECUPERACION"
    if rsi < 70:
        return "NEUTRAL"
    return "OVERBOUGHT"


def _evaluar_pi_cycle(sma111: float, pi_2x350: float) -> tuple:
    """
    Evalúa el estado del Pi Cycle Top Indicator.

    Lógica:
    - Mientras SMA_111 < 2×SMA_350 → bull market en progreso, no hay señal de top
    - Cuando SMA_111 cruza POR ENCIMA de 2×SMA_350 → señal histórica de top de ciclo
    - La brecha (gap) indica cuán lejos estamos de ese cruce

    Returns:
        Tuple (estado, gap_pct, alerta):
          - estado:   "BULL_EN_PROGRESO" / "SEÑAL_TOP" / "SIN_DATOS"
          - gap_pct:  distancia porcentual entre SMA_111 y 2×SMA_350 (negativo = bull sano)
          - alerta:   True si SMA_111 ≥ 2×SMA_350 (señal de top activa)
    """
    if sma111 is None or pi_2x350 is None:
        return ("SIN_DATOS", None, False)

    gap_pct = round((sma111 - pi_2x350) / pi_2x350 * 100, 2)
    alerta  = sma111 >= pi_2x350

    estado  = "SEÑAL_TOP" if alerta else "BULL_EN_PROGRESO"
    return (estado, gap_pct, alerta)


def _interpretar_ps_ratio(ps_ratio: float) -> str:
    """
    Interpreta el P/S ratio de un protocolo DeFi tipo exchange.
    Referencia TradFi: Robinhood ~4-8x, CME ~15-20x.
    """
    if ps_ratio is None:
        return "SIN_DATOS"
    if ps_ratio < 10:
        return "BARATO"       # por debajo de exchanges TradFi establecidos
    if ps_ratio < 25:
        return "RAZONABLE"    # rango fair value para exchange en crecimiento
    if ps_ratio < 50:
        return "CARO"         # pricing in crecimiento significativo
    return "MUY_CARO"         # premium especulativo elevado


def _evaluar_signal_combinada(contexto_macro: str, tendencia_daily: str) -> str:
    """
    Genera la señal combinada cruzando el contexto macro (weekly) con la tendencia daily.

    Lógica:
    - ACUMULAR:             zona de acumulación weekly + momentum daily recuperándose
    - ESPERAR_CONFIRMACION: zona de acumulación weekly pero momentum daily aún negativo
                            (evitar "atrapar el cuchillo")
    - FUERA_DE_ZONA:        precio lejos de la SMA200 weekly, no es zona óptima
    """
    if contexto_macro == "BAJO_SMA200_WEEKLY":
        # Zona extrema histórica: acumular en tranches sin importar el daily
        return "ACUMULAR"

    if contexto_macro == "ZONA_ACUMULACION":
        if tendencia_daily in ["ALCISTA", "CORRECCION"]:
            return "ACUMULAR"
        else:
            # En zona real pero el precio sigue cayendo: esperar confirmación diaria
            return "ESPERAR_CONFIRMACION"

    if contexto_macro == "ZONA_VIGILANCIA":
        # Zona de atención: cerca pero aún no es la zona óptima de compra
        return "ESPERAR_CONFIRMACION"

    return "FUERA_DE_ZONA"
