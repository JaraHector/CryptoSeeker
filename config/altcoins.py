"""
Registro de altcoins monitoreadas por CryptoSeeker.

Para cada coin podés:
  - Agregar:   añadir un dict a la lista ALTCOINS
  - Quitar:    "activo": False  — queda en el archivo pero no se procesa
  - Silenciar: "silenciado": True  — aparece en consola pero no envía Telegram
               (excepto cuando BTC cambia a ACUMULAR, que alerta todo)

Campos requeridos:
  nombre      Etiqueta legible (se usa en el reporte)
  symbol      Par en el exchange (ej: "TAO/USDT")
  exchange    Exchange a usar: "binance", "coinbase", "kraken"
  btc_symbol  Par vs BTC para calcular el ratio (ej: "TAO/BTC"). None si no existe.
  activo      True = se monitorea. False = se ignora completamente.
  silenciado  True = solo consola, sin Telegram (salvo señal BTC crítica).
"""

ALTCOINS = [
    {
        "nombre":     "TAO",
        "symbol":     "TAO/USDT",
        "exchange":   "binance",
        "btc_symbol": "TAO/BTC",
        "activo":     True,
        "silenciado": False,
    },
    {
        "nombre":     "VVV",
        "symbol":     "VVV/USD",
        "exchange":   "coinbase",
        "btc_symbol": None,  # Coinbase no ofrece VVV/BTC
        "activo":     True,
        "silenciado": False,
    },
]
