"""
Cliente de noticias crypto via RSS — CoinDesk + CoinTelegraph + Google News (fallback).
Sin API key, sin dependencias extra (usa xml.etree.ElementTree de stdlib).

Estrategia por coin:
  1. CoinDesk RSS + CoinTelegraph RSS, filtrado por keywords
  2. Si no hay resultados → Google News RSS como fallback (búsqueda por coin)
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
]

_COIN_KEYWORDS = {
    "BTC":  ["bitcoin", "btc"],
    "ETH":  ["ethereum", "eth"],
    "TAO":  ["bittensor", "tao"],
    "VVV":  ["venice", "vvv"],
    "HYPE": ["hyperliquid", "hype"],
}

# Queries para Google News RSS — más específicos que los keywords de filtrado
_GOOGLE_QUERIES = {
    "BTC":  "bitcoin+crypto",
    "ETH":  "ethereum+crypto",
    "TAO":  "bittensor+TAO+crypto",
    "VVV":  "Venice+AI+VVV+crypto+token",
    "HYPE": "Hyperliquid+HYPE+crypto",
}

_GOOGLE_RSS_BASE = "https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
_TIMEOUT         = 10


def get_news(currencies: list, limit: int = 10) -> list:
    """
    Trae noticias recientes filtradas por coin.
    Primero intenta CoinDesk + CoinTelegraph; si no hay resultados usa Google News RSS.

    Args:
        currencies: Lista de símbolos (ej: ["BTC", "TAO"]).
        limit:      Máximo de noticias a devolver en total.

    Returns:
        Lista de dicts con title, url, source, published_at.
    """
    keywords = set()
    for coin in currencies:
        keywords.update(_COIN_KEYWORDS.get(coin.upper(), [coin.lower()]))

    # Paso 1 — fuentes especializadas
    articulos = []
    for feed_url in _FEEDS:
        articulos.extend(_fetch_feed(feed_url, keywords))

    # Paso 2 — fallback a Google News si no hay resultados
    if not articulos:
        for coin in currencies:
            query = _GOOGLE_QUERIES.get(coin.upper(), f"{coin}+crypto")
            url   = _GOOGLE_RSS_BASE.format(query=query)
            articulos.extend(_fetch_feed(url, keywords=None))  # Google ya filtra por query

    # Deduplicar por URL y ordenar por fecha descendente
    vistos = set()
    unicos = []
    for a in articulos:
        if a["url"] not in vistos:
            vistos.add(a["url"])
            unicos.append(a)

    unicos.sort(key=lambda x: x["published_at"], reverse=True)
    return unicos[:limit]


def _fetch_feed(url: str, keywords: set | None) -> list:
    """
    Descarga un feed RSS y filtra items por keywords (si se proveen).
    keywords=None omite el filtrado — útil para Google News que ya filtra por query.
    """
    try:
        response = requests.get(url, timeout=_TIMEOUT, headers={"User-Agent": "CryptoSeeker/1.0"})
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except Exception as e:
        source = url.split("/")[2]
        print(f"  Feed no disponible ({source}): {e}")
        return []

    source_name = _inferir_source(url)
    items       = root.findall(".//item")
    resultados  = []

    for item in items:
        title       = (item.findtext("title") or "").strip()
        link        = (item.findtext("link") or "").strip()
        pub_date    = (item.findtext("pubDate") or "").strip()
        description = (item.findtext("description") or "").strip()

        if keywords is not None:
            texto = (title + " " + description).lower()
            if not any(kw in texto for kw in keywords):
                continue

        resultados.append({
            "title":        title,
            "url":          link,
            "source":       source_name,
            "published_at": _parsear_fecha(pub_date),
        })

    return resultados


def _inferir_source(url: str) -> str:
    if "coindesk" in url:
        return "CoinDesk"
    if "cointelegraph" in url:
        return "CoinTelegraph"
    if "news.google" in url:
        return "Google News"
    return url.split("/")[2]


def _parsear_fecha(pub_date: str) -> str:
    """Convierte fecha RSS a formato YYYY-MM-DD. Devuelve string vacío si falla."""
    if not pub_date:
        return ""
    formatos = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(pub_date, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return pub_date[:10]
