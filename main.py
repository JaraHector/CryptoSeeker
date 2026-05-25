"""
CryptoSeeker - Punto de entrada principal.
Orquesta el flujo completo: datos → pipeline → análisis → output.

Flujo:
  1. Traer candles de BTC desde Binance
  2. Calcular SMA50 y SMA200
  3. Traer dominance de BTC desde CoinGecko
  4. Analizar los datos con el agente
  5. Imprimir el reporte en consola
"""

from data.binance_client import get_ohlcv
from pipeline.indicators import add_sma, get_latest_indicators
from pipeline.dominance import get_btc_dominance
from agents.analyzer import analizar_btc, analizar_dominance
from outputs.notifier import imprimir_reporte


def run():
    """
    Ejecuta el pipeline completo de análisis de BTC.
    """
    print("Iniciando CryptoSeeker...")

    # --- Paso 1: Traer datos de precio desde Binance ---
    # 250 velas diarias nos dan suficiente historia para calcular la SMA200
    print("Trayendo candles de BTC/USDT (diarias)...")
    df_btc = get_ohlcv(symbol="BTC/USDT", timeframe="1d", limit=250)

    # --- Paso 2: Calcular indicadores técnicos ---
    print("Calculando SMA50 y SMA200...")
    df_btc = add_sma(df_btc, periods=[50, 200])

    # Extraemos los valores de la última vela en un diccionario limpio
    indicadores_btc = get_latest_indicators(df_btc)

    # --- Paso 3: Traer dominance desde CoinGecko ---
    print("Trayendo datos de dominance desde CoinGecko...")
    dominance_data = get_btc_dominance()

    # --- Paso 4: Analizar con el agente ---
    print("Analizando indicadores...")
    analisis_btc = analizar_btc(indicadores_btc)
    analisis_dom = analizar_dominance(dominance_data)

    # --- Paso 5: Mostrar reporte en consola ---
    imprimir_reporte(analisis_btc, analisis_dom)


if __name__ == "__main__":
    run()
