"""
Módulo de notificaciones y presentación de resultados.
Etapa 1: consola. Etapa 2 (roadmap): Telegram.
"""

from datetime import datetime


def imprimir_reporte(
    analisis_btc: dict,
    analisis_dominance: dict,
    analisis_altcoins: list = None,
) -> None:
    """
    Imprime en consola el reporte completo con contexto estratégico.
    Las altcoins solo se muestran cuando BTC está en zona de acumulación.
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

    # ── ALTCOINS ──────────────────────────────────────────────────
    btc_en_zona = signal in ("ACUMULAR", "ESPERAR_CONFIRMACION")
    altcoins_activas = [a for a in (analisis_altcoins or []) if a]

    if altcoins_activas and btc_en_zona:
        print(f"\n{sep_fino}")
        print("  🔵 ALTCOINS — Contexto de acumulación")
        print(sep_fino)
        print("  BTC está en zona de acumulación. Ventana para evaluar altcoins.")
        print()
        print("  Indicadores clave para altcoins:")
        print("  • SMA200 daily: referencia de largo plazo. Cerca o bajo la SMA200")
        print("    = zona de acumulación potencial para esa coin.")
        print("  • SMA50 daily: si el precio ya superó la SMA50, el momentum empieza")
        print("    a recuperarse — señal de entrada más segura.")
        print("  • RSI(14): mide si la coin está sobrevendida o sobrecomprada.")
        print("    RSI < 35 = sobrevendido fuerte → señal de acumulación.")
        print("    RSI > 70 = sobrecomprado → no acumular, esperar corrección.")
        print("  • Ratio vs BTC (30d): si la altcoin pierde vs BTC, mejor quedarse")
        print("    en BTC. Solo acumular altcoins que muestren alpha positivo vs BTC.")

        for alt in altcoins_activas:
            _imprimir_altcoin(alt, sep_fino)

    elif altcoins_activas and not btc_en_zona:
        # BTC fuera de zona: mostrar altcoins brevemente sin detalle
        print(f"\n{sep_fino}")
        print("  🔵 ALTCOINS — Fuera de ventana de acumulación BTC")
        print(sep_fino)
        print("  BTC está fuera de zona óptima. Datos de altcoins disponibles")
        print("  pero no es el momento de acumular. Resumen rápido:")
        print()
        for alt in altcoins_activas:
            signal_alt = alt["signal"]
            etiqueta = {"ACUMULAR": "✅", "ESPERAR_CONFIRMACION": "⏳", "FUERA_DE_ZONA": "📊"}.get(signal_alt, "⚪")
            precio_alt = alt["precio_actual"]
            silenciado_tag = " [silenciado]" if alt.get("silenciado") else ""
            print(f"  {etiqueta} {alt['nombre']:<6} ${precio_alt:>12,.4f}  {signal_alt}{silenciado_tag}")

    print(f"\n{sep_grueso}\n")


def _imprimir_altcoin(alt: dict, sep_fino: str) -> None:
    """Imprime el bloque de análisis detallado de una altcoin."""
    nombre   = alt["nombre"]
    precio   = alt["precio_actual"]
    sma50    = alt.get("sma_50_daily")
    sma200   = alt.get("sma_200_daily")
    dist50   = alt.get("dist_sma50_daily_pct")
    dist200  = alt.get("dist_sma200_daily_pct")
    rsi      = alt.get("rsi_14")
    zona_rsi = alt.get("zona_rsi", "SIN_DATOS")
    ratio    = alt.get("ratio_btc")
    cambio   = alt.get("cambio_ratio_30d_pct")
    signal   = alt["signal"]
    silenciado = alt.get("silenciado", False)

    silenciado_tag = "  [silenciado — solo consola]" if silenciado else ""

    print(f"\n  ── {nombre} ({alt['symbol']}){silenciado_tag}")
    print(f"  Precio:       ${precio:,.4f}")

    if sma200 is not None:
        dir200 = "sobre" if dist200 >= 0 else "bajo"
        print(f"  SMA200 daily: ${sma200:,.4f}  ({abs(dist200):.1f}% {dir200})")

    if sma50 is not None:
        dir50 = "sobre" if dist50 >= 0 else "bajo"
        print(f"  SMA50 daily:  ${sma50:,.4f}  ({abs(dist50):.1f}% {dir50})")

    # RSI con interpretación
    etiquetas_rsi = {
        "OVERSOLD_EXTREMO": "🔴 < 30 — Extremadamente sobrevendido. Señal fuerte de acumulación.",
        "OVERSOLD":         "🟠 30–35 — Sobrevendido. Zona de acumulación activa.",
        "RECUPERACION":     "🟡 35–50 — Recuperándose. Momentum aún débil pero mejorando.",
        "NEUTRAL":          "🟢 50–70 — Neutral a positivo. El rebote ya comenzó.",
        "OVERBOUGHT":       "⛔ > 70 — Sobrecomprado. Esperar corrección antes de acumular.",
        "SIN_DATOS":        "— Sin datos",
    }
    if rsi is not None:
        print(f"  RSI(14):      {rsi:.1f}  {etiquetas_rsi.get(zona_rsi, zona_rsi)}")

    # Ratio vs BTC
    if ratio is not None:
        if cambio is not None:
            direccion_ratio = "▲" if cambio >= 0 else "▼"
            interpretacion_ratio = (
                "gana vs BTC — alpha positivo ✅"
                if cambio >= 0
                else "pierde vs BTC — considerar quedarse en BTC ⚠️"
            )
            print(f"  Ratio vs BTC: {ratio:.8f}  ({direccion_ratio}{abs(cambio):.1f}% en 30d — {interpretacion_ratio})")
        else:
            print(f"  Ratio vs BTC: {ratio:.8f}")
    else:
        print(f"  Ratio vs BTC: no disponible para este exchange")

    # Señal
    etiquetas_signal = {
        "ACUMULAR":             "✅ ACUMULAR — zona SMA200 + momentum recuperándose.",
        "ESPERAR_CONFIRMACION": "⏳ ESPERAR CONFIRMACION — en zona pero aún cayendo.",
        "FUERA_DE_ZONA":        "📊 FUERA DE ZONA — lejos de SMA200 daily.",
        "SIN_DATOS":            "— Sin datos suficientes.",
    }
    print(f"  Señal:        {etiquetas_signal.get(signal, signal)}")


def formatear_para_telegram(
    analisis_btc: dict,
    analisis_dominance: dict,
    analisis_altcoins: list = None,
) -> str:
    """
    Genera el texto formateado para enviar por Telegram.
    Las altcoins silenciadas no se incluyen en el mensaje.
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

    # Altcoins: incluir solo no silenciadas cuando BTC está en zona
    btc_en_zona = signal in ("ACUMULAR", "ESPERAR_CONFIRMACION")
    altcoins_visibles = [
        a for a in (analisis_altcoins or [])
        if a and not a.get("silenciado", False)
    ]

    if altcoins_visibles and btc_en_zona:
        mensaje += "\n\n*— Altcoins —*"
        for alt in altcoins_visibles:
            mensaje += _formatear_altcoin_telegram(alt)

    return mensaje


def _formatear_altcoin_telegram(alt: dict) -> str:
    """Genera el bloque Telegram para una altcoin."""
    nombre   = alt["nombre"]
    precio   = alt["precio_actual"]
    rsi      = alt.get("rsi_14")
    dist200  = alt.get("dist_sma200_daily_pct")
    ratio    = alt.get("ratio_btc")
    cambio   = alt.get("cambio_ratio_30d_pct")
    signal   = alt["signal"]

    emojis_signal = {
        "ACUMULAR":             "✅",
        "ESPERAR_CONFIRMACION": "⏳",
        "FUERA_DE_ZONA":        "📊",
    }
    emoji = emojis_signal.get(signal, "⚪")

    lineas = [f"\n\n{emoji} *{nombre}* (${precio:,.4f})"]

    if dist200 is not None:
        dir200 = "sobre" if dist200 >= 0 else "bajo"
        lineas.append(f"SMA200: {abs(dist200):.1f}% {dir200}")

    if rsi is not None:
        rsi_tag = "oversold 🔴" if rsi < 35 else ("overbought ⛔" if rsi > 70 else "neutral")
        lineas.append(f"RSI: {rsi:.0f} ({rsi_tag})")

    if ratio is not None and cambio is not None:
        dir_ratio = "▲" if cambio >= 0 else "▼"
        alpha_tag = "alpha ✅" if cambio >= 0 else "pierde vs BTC ⚠️"
        lineas.append(f"vs BTC 30d: {dir_ratio}{abs(cambio):.1f}% ({alpha_tag})")

    return "\n".join(lineas)
