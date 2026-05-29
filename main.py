"""
CryptoSeeker - Punto de entrada principal.
Orquesta el flujo completo: datos → pipeline → análisis → output.

Flujo:
  1. Traer candles diarias de BTC (SMA50, SMA200 daily, Pi Cycle 111d/350d)
  2. Traer candles semanales de BTC (SMA200 weekly)
  3. Traer dominance de BTC + trend 30d desde CoinGecko
  4. Traer Fear & Greed Index desde Alternative.me
  5. Traer candles diarias de cada altcoin activa (SMA50, SMA200, RSI) + ratio vs BTC
  6. Analizar los datos con el agente (BTC + ciclo macro + altcoins)
  7. Imprimir el reporte en consola
  8. Enviar alerta Telegram si la señal BTC cambió
"""

from data.exchange_client import get_ohlcv
from data.defillama_client import get_ps_ratio
from data.fear_greed_client import get_fear_greed
from pipeline.indicators import (
    add_sma, add_rsi, add_pi_cycle,
    get_latest_indicators, get_sma200w_slope, get_ath_distance,
)
from pipeline.dominance import get_btc_dominance, get_btc_dominance_trend
from agents.analyzer import analizar_btc, analizar_dominance, analizar_altcoin, analizar_ciclo_macro
from outputs.notifier import imprimir_reporte, formatear_para_telegram
from outputs.telegram import send_alert_if_changed
from config.altcoins import ALTCOINS


def run():
    print("Iniciando CryptoSeeker...")

    # --- Paso 1: Candles diarias — SMA50, SMA200 daily + Pi Cycle (111d, 350d) ---
    # limit=400 para que la SMA_350 del Pi Cycle tenga datos suficientes
    print("Trayendo candles diarias de BTC/USDT...")
    df_daily = get_ohlcv(symbol="BTC/USDT", timeframe="1d", limit=400)
    df_daily = add_sma(df_daily, periods=[50, 200])
    df_daily = add_pi_cycle(df_daily)
    ind_daily = get_latest_indicators(df_daily)

    # --- Paso 2: Candles semanales — SMA200 weekly (~4 años de historia) ---
    print("Trayendo candles semanales de BTC/USDT...")
    df_weekly = get_ohlcv(symbol="BTC/USDT", timeframe="1w", limit=210)
    df_weekly = add_sma(df_weekly, periods=[200])
    ind_weekly = get_latest_indicators(df_weekly)

    # Slope de la SMA200 weekly: ¿está subiendo o bajando vs hace 4 semanas?
    sma200w_slope = get_sma200w_slope(df_weekly)

    # ATH distance: qué tan lejos está BTC de su máximo histórico (últimas 210 semanas)
    ath_data = get_ath_distance(df_weekly, ind_daily["precio_actual"])

    # Combinamos daily y weekly en un único dict para el agente
    indicadores_btc = {
        "precio_actual":              ind_daily["precio_actual"],
        "sma_50_daily":               ind_daily["sma_50"],
        "sma_200_daily":              ind_daily["sma_200"],
        "distancia_sma50_daily_pct":  ind_daily["distancia_sma50_pct"],
        "distancia_sma200_daily_pct": ind_daily["distancia_sma200_pct"],
        "sma_200_weekly":             ind_weekly["sma_200"],
        "distancia_sma200_weekly_pct": ind_weekly["distancia_sma200_pct"],
        "pi_sma111":                  ind_daily.get("pi_sma111"),
        "pi_2x350":                   ind_daily.get("pi_2x350"),
    }

    # --- Paso 3: Dominance desde CoinGecko + trend 30d ---
    print("Trayendo datos de dominance desde CoinGecko...")
    dominance_data    = get_btc_dominance()
    dominance_trend   = get_btc_dominance_trend()

    # --- Paso 4: Fear & Greed Index desde Alternative.me ---
    print("Trayendo Fear & Greed Index...")
    fear_greed_data = get_fear_greed()

    # Agrupamos todos los indicadores de ciclo macro para el agente
    indicadores_ciclo = {
        "fear_greed":       fear_greed_data,
        "dominance_trend":  dominance_trend,
        "sma200w_slope":    sma200w_slope,
        "ath_usd":          ath_data.get("ath_usd"),
        "ath_distancia_pct": ath_data.get("ath_distancia_pct"),
        "pi_sma111":        indicadores_btc.get("pi_sma111"),
        "pi_2x350":         indicadores_btc.get("pi_2x350"),
        "precio_actual":    ind_daily["precio_actual"],
    }

    # Precios de BTC para ratio sintético de coins sin par directo BTC
    btc_price_now    = df_daily.iloc[-1]["close"]
    btc_price_30d_ago = df_daily.iloc[-31]["close"] if len(df_daily) >= 31 else None

    # --- Paso 5: Altcoins (SMA, RSI, ratio vs BTC, P/S si aplica) ---
    analisis_altcoins = []
    for coin in ALTCOINS:
        if not coin.get("activo", True):
            continue

        print(f"Trayendo datos de {coin['nombre']} ({coin['symbol']})...")
        try:
            df_alt = get_ohlcv(symbol=coin["symbol"], timeframe="1d", limit=250, exchange=coin["exchange"])
            df_alt = add_sma(df_alt, periods=[50, 200])
            df_alt = add_rsi(df_alt, period=14)
            ind_alt = get_latest_indicators(df_alt)

            # Ratio vs BTC: cuánto BTC vale 1 unidad de la altcoin + cambio 30 días
            if coin.get("btc_symbol"):
                try:
                    df_btc_ratio = get_ohlcv(
                        symbol=coin["btc_symbol"], timeframe="1d", limit=31, exchange=coin["exchange"]
                    )
                    ratio_actual = round(df_btc_ratio.iloc[-1]["close"], 8)
                    ratio_30d_ago = df_btc_ratio.iloc[0]["close"] if len(df_btc_ratio) >= 31 else None
                    cambio_ratio = (
                        round((ratio_actual - ratio_30d_ago) / ratio_30d_ago * 100, 2)
                        if ratio_30d_ago
                        else None
                    )
                    ind_alt["ratio_btc"]           = ratio_actual
                    ind_alt["cambio_ratio_30d_pct"] = cambio_ratio
                except Exception as e:
                    print(f"  Ratio BTC no disponible para {coin['nombre']}: {e}")
            else:
                # Ratio sintético: precio_altcoin_USD ÷ precio_BTC_USD
                alt_price_now    = df_alt.iloc[-1]["close"]
                alt_price_30d_ago = df_alt.iloc[-31]["close"] if len(df_alt) >= 31 else None
                ratio_actual = round(alt_price_now / btc_price_now, 8)
                cambio_ratio = (
                    round((ratio_actual - alt_price_30d_ago / btc_price_30d_ago) / (alt_price_30d_ago / btc_price_30d_ago) * 100, 2)
                    if alt_price_30d_ago and btc_price_30d_ago
                    else None
                )
                ind_alt["ratio_btc"]            = ratio_actual
                ind_alt["cambio_ratio_30d_pct"]  = cambio_ratio

            # P/S ratio desde DeFiLlama (solo para protocolos con fees medibles)
            if coin.get("defillama_slug"):
                try:
                    ps_data = get_ps_ratio(coin["defillama_slug"])
                    ind_alt.update(ps_data)
                except Exception as e:
                    print(f"  P/S ratio no disponible para {coin['nombre']}: {e}")

            analisis = analizar_altcoin(ind_alt, coin)
            analisis_altcoins.append(analisis)

        except Exception as e:
            print(f"  Error procesando {coin['nombre']}: {e}")

    # --- Paso 6: Analizar BTC + ciclo macro ---
    print("Analizando indicadores...")
    analisis_btc   = analizar_btc(indicadores_btc)
    analisis_dom   = analizar_dominance(dominance_data)
    analisis_ciclo = analizar_ciclo_macro(indicadores_ciclo)

    # --- Paso 7: Reporte en consola ---
    imprimir_reporte(analisis_btc, analisis_dom, analisis_altcoins, analisis_ciclo)

    # --- Paso 8: Alerta Telegram (solo si la señal cambió) ---
    mensaje_telegram = formatear_para_telegram(analisis_btc, analisis_dom, analisis_altcoins, analisis_ciclo)
    send_alert_if_changed(mensaje_telegram, analisis_btc["signal_combinada"])


if __name__ == "__main__":
    run()
