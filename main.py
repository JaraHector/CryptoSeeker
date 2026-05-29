"""
CryptoSeeker - Punto de entrada principal.
Orquesta el flujo completo: datos → pipeline → análisis → output.

Flujo:
  1. Traer candles diarias de BTC (SMA50 daily + SMA200 daily)
  2. Traer candles semanales de BTC (SMA200 weekly)
  3. Traer dominance de BTC desde CoinGecko
  4. Traer candles diarias de cada altcoin activa (SMA50, SMA200, RSI) + ratio vs BTC
  5. Analizar los datos con el agente
  6. Imprimir el reporte en consola
  7. Enviar alerta Telegram si la señal BTC cambió
"""

from data.exchange_client import get_ohlcv
from pipeline.indicators import add_sma, add_rsi, get_latest_indicators
from pipeline.dominance import get_btc_dominance
from agents.analyzer import analizar_btc, analizar_dominance, analizar_altcoin
from outputs.notifier import imprimir_reporte, formatear_para_telegram
from outputs.telegram import send_alert_if_changed
from config.altcoins import ALTCOINS


def run():
    print("Iniciando CryptoSeeker...")

    # --- Paso 1: Candles diarias — SMA50 y SMA200 daily ---
    print("Trayendo candles diarias de BTC/USDT...")
    df_daily = get_ohlcv(symbol="BTC/USDT", timeframe="1d", limit=250)
    df_daily = add_sma(df_daily, periods=[50, 200])
    ind_daily = get_latest_indicators(df_daily)

    # --- Paso 2: Candles semanales — SMA200 weekly (~4 años de historia) ---
    print("Trayendo candles semanales de BTC/USDT...")
    df_weekly = get_ohlcv(symbol="BTC/USDT", timeframe="1w", limit=210)
    df_weekly = add_sma(df_weekly, periods=[200])
    ind_weekly = get_latest_indicators(df_weekly)

    # Combinamos daily y weekly en un único dict para el agente
    indicadores_btc = {
        "precio_actual":              ind_daily["precio_actual"],
        "sma_50_daily":               ind_daily["sma_50"],
        "sma_200_daily":              ind_daily["sma_200"],
        "distancia_sma50_daily_pct":  ind_daily["distancia_sma50_pct"],
        "distancia_sma200_daily_pct": ind_daily["distancia_sma200_pct"],
        "sma_200_weekly":             ind_weekly["sma_200"],
        "distancia_sma200_weekly_pct": ind_weekly["distancia_sma200_pct"],
    }

    # --- Paso 3: Dominance desde CoinGecko ---
    print("Trayendo datos de dominance desde CoinGecko...")
    dominance_data = get_btc_dominance()

    # Precios de BTC para ratio sintético de coins sin par directo BTC
    btc_price_now    = df_daily.iloc[-1]["close"]
    btc_price_30d_ago = df_daily.iloc[-31]["close"] if len(df_daily) >= 31 else None

    # --- Paso 4: Altcoins ---
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

            analisis = analizar_altcoin(ind_alt, coin)
            analisis_altcoins.append(analisis)

        except Exception as e:
            print(f"  Error procesando {coin['nombre']}: {e}")

    # --- Paso 5: Analizar BTC ---
    print("Analizando indicadores...")
    analisis_btc = analizar_btc(indicadores_btc)
    analisis_dom = analizar_dominance(dominance_data)

    # --- Paso 6: Reporte en consola ---
    imprimir_reporte(analisis_btc, analisis_dom, analisis_altcoins)

    # --- Paso 7: Alerta Telegram (solo si la señal cambió) ---
    mensaje_telegram = formatear_para_telegram(analisis_btc, analisis_dom, analisis_altcoins)
    send_alert_if_changed(mensaje_telegram, analisis_btc["signal_combinada"])


if __name__ == "__main__":
    run()
