"""
Módulo de notificaciones y presentación de resultados.
Etapa 1: consola. Etapa 2 (roadmap): Telegram.
"""

from datetime import datetime


def imprimir_reporte(
    analisis_btc: dict,
    analisis_dominance: dict,
    analisis_altcoins: list = None,
    analisis_ciclo: dict = None,
    analisis_fundamental: dict = None,
    conclusiones: dict = None,
) -> None:
    """
    Imprime en consola el reporte completo con contexto estratégico.
    Orden: BTC técnico → Ciclo Macro → Fundamentals BTC → Conclusión BTC → Dominance → Altcoins.
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
        "ZONA_ACUMULACION":   "🟠 ZONA DE ACUMULACION — Dentro del 15%. Zona real de compra.",
        "ZONA_VIGILANCIA":    "🟡 ZONA DE VIGILANCIA — Entre 15-20%. Empezar a prestar atención.",
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

    cross_event = analisis_btc.get("cross_event", "NINGUNO")
    if cross_event == "DEATH_CROSS":
        print("  ⚠️  DEATH CROSS RECIENTE — SMA50 cruzó por debajo de SMA200 (señal bajista estructural).")
    elif cross_event == "GOLDEN_CROSS":
        print("  ✨ GOLDEN CROSS RECIENTE — SMA50 cruzó por encima de SMA200 (señal alcista estructural).")

    # ── SEÑAL COMBINADA ───────────────────────────────────────────
    print(f"\n{sep_fino}")
    print("  🎯 SEÑAL COMBINADA")
    print(sep_fino)

    signal = analisis_btc["signal_combinada"]

    # Tabla de señales: la fila activa se marca con ►
    filas = [
        ("BAJO_SMA200_WEEKLY", "ACUMULAR",             "Bajo SMA200 weekly   ", "Cualquiera           ", "ACUMULAR          "),
        ("ZONA_ACUMULACION",   "ACUMULAR",             "Zona acumul. (≤15%)  ", "Recuperándose        ", "ACUMULAR          "),
        ("ZONA_ACUMULACION",   "ESPERAR_CONFIRMACION", "Zona acumul. (≤15%)  ", "Todavía bajando      ", "ESPERAR CONFIRM.  "),
        ("ZONA_VIGILANCIA",    "ESPERAR_CONFIRMACION", "Zona vigil. (15-20%) ", "Cualquiera           ", "ESPERAR CONFIRM.  "),
        ("MERCADO_ALTO",       "FUERA_DE_ZONA",        "Lejos de zona (>20%) ", "Cualquiera           ", "FUERA DE ZONA     "),
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

    # ── CICLO MACRO ───────────────────────────────────────────────
    if analisis_ciclo:
        _imprimir_ciclo_macro(analisis_ciclo, sep_fino)

    # ── FUNDAMENTALS BTC ──────────────────────────────────────────
    if analisis_fundamental and "BTC" in analisis_fundamental:
        _imprimir_fundamental(analisis_fundamental["BTC"], "BTC", sep_fino)

    # ── CONCLUSIÓN INTEGRADA BTC ──────────────────────────────────
    if conclusiones and "BTC" in conclusiones:
        print(f"\n{sep_fino}")
        print("  💡 CONCLUSIÓN — BTC")
        print(sep_fino)
        print(f"  {conclusiones['BTC']}")

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
        print("  • P/S ratio (protocolos DeFi con fees): market cap ÷ revenue anual.")
        print("    Referencia TradFi: Robinhood ~6x, CME ~18x.")
        print("    < 10x = barato  |  10–25x = razonable  |  > 25x = caro.")

        for alt in altcoins_activas:
            fund       = (analisis_fundamental or {}).get(alt["nombre"])
            conclusion = (conclusiones or {}).get(alt["nombre"])
            _imprimir_altcoin(alt, sep_fino, fund, conclusion)

    elif altcoins_activas and not btc_en_zona:
        # BTC fuera de zona: mostrar altcoins brevemente sin detalle
        print(f"\n{sep_fino}")
        print("  🔵 ALTCOINS — Fuera de ventana de acumulación BTC")
        print(sep_fino)
        print("  BTC está fuera de zona óptima. Datos de altcoins disponibles")
        print("  pero no es el momento de acumular. Resumen rápido:")
        print()
        for alt in altcoins_activas:
            signal_alt   = alt["signal"]
            zona_alt     = alt.get("zona_altcoin", "")
            cross_alt    = alt.get("cross_event", "NINGUNO")
            etiqueta     = {"ACUMULAR": "✅", "ESPERAR_CONFIRMACION": "⏳", "FUERA_DE_ZONA": "📊"}.get(signal_alt, "⚪")
            zona_tag     = {"BAJO_SMA200D": "🔴", "ZONA_ACUMULACION": "🟠", "ZONA_VIGILANCIA": "🟡", "FUERA_DE_ZONA": "🟢"}.get(zona_alt, "")
            cross_tag    = " ⚠️DC" if cross_alt == "DEATH_CROSS" else (" ✨GC" if cross_alt == "GOLDEN_CROSS" else "")
            precio_alt   = alt["precio_actual"]
            silenciado_tag = " [silenciado]" if alt.get("silenciado") else ""
            print(f"  {etiqueta} {alt['nombre']:<6} ${precio_alt:>12,.4f}  {zona_tag} {signal_alt}{cross_tag}{silenciado_tag}")

    print(f"\n{sep_grueso}\n")


def _imprimir_altcoin(alt: dict, sep_fino: str, fundamental: dict = None, conclusion: str = None) -> None:
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

    zona_altcoin = alt.get("zona_altcoin", "SIN_DATOS")
    cross_event  = alt.get("cross_event", "NINGUNO")

    etiquetas_zona_alt = {
        "BAJO_SMA200D":    "🔴 BAJO SMA200D — zona extrema, acumular fuerte.",
        "ZONA_ACUMULACION":"🟠 ZONA ACUMULACION — dentro del 20% de SMA200d.",
        "ZONA_VIGILANCIA": "🟡 ZONA VIGILANCIA — entre 20-30% de SMA200d. Empezar a prestar atención.",
        "FUERA_DE_ZONA":   "🟢 FUERA DE ZONA — más del 30% sobre SMA200d.",
        "SIN_DATOS":       "— Sin datos",
    }

    print(f"\n  ── {nombre} ({alt['symbol']}){silenciado_tag}")
    print(f"  Precio:       ${precio:,.4f}")
    print(f"  Zona:         {etiquetas_zona_alt.get(zona_altcoin, zona_altcoin)}")

    if cross_event == "DEATH_CROSS":
        print("  ⚠️  DEATH CROSS RECIENTE — señal bajista estructural (SMA50 cruzó bajo SMA200).")
    elif cross_event == "GOLDEN_CROSS":
        print("  ✨ GOLDEN CROSS RECIENTE — señal alcista estructural (SMA50 cruzó sobre SMA200).")

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

    # P/S ratio (solo si está disponible)
    ps_ratio    = alt.get("ps_ratio")
    ps_interp   = alt.get("ps_interpretacion")
    rev_anual   = alt.get("revenue_anual_usd")
    mcap_usd    = alt.get("mcap_usd")

    if ps_ratio is not None:
        etiquetas_ps = {
            "BARATO":    "🟢 < 10x — por debajo de exchanges TradFi (Robinhood ~6x, CME ~18x)",
            "RAZONABLE": "🟡 10–25x — rango fair value para exchange en crecimiento",
            "CARO":      "🟠 25–50x — pricing in crecimiento significativo",
            "MUY_CARO":  "🔴 > 50x — premium especulativo elevado",
        }
        rev_str  = f"${rev_anual/1e6:.0f}M" if rev_anual and rev_anual < 1e9 else (f"${rev_anual/1e9:.2f}B" if rev_anual else "—")
        mcap_str = f"${mcap_usd/1e9:.2f}B" if mcap_usd and mcap_usd >= 1e9 else (f"${mcap_usd/1e6:.0f}M" if mcap_usd else "—")
        print(f"  P/S ratio:    {ps_ratio}x  {etiquetas_ps.get(ps_interp, ps_interp)}")
        print(f"                Revenue anual: {rev_str}  |  Market cap: {mcap_str}")

    # Señal
    etiquetas_signal = {
        "ACUMULAR":             "✅ ACUMULAR — zona SMA200 + momentum recuperándose.",
        "ESPERAR_CONFIRMACION": "⏳ ESPERAR CONFIRMACION — en zona pero aún cayendo.",
        "FUERA_DE_ZONA":        "📊 FUERA DE ZONA — lejos de SMA200 daily.",
        "SIN_DATOS":            "— Sin datos suficientes.",
    }
    print(f"  Señal:        {etiquetas_signal.get(signal, signal)}")

    # Fundamentals (si están disponibles para esta coin)
    if fundamental:
        _imprimir_fundamental(fundamental, nombre, sep_fino, indent="  ")

    # Conclusión integrada técnico + fundamental
    if conclusion:
        print(f"\n  💡 Conclusión: {conclusion}")


def _imprimir_fundamental(fund: dict, coin: str, sep_fino: str, indent: str = "") -> None:
    """
    Imprime el bloque de análisis fundamental de una coin.

    thesis_status — posibles valores y su significado de inversión:
      ACUMULAR     Fundamentals refuerzan la thesis, buen momento de entrada
      HOLD         Thesis válida, sin señales de salida, mantener posición
      WATCH        Señales mixtas, monitorear de cerca antes de actuar
      TAKE_PROFIT  Fundamentals sugieren techo de ciclo o sobrevaluación
      STOP_LOSS    Thesis invalidada — hack, competidor, colapso de narrativa
      SIN_DATOS    Información insuficiente
    """
    thesis    = fund.get("thesis_status", "SIN_DATOS")
    resumen   = fund.get("resumen", "")
    positivas = fund.get("señales_positivas", [])
    negativas = fund.get("señales_negativas", [])
    fecha     = fund.get("fecha", "")

    if indent == "":
        print(f"\n{sep_fino}")
        print(f"  📰 FUNDAMENTALS — {coin}  ({fecha})")
        print(sep_fino)
    else:
        print(f"\n{indent}📰 Fundamentals  ({fecha})")

    thesis_emojis = {
        "ACUMULAR":    "✅",
        "HOLD":        "🔵",
        "WATCH":       "🟡",
        "TAKE_PROFIT": "🟠",
        "STOP_LOSS":   "🔴",
        "SIN_DATOS":   "⚪",
    }
    thesis_labels = {
        "ACUMULAR":    "ACUMULAR — fundamentals refuerzan la thesis",
        "HOLD":        "HOLD — thesis válida, mantener posición",
        "WATCH":       "WATCH — señales mixtas, monitorear de cerca",
        "TAKE_PROFIT": "TAKE PROFIT — señales de techo, considerar salida parcial",
        "STOP_LOSS":   "STOP LOSS — thesis invalidada, salir para limitar daño",
        "SIN_DATOS":   "SIN DATOS — información insuficiente",
    }
    emoji = thesis_emojis.get(thesis, "⚪")
    label = thesis_labels.get(thesis, thesis)
    print(f"{indent}  Thesis:  {emoji} {label}")

    if resumen:
        print(f"{indent}  Contexto: {resumen}")

    if positivas:
        print(f"{indent}  Señales positivas:")
        for s in positivas:
            print(f"{indent}    + {s}")

    if negativas:
        print(f"{indent}  Señales negativas:")
        for s in negativas:
            print(f"{indent}    - {s}")


def _imprimir_ciclo_macro(ciclo: dict, sep_fino: str) -> None:
    """
    Imprime la sección de indicadores de ciclo macro en consola.
    Incluye Fear & Greed, dominance trend, SMA200w slope, ATH distance y Pi Cycle.
    """
    print(f"\n{sep_fino}")
    print("  🔄 CICLO MACRO")
    print(sep_fino)

    # Fear & Greed
    fg_val   = ciclo.get("fg_valor")
    fg_clas  = ciclo.get("fg_clasificacion", "—")
    fg_trend = ciclo.get("fg_trend_7d", "SIN_DATOS")
    fg_prev  = ciclo.get("fg_valor_7d_ago")

    if fg_val is not None:
        fg_emojis = {
            "MIEDO EXTREMO": "🔴", "MIEDO": "🟠",
            "NEUTRAL": "⚪", "CODICIA": "🟡", "CODICIA EXTREMA": "🟢",
        }
        trend_simbolo = {"SUBIENDO": "↑", "BAJANDO": "↓", "ESTABLE": "→"}.get(fg_trend, "")
        prev_str = f" (era {fg_prev} hace 7d)" if fg_prev is not None else ""
        emoji_fg = fg_emojis.get(fg_clas, "⚪")
        print(f"  Fear & Greed:     {fg_val} — {emoji_fg} {fg_clas}  {trend_simbolo}{prev_str}")
    else:
        print("  Fear & Greed:     — Sin datos")

    # Dominance trend
    dom_trend   = ciclo.get("dom_trend", "SIN_DATOS")
    dom_cambio  = ciclo.get("dom_cambio_30d")
    dom_hoy     = ciclo.get("dom_hoy_pct")

    if dom_hoy is not None:
        simbolo_dom = "↑" if dom_trend == "SUBIENDO" else "↓" if dom_trend == "BAJANDO" else "→"
        cambio_str  = f"{simbolo_dom}{abs(dom_cambio):.1f}% en 30d" if dom_cambio is not None else ""
        interp_dom  = {
            "SUBIENDO": "capital refugiándose en BTC (early bull o bear)",
            "BAJANDO":  "capital fluyendo a alts — posible altcoin season (late bull)",
            "ESTABLE":  "dominance estable",
        }.get(dom_trend, "")
        print(f"  Dominance trend:  {dom_hoy}%  {cambio_str} — {interp_dom}")
    else:
        print("  Dominance trend:  — Sin datos")

    # SMA200w slope
    slope      = ciclo.get("sma200w_slope", "SIN_DATOS")
    slope_interp = {
        "SUBIENDO": "🟢 SUBIENDO — tendencia macro alcista sostenida",
        "BAJANDO":  "🔴 BAJANDO — tendencia macro deteriorándose",
        "SIN_DATOS": "— Sin datos",
    }
    print(f"  SMA200w slope:    {slope_interp.get(slope, slope)}")

    # ATH distance
    ath_usd  = ciclo.get("ath_usd")
    ath_dist = ciclo.get("ath_distancia_pct")
    if ath_usd is not None and ath_dist is not None:
        dir_ath = "bajo" if ath_dist < 0 else "sobre"
        print(f"  ATH distance:     {abs(ath_dist):.1f}% {dir_ath} ATH (${ath_usd:,.0f})")
    else:
        print("  ATH distance:     — Sin datos")

    # Pi Cycle Top
    pi_estado = ciclo.get("pi_estado", "SIN_DATOS")
    pi_gap    = ciclo.get("pi_gap_pct")
    pi_alerta = ciclo.get("pi_alerta", False)
    pi_111    = ciclo.get("pi_sma111")
    pi_2x350  = ciclo.get("pi_2x350")

    if pi_estado != "SIN_DATOS" and pi_111 is not None:
        if pi_alerta:
            # Cruce activo: señal histórica de top de ciclo
            print(f"  Pi Cycle Top:     ⚠️  SEÑAL DE TOP ACTIVA")
            print(f"                    SMA111: ${pi_111:,.0f} ≥ 2×SMA350: ${pi_2x350:,.0f}")
        else:
            # Bull en progreso: mostrar brecha (negativa = bull sano, alejado del cruce)
            print(f"  Pi Cycle Top:     ✅ SIN SEÑAL DE TOP — bull en progreso")
            print(f"                    SMA111: ${pi_111:,.0f}  |  2×SMA350: ${pi_2x350:,.0f}  |  gap: {pi_gap:+.1f}%")
    else:
        print("  Pi Cycle Top:     — Sin datos (necesita 350+ días de historial)")


def formatear_para_telegram(
    analisis_btc: dict,
    analisis_dominance: dict,
    analisis_altcoins: list = None,
    analisis_ciclo: dict = None,
    analisis_fundamental: dict = None,
    conclusiones: dict = None,
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

    cross_btc = analisis_btc.get("cross_event", "NINGUNO")
    cross_btc_linea = ""
    if cross_btc == "DEATH_CROSS":
        cross_btc_linea = "\n⚠️ *DEATH CROSS reciente* — SMA50 cruzó bajo SMA200"
    elif cross_btc == "GOLDEN_CROSS":
        cross_btc_linea = "\n✨ *GOLDEN CROSS reciente* — SMA50 cruzó sobre SMA200"

    mensaje = (
        f"{emoji} *CryptoSeeker — BTC Report*\n"
        f"_{timestamp}_\n\n"
        f"*Precio:* ${precio:,.2f}\n\n"
        f"*SMA200 weekly:* ${sma200w:,.2f} ({abs(dist200w):.1f}% {dir200w})\n"
        f"*SMA200 daily:*  ${sma200d:,.2f} ({abs(dist200d):.1f}% {dir200d})\n\n"
        f"*Señal:* {etiquetas.get(signal, signal)}{cross_btc_linea}\n\n"
        f"*Dominance ajustada:* {analisis_dominance['dominance_adjusted_pct']}%\n"
        f"_{analisis_dominance['interpretacion']}_"
    )

    # Ciclo macro: resumen compacto para Telegram
    if analisis_ciclo:
        fg_val  = analisis_ciclo.get("fg_valor")
        fg_clas = analisis_ciclo.get("fg_clasificacion", "")
        slope   = analisis_ciclo.get("sma200w_slope", "")
        ath_d   = analisis_ciclo.get("ath_distancia_pct")
        pi_al   = analisis_ciclo.get("pi_alerta", False)

        ciclo_lineas = ["\n\n*— Ciclo Macro —*"]
        if fg_val is not None:
            ciclo_lineas.append(f"Fear & Greed: {fg_val} ({fg_clas})")
        if slope:
            ciclo_lineas.append(f"SMA200w: {slope}")
        if ath_d is not None:
            ciclo_lineas.append(f"ATH: {abs(ath_d):.1f}% {'bajo' if ath_d < 0 else 'sobre'} ATH")
        if pi_al:
            ciclo_lineas.append("⚠️ Pi Cycle Top: SEÑAL DE TOP ACTIVA")

        mensaje += "\n".join(ciclo_lineas)

    # Fundamentals BTC: resumen compacto
    if analisis_fundamental and "BTC" in analisis_fundamental:
        fund_btc   = analisis_fundamental["BTC"]
        thesis     = fund_btc.get("thesis_status", "SIN_DATOS")
        resumen    = fund_btc.get("resumen", "")
        thesis_tag = _thesis_tag_telegram(thesis)
        if resumen:
            mensaje += f"\n\n*— Fundamentals BTC —*\nThesis: {thesis_tag}\n_{resumen}_"

    # Conclusión integrada BTC
    if conclusiones and "BTC" in conclusiones:
        mensaje += f"\n\n*💡 Conclusión:* _{conclusiones['BTC']}_"

    # Altcoins: incluir solo no silenciadas cuando BTC está en zona
    btc_en_zona = signal in ("ACUMULAR", "ESPERAR_CONFIRMACION")
    altcoins_visibles = [
        a for a in (analisis_altcoins or [])
        if a and not a.get("silenciado", False)
    ]

    if altcoins_visibles and btc_en_zona:
        mensaje += "\n\n*— Altcoins —*"
        for alt in altcoins_visibles:
            fund       = (analisis_fundamental or {}).get(alt["nombre"])
            conclusion = (conclusiones or {}).get(alt["nombre"])
            mensaje   += _formatear_altcoin_telegram(alt, fund, conclusion)

    return mensaje


def _thesis_tag_telegram(thesis_status: str) -> str:
    """Devuelve el tag compacto de thesis_status para mensajes Telegram."""
    tags = {
        "ACUMULAR":    "✅ ACUMULAR",
        "HOLD":        "🔵 HOLD",
        "WATCH":       "🟡 WATCH",
        "TAKE_PROFIT": "🟠 TAKE PROFIT",
        "STOP_LOSS":   "🔴 STOP LOSS",
        "SIN_DATOS":   "⚪ sin datos",
    }
    return tags.get(thesis_status, "⚪ sin datos")


def _formatear_altcoin_telegram(alt: dict, fundamental: dict = None, conclusion: str = None) -> str:
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

    zona_altcoin = alt.get("zona_altcoin", "SIN_DATOS")
    cross_event  = alt.get("cross_event", "NINGUNO")

    zonas_telegram = {
        "BAJO_SMA200D":    "🔴 BAJO SMA200D",
        "ZONA_ACUMULACION":"🟠 ZONA ACUM",
        "ZONA_VIGILANCIA": "🟡 ZONA VIGIL",
        "FUERA_DE_ZONA":   "🟢 FUERA ZONA",
    }

    lineas = [f"\n\n{emoji} *{nombre}* (${precio:,.4f})"]
    lineas.append(f"Zona: {zonas_telegram.get(zona_altcoin, zona_altcoin)}")

    if cross_event == "DEATH_CROSS":
        lineas.append("⚠️ DEATH CROSS reciente")
    elif cross_event == "GOLDEN_CROSS":
        lineas.append("✨ GOLDEN CROSS reciente")

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

    ps_ratio  = alt.get("ps_ratio")
    ps_interp = alt.get("ps_interpretacion")
    if ps_ratio is not None:
        ps_emojis = {"BARATO": "🟢", "RAZONABLE": "🟡", "CARO": "🟠", "MUY_CARO": "🔴"}
        emoji_ps = ps_emojis.get(ps_interp, "⚪")
        lineas.append(f"P/S: {ps_ratio}x {emoji_ps} ({ps_interp.lower().replace('_', ' ')})")

    if fundamental:
        thesis = fundamental.get("thesis_status", "SIN_DATOS")
        lineas.append(f"Thesis: {_thesis_tag_telegram(thesis)}")

    if conclusion:
        lineas.append(f"💡 _{conclusion}_")

    return "\n".join(lineas)
