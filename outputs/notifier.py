"""
Módulo de notificaciones y presentación de resultados.
Etapa 1: consola. Etapa 2 (roadmap): Telegram.
"""

from datetime import datetime


def imprimir_reporte(analisis_btc: dict, analisis_dominance: dict) -> None:
    """
    Imprime en consola el reporte completo con contexto estratégico.
    """
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep_grueso = "=" * 62
    sep_fino   = "─" * 62

    print(f"\n{sep_grueso}")
    print(f"  CRYPTOSEEKER — Reporte BTC")
    print(f"  {timestamp}")
    print(sep_grueso)

    precio = analisis_btc["precio_actual"]
    print(f"\n  💰 Precio actual: ${precio:,.2f}")

    # ── SMA200 WEEKLY ─────────────────────────────────────────────
    print(f"\n{sep_fino}")
    print("  SMA200 WEEKLY — Zona de acumulación macro (~4 años)")
    print(sep_fino)

    sma200w = analisis_btc.get("sma_200_weekly")
    dist200w = analisis_btc.get("dist_sma200_weekly_pct")
    contexto = analisis_btc["contexto_macro"]

    if sma200w:
        direccion = "sobre" if dist200w >= 0 else "bajo"
        print(f"  Valor:     ${sma200w:,.2f}")
        print(f"  Distancia: {abs(dist200w):.1f}% {direccion} la SMA200 weekly")

    etiquetas_macro = {
        "BAJO_SMA200_WEEKLY": "🔴 BAJO SMA200 WEEKLY — Zona extrema histórica. Acumular en tranches.",
        "ZONA_ACUMULACION":   "🟡 ZONA DE ACUMULACION — Precio cerca del soporte macro. Zona de interés.",
        "MERCADO_ALTO":       "🟢 MERCADO ALTO — Precio lejos de la zona de acumulación óptima.",
    }
    print(f"  Estado:    {etiquetas_macro.get(contexto, contexto)}")

    # ── SMA200 DAILY ──────────────────────────────────────────────
    print(f"\n{sep_fino}")
    print("  SMA200 DAILY — Tendencia de mediano plazo")
    print(sep_fino)

    sma200d  = analisis_btc.get("sma_200_daily")
    dist200d = analisis_btc.get("dist_sma200_daily_pct")
    nivel    = analisis_btc["nivel_alerta"]

    if sma200d:
        direccion = "sobre" if dist200d >= 0 else "bajo"
        print(f"  Valor:     ${sma200d:,.2f}")
        print(f"  Distancia: {abs(dist200d):.1f}% {direccion} la SMA200 daily")

    etiquetas_daily = {
        "NORMAL":            "🟢 NORMAL — Precio bien por encima, momentum positivo.",
        "ATENCION":          "🟡 ATENCION — BTC acercándose a la SMA200 daily.",
        "CRITICO":           "🔴 CRITICO — BTC muy cerca de la SMA200 daily.",
        "DEBAJO_SMA200_DAILY": "⛔ DEBAJO SMA200 DAILY — Momentum negativo.",
    }
    print(f"  Estado:    {etiquetas_daily.get(nivel, nivel)}")

    # ── SMA50 DAILY ───────────────────────────────────────────────
    print(f"\n{sep_fino}")
    print("  SMA50 DAILY — Tendencia de corto plazo")
    print(sep_fino)

    sma50d  = analisis_btc.get("sma_50_daily")
    dist50d = analisis_btc.get("dist_sma50_daily_pct")
    tendencia = analisis_btc["tendencia_daily"]

    if sma50d:
        direccion = "sobre" if dist50d >= 0 else "bajo"
        print(f"  Valor:     ${sma50d:,.2f}")
        print(f"  Distancia: {abs(dist50d):.1f}% {direccion} la SMA50 daily")

    etiquetas_tendencia = {
        "ALCISTA":    "🟢 ALCISTA — precio > SMA50 > SMA200.",
        "BAJISTA":    "🔴 BAJISTA — precio por debajo de SMA50 y SMA200.",
        "CORRECCION": "🟡 CORRECCION — precio entre SMA50 y SMA200.",
        "TRANSICION": "⚪ TRANSICION — señales mixtas.",
    }
    print(f"  Tendencia: {etiquetas_tendencia.get(tendencia, tendencia)}")

    # ── SEÑAL COMBINADA ───────────────────────────────────────────
    print(f"\n{sep_fino}")
    print("  🎯 SEÑAL COMBINADA")
    print(sep_fino)

    signal = analisis_btc["signal_combinada"]

    # Tabla de señales: la fila activa se marca con ►
    filas = [
        ("BAJO_SMA200_WEEKLY", "ACUMULAR",             "Bajo SMA200 weekly   ", "Cualquiera           ", "ACUMULAR          "),
        ("ZONA_ACUMULACION",   "ACUMULAR",             "Zona acumulación     ", "Recuperándose        ", "ACUMULAR          "),
        ("ZONA_ACUMULACION",   "ESPERAR_CONFIRMACION", "Zona acumulación     ", "Todavía bajando      ", "ESPERAR CONFIRM.  "),
        ("MERCADO_ALTO",       "FUERA_DE_ZONA",        "Lejos de zona        ", "Cualquiera           ", "FUERA DE ZONA     "),
    ]

    print(f"  {'SMA200 Weekly':<22} {'SMA200 Daily':<22} {'Señal':<18}")
    print(f"  {'─'*22} {'─'*22} {'─'*18}")

    for contexto_fila, signal_fila, col_weekly, col_daily, col_signal in filas:
        activo = (contexto == contexto_fila and signal == signal_fila)
        marcador = "►" if activo else " "
        print(f"{marcador} {col_weekly} {col_daily} {col_signal}")

    print()
    mensajes_signal = {
        "ACUMULAR": (
            "  ✅ ACUMULAR\n"
            "  Zona de acumulación macro activa Y momentum daily recuperándose.\n"
            "  Señal combinada favorable para empezar a comprar en tranches."
        ),
        "ESPERAR_CONFIRMACION": (
            "  ⏳ ESPERAR CONFIRMACION\n"
            "  Zona de acumulación macro activa PERO el precio sigue cayendo en daily.\n"
            "  Evitar 'atrapar el cuchillo': esperar que el precio recupere\n"
            "  la SMA200 daily antes de acumular."
        ),
        "FUERA_DE_ZONA": (
            "  📊 FUERA DE ZONA\n"
            "  Precio lejos de la SMA200 weekly. No es el momento óptimo\n"
            "  para acumular. Seguir monitoreando."
        ),
    }
    print(mensajes_signal.get(signal, signal))

    # ── CONTEXTO ESTRATÉGICO ──────────────────────────────────────
    print(f"\n{sep_fino}")
    print("  💡 CONTEXTO ESTRATEGICO")
    print(sep_fino)
    print(f"  • SMA200 weekly (${sma200w:,.0f}): soporte macro histórico de ~4 años.")
    print(f"    Cuando BTC se acerca, es la zona de acumulación de largo plazo.")
    print(f"  • SMA200 daily: indica si el momentum empezó a recuperarse")
    print(f"    o todavía está cayendo. Usala para afinar el timing de entrada.")
    print(f"  • Señal óptima: precio cerca de SMA200 weekly + recuperando SMA200 daily.")
    print(f"  • Cuidado con el 'cuchillo cayendo': si estás en zona de acumulación")
    print(f"    weekly pero aún por debajo de la SMA200 daily, esperar confirmación.")

    # ── DOMINANCE ─────────────────────────────────────────────────
    print(f"\n{sep_fino}")
    print("  🌐 BITCOIN DOMINANCE")
    print(sep_fino)
    print(f"  Estándar:           {analisis_dominance['dominance_standard_pct']}%")
    print(f"  Ajustada (ex-stable): {analisis_dominance['dominance_adjusted_pct']}%")
    print(f"  Diferencia:         +{analisis_dominance['diferencia_pct']}% (capital en stables)")
    print(f"  Interpretación:     {analisis_dominance['interpretacion']}")

    print(f"\n{sep_grueso}\n")


def formatear_para_telegram(analisis_btc: dict, analisis_dominance: dict) -> str:
    """
    Genera el texto formateado para enviar por Telegram.
    Se conecta en la Etapa 2 del proyecto.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    signal    = analisis_btc["signal_combinada"]
    precio    = analisis_btc["precio_actual"]
    sma200w   = analisis_btc.get("sma_200_weekly")
    sma200d   = analisis_btc.get("sma_200_daily")
    dist200w  = analisis_btc.get("dist_sma200_weekly_pct")
    dist200d  = analisis_btc.get("dist_sma200_daily_pct")

    emojis = {
        "ACUMULAR":             "✅",
        "ESPERAR_CONFIRMACION": "⏳",
        "FUERA_DE_ZONA":        "📊",
    }
    etiquetas = {
        "ACUMULAR":             "ACUMULAR",
        "ESPERAR_CONFIRMACION": "ESPERAR CONFIRMACION",
        "FUERA_DE_ZONA":        "FUERA DE ZONA",
    }
    emoji = emojis.get(signal, "⚪")

    dir200w = "sobre" if dist200w >= 0 else "bajo"
    dir200d = "sobre" if dist200d >= 0 else "bajo"

    mensaje = (
        f"{emoji} *CryptoSeeker — BTC Report*\n"
        f"_{timestamp}_\n\n"
        f"*Precio:* ${precio:,.2f}\n\n"
        f"*SMA200 weekly:* ${sma200w:,.2f} ({abs(dist200w):.1f}% {dir200w})\n"
        f"*SMA200 daily:*  ${sma200d:,.2f} ({abs(dist200d):.1f}% {dir200d})\n\n"
        f"*Señal:* {etiquetas.get(signal, signal)}\n\n"
        f"*Dominance ajustada:* {analisis_dominance['dominance_adjusted_pct']}%\n"
        f"_{analisis_dominance['interpretacion']}_"
    )

    return mensaje
