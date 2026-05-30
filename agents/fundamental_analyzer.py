"""
Análisis fundamental via Claude API (claude-haiku-4-5-20251001).
Toma noticias de CryptoPanic e interpreta si la thesis de inversión sigue vigente.
Corre UNA VEZ AL DÍA — resultado cacheado en logs/fundamental_cache.json.
"""

import json
import os
from datetime import datetime
from anthropic import Anthropic
from data.news_client import get_news

_MODEL      = "claude-haiku-4-5-20251001"
_CACHE_FILE = "logs/fundamental_cache.json"
_MAX_TOKENS = 500
_NEWS_LIMIT = 10


def get_fundamental_analysis(coins: list) -> dict:
    """
    Devuelve el análisis fundamental del día para cada coin.
    Si ya corrió hoy, devuelve el caché. Si no, llama a CryptoPanic + Claude API.

    Args:
        coins: Lista de nombres de coin (ej: ["BTC", "TAO", "VVV", "HYPE"]).

    Returns:
        Dict {coin: resultado} para cada coin. Vacío si no hay API key configurada.
    """
    cached = _load_cache()
    today  = datetime.now().strftime("%Y-%m-%d")

    if cached.get("fecha") == today:
        print("Análisis fundamental: usando caché del día.")
        return cached.get("resultados", {})

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY no configurada, saltando análisis fundamental.")
        return {}

    print("Corriendo análisis fundamental (1 vez al día)...")
    client     = Anthropic(api_key=api_key)
    resultados = {}

    for coin in coins:
        print(f"  Analizando fundamentals de {coin}...")
        resultados[coin] = _analizar_coin(client, coin)

    _save_cache(today, resultados)
    return resultados


def _analizar_coin(client: Anthropic, coin: str) -> dict:
    """Analiza una coin: trae noticias de CryptoPanic y las interpreta con Claude."""
    noticias = get_news(currencies=[coin], limit=_NEWS_LIMIT)

    if not noticias:
        return _resultado_vacio(coin, "Sin noticias disponibles en CryptoPanic.")

    noticias_texto = "\n".join([
        f"- [{n['source']}] {n['title']} ({n['published_at']})"
        for n in noticias
    ])

    prompt = f"""Analiza las siguientes noticias recientes de {coin} y determina si la thesis de inversión sigue siendo válida.

Noticias:
{noticias_texto}

Responde SOLO con JSON válido (sin markdown), con esta estructura exacta:
{{
  "resumen": "2-3 líneas sobre el contexto fundamental actual",
  "thesis_valida": true,
  "señales_positivas": ["señal 1", "señal 2"],
  "señales_negativas": ["señal 1", "señal 2"]
}}

thesis_valida puede ser true, false, o null si no hay información suficiente."""

    try:
        response = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=(
                "Eres un analista de inversiones en crypto experimentado. "
                "Respondes siempre en español, de forma concisa y directa. "
                "Devuelves solo JSON válido sin texto adicional ni bloques de código."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        contenido = response.content[0].text.strip()

        # Limpiar bloques markdown si Claude los incluyó
        if "```" in contenido:
            partes    = contenido.split("```")
            contenido = partes[1].lstrip("json").strip() if len(partes) > 1 else contenido

        resultado = json.loads(contenido)

    except json.JSONDecodeError:
        return _resultado_vacio(coin, "Error parseando respuesta de Claude.")
    except Exception as e:
        return _resultado_vacio(coin, f"Error llamando a Claude API: {e}")

    return {
        "coin":              coin,
        "fecha":             datetime.now().strftime("%Y-%m-%d"),
        "resumen":           resultado.get("resumen", ""),
        "thesis_valida":     resultado.get("thesis_valida"),
        "señales_positivas": resultado.get("señales_positivas", []),
        "señales_negativas": resultado.get("señales_negativas", []),
        "fuentes":           [n["url"] for n in noticias[:5]],
    }


def _resultado_vacio(coin: str, motivo: str) -> dict:
    return {
        "coin":              coin,
        "fecha":             datetime.now().strftime("%Y-%m-%d"),
        "resumen":           motivo,
        "thesis_valida":     None,
        "señales_positivas": [],
        "señales_negativas": [],
        "fuentes":           [],
    }


def _load_cache() -> dict:
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_cache(fecha: str, resultados: dict) -> None:
    os.makedirs("logs", exist_ok=True)
    with open(_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"fecha": fecha, "resultados": resultados}, f, indent=2, ensure_ascii=False)
