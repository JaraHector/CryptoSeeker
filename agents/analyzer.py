"""
Módulo de análisis e interpretación de indicadores.
Este es el "cerebro" del proyecto: toma los números calculados por el pipeline
y los convierte en señales y conclusiones en lenguaje natural.
En el futuro, acá se integrará un LLM (ej: Claude) para análisis más sofisticados.
"""

# Umbrales de alerta para la distancia entre el precio de BTC y la SMA200
# Cuando BTC está dentro de estos rangos, se dispara una alerta
ALERTA_ZONA_ATENCION_PCT = 15.0   # BTC está a menos del 15% de la SMA200
ALERTA_ZONA_CRITICA_PCT = 10.0    # BTC está a menos del 10% de la SMA200


def analizar_btc(indicadores: dict) -> dict:
    """
    Analiza los indicadores de BTC y genera señales y conclusiones.

    Args:
        indicadores: Diccionario generado por get_latest_indicators() del pipeline.

    Returns:
        Diccionario con el análisis: señal, nivel de alerta y descripción.
    """
    precio = indicadores["precio_actual"]
    distancia_sma200 = indicadores.get("distancia_sma200_pct")
    distancia_sma50 = indicadores.get("distancia_sma50_pct")
    sma50 = indicadores.get("sma_50")
    sma200 = indicadores.get("sma_200")

    # Determinamos el nivel de alerta según la distancia a la SMA200
    nivel_alerta = _evaluar_nivel_alerta(distancia_sma200)

    # Determinamos la tendencia comparando precio vs SMAs
    tendencia = _evaluar_tendencia(precio, sma50, sma200)

    # Construimos la descripción en lenguaje natural
    descripcion = _generar_descripcion_btc(precio, sma50, sma200, distancia_sma50, distancia_sma200, tendencia, nivel_alerta)

    return {
        "activo": "BTC",
        "nivel_alerta": nivel_alerta,
        "tendencia": tendencia,
        "descripcion": descripcion,
        "requiere_atencion": nivel_alerta in ["ATENCION", "CRITICO"],
    }


def analizar_dominance(dominance_data: dict) -> dict:
    """
    Analiza los datos de dominance de BTC y genera una interpretación.

    Args:
        dominance_data: Diccionario generado por get_btc_dominance() del pipeline.

    Returns:
        Diccionario con la interpretación de la dominance.
    """
    std = dominance_data["dominance_standard_pct"]
    adj = dominance_data["dominance_adjusted_pct"]

    # La diferencia entre ambas dominances indica cuánto capital hay en stablecoins
    diferencia = round(adj - std, 2)

    # Interpretamos qué significa el nivel actual de dominance ajustada
    if adj > 60:
        interpretacion = "BTC domina fuertemente el mercado. Altcoins en general débiles."
    elif adj > 55:
        interpretacion = "BTC con dominance alta. Mercado favorable para BTC sobre altcoins."
    elif adj > 50:
        interpretacion = "BTC con leve ventaja sobre altcoins. Mercado en equilibrio."
    else:
        interpretacion = "Altcoins ganando terreno vs BTC. Posible temporada de altcoins."

    return {
        "dominance_standard_pct": std,
        "dominance_adjusted_pct": adj,
        "diferencia_pct": diferencia,
        "interpretacion": interpretacion,
    }


def _evaluar_nivel_alerta(distancia_sma200: float) -> str:
    """
    Determina el nivel de alerta según la distancia porcentual a la SMA200.
    Solo aplica cuando BTC está POR ENCIMA de la SMA200 (distancia positiva).
    """
    if distancia_sma200 is None:
        return "SIN_DATOS"

    if distancia_sma200 < 0:
        # BTC está por debajo de la SMA200, zona de peligro/oportunidad según contexto
        return "DEBAJO_SMA200"

    if distancia_sma200 <= ALERTA_ZONA_CRITICA_PCT:
        return "CRITICO"      # Dentro del 10%: muy cerca de la SMA200

    if distancia_sma200 <= ALERTA_ZONA_ATENCION_PCT:
        return "ATENCION"     # Entre 10% y 15%: zona de atención

    return "NORMAL"           # Más del 15% sobre la SMA200


def _evaluar_tendencia(precio: float, sma50: float, sma200: float) -> str:
    """
    Determina la tendencia del precio comparando su posición relativa a las SMAs.
    """
    if sma50 is None or sma200 is None:
        return "SIN_DATOS"

    precio_sobre_sma200 = precio > sma200
    precio_sobre_sma50 = precio > sma50
    sma50_sobre_sma200 = sma50 > sma200

    if precio_sobre_sma50 and precio_sobre_sma200 and sma50_sobre_sma200:
        return "ALCISTA"          # Precio > SMA50 > SMA200: tendencia alcista fuerte

    if not precio_sobre_sma50 and not precio_sobre_sma200:
        return "BAJISTA"          # Precio < SMA50 y SMA200: tendencia bajista

    if precio_sobre_sma200 and not precio_sobre_sma50:
        return "CORRECCION"       # Precio entre SMA50 y SMA200: corrección en tendencia alcista

    return "TRANSICION"           # Cualquier otro caso: mercado en transición


def _generar_descripcion_btc(precio, sma50, sma200, dist50, dist200, tendencia, nivel_alerta) -> str:
    """
    Genera un texto descriptivo en lenguaje natural con el estado actual de BTC.
    """
    lineas = []

    lineas.append(f"Precio actual: ${precio:,.2f}")

    if sma50:
        direccion50 = "sobre" if dist50 > 0 else "bajo"
        lineas.append(f"SMA50: ${sma50:,.2f} ({abs(dist50):.1f}% {direccion50} la SMA)")

    if sma200:
        direccion200 = "sobre" if dist200 > 0 else "bajo"
        lineas.append(f"SMA200: ${sma200:,.2f} ({abs(dist200):.1f}% {direccion200} la SMA)")

    # Mensaje según la tendencia detectada
    mensajes_tendencia = {
        "ALCISTA": "Tendencia alcista: precio por encima de ambas medias móviles.",
        "BAJISTA": "Tendencia bajista: precio por debajo de ambas medias móviles.",
        "CORRECCION": "En corrección: precio entre SMA50 y SMA200.",
        "TRANSICION": "Mercado en transición, señales mixtas.",
    }
    if tendencia in mensajes_tendencia:
        lineas.append(mensajes_tendencia[tendencia])

    # Mensaje de alerta si corresponde
    if nivel_alerta == "CRITICO":
        lineas.append(f"⚠️  ALERTA CRITICA: BTC a menos del {ALERTA_ZONA_CRITICA_PCT}% de la SMA200.")
    elif nivel_alerta == "ATENCION":
        lineas.append(f"⚡ ATENCION: BTC acercandose a la SMA200 (zona de interes historico).")
    elif nivel_alerta == "DEBAJO_SMA200":
        lineas.append("🔴 BTC por debajo de la SMA200. Zona de alta volatilidad.")

    return " | ".join(lineas)
