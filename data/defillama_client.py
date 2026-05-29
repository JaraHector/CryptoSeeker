"""
Cliente para DeFiLlama API.
Obtiene revenue y market cap de protocolos DeFi para calcular P/S ratio.
"""

import requests

_BASE = "https://api.llama.fi"


def get_ps_ratio(protocol_slug: str) -> dict:
    """
    Calcula el P/S ratio de un protocolo DeFi usando DeFiLlama.

    Revenue: fees totales de los últimos 30 días, anualizados (x12).
    Market cap: desde el endpoint de protocolo de DeFiLlama.

    Args:
        protocol_slug: Slug del protocolo en DeFiLlama (ej: "hyperliquid").

    Returns:
        Diccionario con revenue_30d, revenue_anual, mcap y ps_ratio (todos en USD).
        Campos son None si no están disponibles.
    """
    revenue_30d   = None
    revenue_anual = None
    mcap          = None

    try:
        r = requests.get(f"{_BASE}/summary/fees/{protocol_slug}", timeout=10)
        r.raise_for_status()
        data = r.json()
        revenue_30d = data.get("total30d") or (data.get("total7d", 0) * 30 / 7)
        revenue_anual = revenue_30d * 12 if revenue_30d else None
    except Exception:
        pass

    try:
        r = requests.get(f"{_BASE}/protocol/{protocol_slug}", timeout=10)
        r.raise_for_status()
        data = r.json()
        mcap = data.get("mcap")
    except Exception:
        pass

    ps_ratio = round(mcap / revenue_anual, 1) if mcap and revenue_anual else None

    return {
        "revenue_30d_usd":   round(revenue_30d)   if revenue_30d   else None,
        "revenue_anual_usd": round(revenue_anual) if revenue_anual else None,
        "mcap_usd":          round(mcap)          if mcap          else None,
        "ps_ratio":          ps_ratio,
    }
