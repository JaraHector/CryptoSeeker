"""
Análisis fundamental via Claude API (claude-haiku-4-5-20251001).
Toma noticias de CoinDesk, CoinTelegraph y Google News (RSS) e interpreta
el estado de la thesis de inversión para cada coin.
Corre UNA VEZ AL DÍA — resultado cacheado en logs/fundamental_cache.json.

thesis_status — posibles valores:
  ACUMULAR     Fundamentals refuerzan la thesis, buen momento de entrada
  HOLD         Thesis válida, sin señales de salida, mantener posición
  WATCH        Señales mixtas, monitorear de cerca antes de actuar
  TAKE_PROFIT  Fundamentals sugieren techo de ciclo o sobrevaluación
  STOP_LOSS    Thesis invalidada — hack, competidor, regulación adversa, colapso de narrativa
  SIN_DATOS    Información insuficiente para determinar
"""

import json
import os
from datetime import datetime
from anthropic import Anthropic
from data.news_client import get_news

_MODEL      = "claude-haiku-4-5-20251001"
_CACHE_FILE = "logs/fundamental_cache.json"
_MAX_TOKENS = 600
_NEWS_LIMIT = 10

# Valores válidos que Claude puede devolver en thesis_status
_THESIS_VALORES = {"ACUMULAR", "HOLD", "WATCH", "TAKE_PROFIT", "STOP_LOSS", "SIN_DATOS"}


def get_fundamental_analysis(coins: list) -> dict:
    """
    Devuelve el análisis fundamental del día para cada coin.
    Si ya corrió hoy, devuelve el caché. Si no, llama a RSS + Claude API.

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
    """
    Analiza una coin: trae noticias via RSS y las interpreta con Claude.
    Devuelve thesis_status (ver valores en el docstring del módulo).
    """
    noticias = get_news(currencies=[coin], limit=_NEWS_LIMIT)

    if not noticias:
        return _resultado_vacio(coin, "Sin noticias disponibles en las fuentes RSS.")

    noticias_texto = "\n".join([
        f"- [{n['source']}] {n['title']} ({n['published_at']})"
        for n in noticias
    ])

    prompt = f"""Analiza las siguientes noticias recientes de {coin} y determina el estado de la thesis de inversión.

Noticias:
{noticias_texto}

Responde SOLO con JSON válido (sin markdown), con esta estructura exacta:
{{
  "resumen": "2-3 líneas sobre el contexto fundamental actual",
  "thesis_status": "HOLD",
  "señales_positivas": ["señal 1", "señal 2"],
  "señales_negativas": ["señal 1", "señal 2"]
}}

Valores posibles para thesis_status (elegí UNO):
- "ACUMULAR":     fundamentals refuerzan la thesis, buen momento de entrada
- "HOLD":         thesis válida, sin señales de salida, mantener posición
- "WATCH":        señales mixtas, monitorear de cerca antes de actuar
- "TAKE_PROFIT":  fundamentals sugieren techo de ciclo o sobrevaluación
- "STOP_LOSS":    thesis invalidada — hack, competidor, colapso de narrativa, regulación adversa
- "SIN_DATOS":    información insuficiente para determinar (solo si las noticias no aportan contexto fundamental real)"""

    try:
        response = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=(
                "Eres un analista de inversiones en crypto experimentado con foco en ciclos de mercado. "
                "Tu objetivo es ayudar al inversor a decidir cuándo acumular, mantener, vigilar o salir de una posición. "
                "Respondes siempre en español, de forma concisa y directa. "
                "Devuelves solo JSON válido sin texto adicional ni bloques de código."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        contenido = response.content[0].text.strip()

        # Limpiar bloques markdown si Claude los incluyó de todas formas
        if "```" in contenido:
            partes    = contenido.split("```")
            contenido = partes[1].lstrip("json").strip() if len(partes) > 1 else contenido

        resultado = json.loads(contenido)

    except json.JSONDecodeError:
        return _resultado_vacio(coin, "Error parseando respuesta de Claude.")
    except Exception as e:
        return _resultado_vacio(coin, f"Error llamando a Claude API: {e}")

    # Validar que thesis_status sea un valor conocido
    thesis_status = resultado.get("thesis_status", "SIN_DATOS")
    if thesis_status not in _THESIS_VALORES:
        thesis_status = "SIN_DATOS"

    return {
        "coin":              coin,
        "fecha":             datetime.now().strftime("%Y-%m-%d"),
        "resumen":           resultado.get("resumen", ""),
        "thesis_status":     thesis_status,
        "señales_positivas": resultado.get("señales_positivas", []),
        "señales_negativas": resultado.get("señales_negativas", []),
        "fuentes":           [n["url"] for n in noticias[:5]],
    }


def _resultado_vacio(coin: str, motivo: str) -> dict:
    """Devuelve un resultado vacío cuando no hay noticias o falla la API."""
    return {
        "coin":              coin,
        "fecha":             datetime.now().strftime("%Y-%m-%d"),
        "resumen":           motivo,
        "thesis_status":     "SIN_DATOS",
        "señales_positivas": [],
        "señales_negativas": [],
        "fuentes":           [],
    }


def get_conclusiones_integradas(
    analisis_btc: dict,
    analisis_ciclo: dict,
    analisis_altcoins: list,
    analisis_fundamental: dict,
) -> dict:
    """
    Genera una conclusión narrativa integrando indicadores técnicos + fundamentals para cada coin.
    Se ejecuta en cada run (sin caché) porque usa los indicadores técnicos del momento.

    Args:
        analisis_btc:         Resultado de analizar_btc().
        analisis_ciclo:       Resultado de analizar_ciclo_macro().
        analisis_altcoins:    Lista de resultados de analizar_altcoin().
        analisis_fundamental: Dict {coin: resultado} de get_fundamental_analysis().

    Returns:
        Dict {coin: "conclusión narrativa en 2-3 oraciones"}.
        Vacío si no hay ANTHROPIC_API_KEY o falla la API.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {}

    client      = Anthropic(api_key=api_key)
    conclusiones = {}

    # BTC
    fund_btc = (analisis_fundamental or {}).get("BTC", {})
    conclusiones["BTC"] = _concluir_btc(client, analisis_btc, analisis_ciclo, fund_btc)

    # Altcoins activas (no silenciadas para el reporte)
    for alt in (analisis_altcoins or []):
        if not alt:
            continue
        nombre   = alt["nombre"]
        fund_alt = (analisis_fundamental or {}).get(nombre, {})
        conclusiones[nombre] = _concluir_altcoin(client, alt, analisis_btc, fund_alt)

    return conclusiones


def _concluir_btc(client: Anthropic, analisis_btc: dict, analisis_ciclo: dict, fund: dict) -> str:
    """Genera conclusión integrada para BTC cruzando técnico + macro + fundamentals."""
    signal      = analisis_btc.get("signal_combinada", "")
    contexto    = analisis_btc.get("contexto_macro", "")
    tendencia   = analisis_btc.get("tendencia_daily", "")
    cross       = analisis_btc.get("cross_event", "NINGUNO")
    dist200w    = analisis_btc.get("dist_sma200_weekly_pct")
    precio      = analisis_btc.get("precio_actual")

    fg_val      = (analisis_ciclo or {}).get("fg_valor")
    fg_clas     = (analisis_ciclo or {}).get("fg_clasificacion", "")
    ath_dist    = (analisis_ciclo or {}).get("ath_distancia_pct")
    pi_alerta   = (analisis_ciclo or {}).get("pi_alerta", False)
    slope       = (analisis_ciclo or {}).get("sma200w_slope", "")

    thesis      = fund.get("thesis_status", "SIN_DATOS")
    resumen_fund = fund.get("resumen", "")

    cross_texto = {
        "DEATH_CROSS":  "Death Cross activo (SMA50 cruzó bajo SMA200 recientemente)",
        "GOLDEN_CROSS": "Golden Cross activo (SMA50 cruzó sobre SMA200 recientemente)",
        "NINGUNO":      "Sin cruce estructural reciente",
    }.get(cross, cross)

    prompt = f"""Sos un analista de inversiones crypto con foco en ciclos de mercado. Analizá el estado actual de Bitcoin para un inversor de largo plazo.

Datos técnicos:
- Precio: ${precio:,.0f}
- Señal combinada: {signal}
- Contexto macro (SMA200w): {contexto} ({dist200w:.1f}% sobre SMA200w)
- Tendencia daily (SMA50/200): {tendencia}
- Cruce estructural: {cross_texto}
- SMA200w slope: {slope}
- Fear & Greed: {fg_val} ({fg_clas})
- Distancia al ATH: {ath_dist:.1f}%
- Pi Cycle Top: {"SEÑAL DE TOP ACTIVA ⚠️" if pi_alerta else "sin señal de top"}

Análisis fundamental:
- Thesis status: {thesis}
- Contexto de noticias: {resumen_fund or "sin datos"}

Escribí una conclusión en 2-3 oraciones en español que responda: "¿qué significa esto para mí como inversor de largo plazo ahora mismo?". Conectá el técnico con los fundamentals. Sé directo y accionable. No repitas los números — interpretá el conjunto."""

    try:
        response = client.messages.create(
            model=_MODEL,
            max_tokens=300,
            system=(
                "Sos un analista de inversiones en crypto experimentado. "
                "Respondés en español, de forma concisa y directa. "
                "Sin markdown, sin listas, solo texto plano en 2-3 oraciones."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"(Error generando conclusión: {e})"


def _concluir_altcoin(client: Anthropic, alt: dict, analisis_btc: dict, fund: dict) -> str:
    """Genera conclusión integrada para una altcoin cruzando técnico + fundamentals + contexto BTC."""
    nombre      = alt["nombre"]
    zona        = alt.get("zona_altcoin", "SIN_DATOS")
    signal      = alt.get("signal", "")
    rsi         = alt.get("rsi_14")
    zona_rsi    = alt.get("zona_rsi", "")
    cambio_ratio = alt.get("cambio_ratio_30d_pct")
    cross       = alt.get("cross_event", "NINGUNO")
    dist200     = alt.get("dist_sma200_daily_pct")
    ps_ratio    = alt.get("ps_ratio")
    ps_interp   = alt.get("ps_interpretacion", "")

    btc_signal  = analisis_btc.get("signal_combinada", "")
    btc_contexto = analisis_btc.get("contexto_macro", "")

    thesis      = fund.get("thesis_status", "SIN_DATOS")
    resumen_fund = fund.get("resumen", "")

    cross_texto = {
        "DEATH_CROSS":  "Death Cross reciente (señal bajista estructural)",
        "GOLDEN_CROSS": "Golden Cross reciente (señal alcista estructural)",
        "NINGUNO":      "sin cruce estructural reciente",
    }.get(cross, cross)

    ratio_texto = (
        f"{'gana' if cambio_ratio >= 0 else 'pierde'} {abs(cambio_ratio):.1f}% vs BTC en 30d"
        if cambio_ratio is not None else "ratio vs BTC no disponible"
    )

    ps_texto = f"P/S ratio: {ps_ratio}x ({ps_interp})" if ps_ratio else "sin P/S ratio"

    prompt = f"""Sos un analista de inversiones crypto con foco en ciclos de mercado. Analizá el estado actual de {nombre} para un inversor de largo plazo.

Datos técnicos de {nombre}:
- Zona SMA200d: {zona} ({dist200:.1f}% sobre SMA200d)
- Señal: {signal}
- RSI(14): {rsi:.1f} ({zona_rsi})
- Ratio vs BTC: {ratio_texto}
- Cruce estructural: {cross_texto}
- {ps_texto}

Contexto de mercado (BTC):
- Señal BTC: {btc_signal}
- Contexto macro BTC: {btc_contexto}

Análisis fundamental de {nombre}:
- Thesis status: {thesis}
- Contexto de noticias: {resumen_fund or "sin datos"}

Escribí una conclusión en 2-3 oraciones en español que responda: "¿vale la pena estar en {nombre} ahora mismo vs quedarme en BTC?". Conectá el técnico con los fundamentals y el contexto de mercado. Sé directo y accionable. No repitas los números — interpretá el conjunto."""

    try:
        response = client.messages.create(
            model=_MODEL,
            max_tokens=300,
            system=(
                "Sos un analista de inversiones en crypto experimentado. "
                "Respondés en español, de forma concisa y directa. "
                "Sin markdown, sin listas, solo texto plano en 2-3 oraciones."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"(Error generando conclusión: {e})"


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
