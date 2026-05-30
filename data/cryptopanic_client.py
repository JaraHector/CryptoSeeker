"""
Cliente para CryptoPanic API — noticias recientes por coin.
API pública gratuita. Opcionalmente usa CRYPTOPANIC_TOKEN si está en .env
para mayor rate limit. Sin token, usa el endpoint público.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

_BASE_URL = "https://cryptopanic.com/api/free/v1/posts/"


def get_news(currencies: list, limit: int = 10) -> list:
    """
    Trae noticias recientes de CryptoPanic para las coins indicadas.

    Args:
        currencies: Lista de símbolos (ej: ["BTC", "TAO"]).
        limit:      Máximo de noticias a devolver.

    Returns:
        Lista de dicts con title, url, source, published_at.
        Devuelve lista vacía si la API no está disponible.
    """
    params = {
        "public": "true",
        "currencies": ",".join(currencies),
    }

    token = os.getenv("CRYPTOPANIC_TOKEN")
    if token:
        params["auth_token"] = token

    try:
        response = requests.get(_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"  CryptoPanic no disponible: {e}")
        return []

    results = data.get("results", [])[:limit]
    return [
        {
            "title":        item.get("title", ""),
            "url":          item.get("url", ""),
            "source":       item.get("source", {}).get("title", ""),
            "published_at": item.get("published_at", "")[:10],
        }
        for item in results
    ]
