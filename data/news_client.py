"""
Cliente de noticias crypto via RSS — CoinDesk + CoinTelegraph.
Sin API key, sin dependencias extra (usa xml.etree.ElementTree de stdlib).
Filtra artículos por keywords de cada coin antes de pasarlos al LLM.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

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

_TIMEOUT = 10


def get_news(currencies: list, limit: int = 10) -> list:
    """
    Trae noticias recientes de CoinDesk y CoinTelegraph filtradas por coin.

    Args:
        currencies: Lista de símbolos (ej: ["BTC", "TAO"]).
        limit:      Máximo de noticias a devolver en total.

    Returns:
        Lista de dicts con title, url, source, published_at.
        Devuelve lista vacía si ambos feeds fallan.
    """
    keywords = set()
    for coin in currencies:
        keywords.update(_COIN_KEYWORDS.get(coin.upper(), [coin.lower()]))

    articulos = []
    for feed_url in _FEEDS:
        articulos.extend(_fetch_feed(feed_url, keywords))

    # Deduplicar por URL y ordenar por fecha descendente
    vistos = set()
    unicos = []
    for a in articulos:
        if a["url"] not in vistos:
            vistos.add(a["url"])
            unicos.append(a)

    unicos.sort(key=lambda x: x["published_at"], reverse=True)
    return unicos[:limit]


def _fetch_feed(url: str, keywords: set) -> list:
    """Descarga un feed RSS y filtra items que contengan alguna keyword."""
    try:
        response = requests.get(url, timeout=_TIMEOUT, headers={"User-Agent": "CryptoSeeker/1.0"})
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except Exception as e:
        source = url.split("/")[2]
        print(f"  Feed no disponible ({source}): {e}")
        return []

    source_name = _inferir_source(url)
    items = root.findall(".//item")
    resultados = []

    for item in items:
        title       = (item.findtext("title") or "").strip()
        link        = (item.findtext("link") or "").strip()
        pub_date    = (item.findtext("pubDate") or "").strip()
        description = (item.findtext("description") or "").strip()

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
