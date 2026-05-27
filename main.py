"""
CryptoSeeker - Punto de entrada principal.
Orquesta el flujo completo: datos → pipeline → análisis → output.

Flujo:
  1. Traer candles diarias de BTC (SMA50 daily + SMA200 daily)
  2. Traer candles semanales de BTC (SMA200 weekly)
  3. Traer dominance de BTC desde CoinGecko
  4. Analizar los datos con el agente
  5. Imprimir el reporte en consola
"""

from data.exchange_client import get_ohlcv
from pipeline.indicators import add_sma, get_latest_indicators
from pipeline.dominance import get_btc_dominance
from agents.analyzer import analizar_btc, analizar_dominance
from outputs.notifier import imprimir_reporte, formatear_para_telegram
from outputs.telegram import send_alert_if_changed


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

    # --- Paso 4: Analizar ---
    print("Analizando indicadores...")
    analisis_btc = analizar_btc(indicadores_btc)
    analisis_dom = analizar_dominance(dominance_data)

    # --- Paso 5: Reporte en consola ---
    imprimir_reporte(analisis_btc, analisis_dom)

    # --- Paso 6: Alerta Telegram (solo si la señal cambió) ---
    mensaje_telegram = formatear_para_telegram(analisis_btc, analisis_dom)
    send_alert_if_changed(mensaje_telegram, analisis_btc["signal_combinada"])


if __name__ == "__main__":
    run()
