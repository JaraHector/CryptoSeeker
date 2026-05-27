"""
Módulo de envío de alertas por Telegram.

Lógica de envío: solo notifica cuando la señal combinada CAMBIA.
Esto evita spam — el cron corre cada 4hs pero Telegram solo se activa
cuando hay algo nuevo que informar.

El estado de la última señal se persiste en logs/signal_state.json
para compararlo en la próxima ejecución.
"""

import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

STATE_FILE = "logs/signal_state.json"


def send_alert_if_changed(mensaje: str, signal_actual: str) -> None:
    """
    Envía alerta por Telegram solo si la señal combinada cambió desde la última ejecución.

    Args:
        mensaje:       Texto formateado (Markdown) para enviar.
        signal_actual: Señal combinada actual (ACUMULAR / ESPERAR_CONFIRMACION / FUERA_DE_ZONA).
    """
    token   = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    # Si no hay credenciales configuradas, skip silencioso
    if not token or not chat_id or token == "tu_token_aqui":
        print("Telegram no configurado, saltando envío.")
        return

    last_signal = _load_last_signal()

    if signal_actual == last_signal:
        print(f"Señal sin cambios ({signal_actual}), no se envía Telegram.")
        return

    # La señal cambió — enviamos
    razon = f"{last_signal or 'inicio'} → {signal_actual}"
    _send_message(token, chat_id, mensaje)
    _save_state(signal_actual)
    print(f"Telegram enviado. Motivo: {razon}")


def _send_message(token: str, chat_id: str, texto: str) -> None:
    """Envía un mensaje a Telegram usando la API HTTP directamente."""
    url     = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id":    chat_id,
        "text":       texto,
        "parse_mode": "Markdown",
    }
    response = requests.post(url, json=payload, timeout=10)

    if not response.ok:
        # Mostramos el error de Telegram sin exponer el token en la URL
        error_detail = response.json().get("description", "error desconocido")
        raise RuntimeError(f"Telegram API error {response.status_code}: {error_detail}")


def _load_last_signal() -> str | None:
    """Carga la última señal guardada. Devuelve None si no existe el archivo."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("last_signal")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _save_state(signal: str) -> None:
    """Persiste la señal actual para comparar en la próxima ejecución."""
    os.makedirs("logs", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({
            "last_signal": signal,
            "updated_at":  datetime.now().isoformat(),
        }, f, indent=2)
