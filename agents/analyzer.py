"""
Módulo de análisis e interpretación de indicadores.
Toma los números del pipeline y genera señales y conclusiones.
En el futuro se integrará un LLM (Claude) para análisis más sofisticados.
"""

# Umbrales SMA200 daily: distancia entre precio y SMA200 daily
ALERTA_ATENCION_DAILY_PCT  = 15.0   # menos del 15% sobre SMA200 daily → atención
ALERTA_CRITICO_DAILY_PCT   = 10.0   # menos del 10% sobre SMA200 daily → crítico

# Umbral SMA200 weekly: dentro del 20% sobre la SMA200 weekly = zona de acumulación macro
ZONA_ACUMULACION_WEEKLY_PCT = 20.0


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


# ── Funciones internas ────────────────────────────────────────────────────────

def _evaluar_contexto_macro(dist_sma200_weekly: float) -> str:
    """
    Evalúa el contexto macro usando la SMA200 weekly.
    Esta es la referencia histórica de largo plazo para acumulación.
    """
    if dist_sma200_weekly is None:
        return "SIN_DATOS"
    if dist_sma200_weekly < 0:
        # BTC por debajo de la SMA200 weekly: zona extrema, muy rara históricamente
        return "BAJO_SMA200_WEEKLY"
    if dist_sma200_weekly <= ZONA_ACUMULACION_WEEKLY_PCT:
        # Dentro del 20% sobre la SMA200 weekly: zona de acumulación macro
        return "ZONA_ACUMULACION"
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
            # El momentum diario empieza a recuperarse: señal fuerte
            return "ACUMULAR"
        else:
            # Zona de acumulación macro pero el precio sigue cayendo en daily
            return "ESPERAR_CONFIRMACION"

    return "FUERA_DE_ZONA"
