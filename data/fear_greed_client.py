"""
Cliente para el Fear & Greed Index de Alternative.me.
Mide el sentimiento general del mercado crypto en una escala de 0 (miedo extremo)
a 100 (codicia extrema). Es un indicador de sentimiento contrarian:
  - Miedo extremo sostenido → posible bottom, oportunidad de acumulación
  - Codicia extrema sostenida → posible top, señal de precaución

API pública gratuita, sin API key. Devuelve hasta 30 días de historial.
"""

import requests

_URL = "https://api.alternative.me/fng/?limit=30"

# Clasificaciones del índice en español para el reporte
_CLASIFICACIONES = {
    "Extreme Fear":  "MIEDO EXTREMO",
    "Fear":          "MIEDO",
    "Neutral":       "NEUTRAL",
    "Greed":         "CODICIA",
    "Extreme Greed": "CODICIA EXTREMA",
}


def get_fear_greed() -> dict:
    """
    Obtiene el Fear & Greed Index actual y su tendencia de los últimos 7 días.

    Returns:
        Diccionario con:
          - valor (int 0-100): índice actual
          - clasificacion (str): interpretación del valor actual
          - valor_7d_ago (int): valor hace 7 días para comparar tendencia
          - trend_7d (str): SUBIENDO / BAJANDO / ESTABLE
    """
    r = requests.get(_URL, timeout=10)
    r.raise_for_status()
    data = r.json()["data"]  # lista de registros, el primero es el más reciente

    valor_actual  = int(data[0]["value"])
    clasificacion = _CLASIFICACIONES.get(data[0]["value_classification"], data[0]["value_classification"])

    # Comparamos con hace 7 días para detectar si el sentimiento está mejorando o empeorando
    valor_7d_ago = int(data[7]["value"]) if len(data) > 7 else None

    if valor_7d_ago is not None:
        diff = valor_actual - valor_7d_ago
        trend_7d = "SUBIENDO" if diff > 3 else "BAJANDO" if diff < -3 else "ESTABLE"
    else:
        trend_7d = "SIN_DATOS"

    return {
        "valor":          valor_actual,
        "clasificacion":  clasificacion,
        "valor_7d_ago":   valor_7d_ago,
        "trend_7d":       trend_7d,
    }
