"""
Módulo de notificaciones y presentación de resultados.
Por ahora imprime en consola con formato legible.
En la segunda etapa, se agrega el envío por Telegram.
"""

from datetime import datetime


def imprimir_reporte(analisis_btc: dict, analisis_dominance: dict) -> None:
    """
    Imprime en consola un reporte formateado con el análisis completo.

    Args:
        analisis_btc:        Resultado de analizar_btc() del agente.
        analisis_dominance:  Resultado de analizar_dominance() del agente.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separador = "=" * 60

    print(f"\n{separador}")
    print(f"  CRYPTOSEEKER - Reporte BTC")
    print(f"  {timestamp}")
    print(separador)

    # --- Sección: Precio y SMAs ---
    print("\n📊 PRECIO Y MEDIAS MOVILES (BTC/USDT)")
    print(f"  {analisis_btc['descripcion']}")

    # --- Sección: Nivel de alerta ---
    nivel = analisis_btc["nivel_alerta"]
    tendencia = analisis_btc["tendencia"]
    print(f"\n  Tendencia:    {tendencia}")
    print(f"  Nivel alerta: {nivel}")

    # --- Sección: Dominance ---
    print(f"\n🌐 BITCOIN DOMINANCE")
    print(f"  Estándar:          {analisis_dominance['dominance_standard_pct']}%")
    print(f"  Ajustada (ex-USDT): {analisis_dominance['dominance_adjusted_pct']}%")
    print(f"  Diferencia:        +{analisis_dominance['diferencia_pct']}% (capital en stables)")
    print(f"  Interpretación:    {analisis_dominance['interpretacion']}")

    print(f"\n{separador}\n")


def formatear_para_telegram(analisis_btc: dict, analisis_dominance: dict) -> str:
    """
    Genera el texto formateado para enviar por Telegram.
    Telegram soporta Markdown básico: *negrita*, _cursiva_, `código`.
    Esta función se usará en la segunda etapa del proyecto.

    Args:
        analisis_btc:        Resultado de analizar_btc() del agente.
        analisis_dominance:  Resultado de analizar_dominance() del agente.

    Returns:
        String formateado listo para enviar como mensaje de Telegram.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    nivel = analisis_btc["nivel_alerta"]

    # Elegimos un emoji según el nivel de alerta
    emojis_alerta = {
        "NORMAL": "🟢",
        "ATENCION": "🟡",
        "CRITICO": "🔴",
        "DEBAJO_SMA200": "⛔",
    }
    emoji = emojis_alerta.get(nivel, "⚪")

    mensaje = (
        f"{emoji} *CryptoSeeker - BTC Report*\n"
        f"_{timestamp}_\n\n"
        f"*Precio:* ${analisis_btc.get('precio_actual', 'N/A'):,.2f}\n"
        f"*Tendencia:* {analisis_btc['tendencia']}\n"
        f"*Alerta:* {nivel}\n\n"
        f"*Dominance estándar:* {analisis_dominance['dominance_standard_pct']}%\n"
        f"*Dominance ajustada:* {analisis_dominance['dominance_adjusted_pct']}%\n\n"
        f"_{analisis_dominance['interpretacion']}_"
    )

    return mensaje
