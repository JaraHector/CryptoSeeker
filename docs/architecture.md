# CryptoSeeker — Arquitectura del Sistema

## Visión general

CryptoSeeker es un sistema de análisis y alertas de criptomonedas organizado en 4 capas.
El objetivo final es tener señales técnicas + contexto fundamental para tomar decisiones
de acumulación, con visión futura de trading automatizado.

```
┌─────────────────────────────────────────────────────────────┐
│  Capa 1 — DATA SOURCES                                      │
│  Binance (ccxt) · CoinGecko · TradingView webhook (futuro)  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Capa 2 — DATA PIPELINE                                     │
│  SMA50 daily · SMA200 daily · SMA200 weekly                 │
│  BTC Dominance (ex-stablecoins) · Fibonacci (roadmap)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Capa 3 — AI AGENTS                                         │
│  Señal combinada (rule-based) · Análisis fundamental (LLM)  │
│  Comparación de pares · Contexto de altcoins                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Capa 4 — OUTPUT                                            │
│  Consola · Telegram · HTML (roadmap)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Capa 1 — Data Sources

### Binance (via ccxt)
- Librería: `ccxt==4.4.61`
- Datos: candles OHLCV de cualquier par (BTC/USDT, ETH/USDT, etc.)
- Timeframes usados: `1d` (diario) y `1w` (semanal)
- No requiere API key para datos públicos de mercado
- Las API keys de Binance están reservadas para trading futuro

### CoinGecko
- API pública gratuita, sin API key en el tier básico
- Datos: market cap global, Bitcoin Dominance
- Dominance **ajustada**: excluye stablecoins (USDT, USDC, DAI, etc.) del total del mercado
  para mostrar la dominancia real de BTC sobre las altcoins activas

### TradingView (roadmap)
- Alternativa a polling: recibir datos vía webhook en tiempo real
- Evita el delay del cron job para señales de corto plazo

---

## Capa 2 — Data Pipeline

### Indicadores implementados

#### SMA50 Daily
- Promedio de los últimos 50 cierres diarios (~2 meses)
- Indica la tendencia de corto/mediano plazo
- Se compara con SMA200 daily para determinar si el mercado es alcista o bajista

#### SMA200 Daily
- Promedio de los últimos 200 cierres diarios (~9 meses)
- El indicador más seguido por traders e institucionales
- **Uso en CryptoSeeker:** timing de entrada — indica si el momentum empezó a recuperarse
- Cuando el precio está por encima: tendencia alcista, momentum positivo
- Cuando el precio está por debajo: tendencia bajista, momentum negativo

#### SMA200 Weekly
- Promedio de los últimos 200 cierres semanales (~4 años)
- Incluye los ciclos bajistas de 2022-2023, por eso su valor es mucho más bajo que el daily
- **Uso en CryptoSeeker:** zona de acumulación macro
- Históricamente BTC nunca cerró mucho tiempo por debajo de esta SMA
- Zona de acumulación: precio dentro del 20% sobre la SMA200 weekly

#### Bitcoin Dominance ajustada
- Fórmula estándar: BTC market cap / Total market cap * 100
- Fórmula ajustada: BTC market cap / (Total market cap - Stablecoin market cap) * 100
- La diferencia entre ambas indica cuánto capital está refugiado en stablecoins
- Alta dominance ajustada (>60%): altcoins débiles, mercado favorable para BTC
- Baja dominance ajustada (<50%): posible temporada de altcoins

### Indicadores en roadmap

#### Fibonacci Retracement
- Niveles clave: 23.6%, 38.2%, 50%, 61.8%, 78.6%
- Se calcula entre el último máximo y mínimo significativo del ciclo
- Permite identificar zonas de soporte donde el precio podría rebotar
- La confluencia SMA200 weekly + nivel Fibonacci = señal de acumulación más fuerte

---

## Capa 3 — AI Agents

### Estado actual: rule-based
El módulo `agents/analyzer.py` implementa lógica de reglas (if/else) para generar señales.
No hay LLM todavía — el comentario en el código marca dónde se integrará.

### Señal combinada (implementada)
Cruza el contexto macro (SMA200 weekly) con la tendencia daily (SMA200 daily):

| SMA200 Weekly       | SMA200 Daily        | Señal                |
|---------------------|---------------------|----------------------|
| Bajo SMA200 weekly  | Cualquiera          | ACUMULAR             |
| Zona acumulación    | Recuperándose       | ACUMULAR             |
| Zona acumulación    | Todavía bajando     | ESPERAR CONFIRMACION |
| Lejos de zona       | Cualquiera          | FUERA DE ZONA        |

### Análisis fundamental (roadmap)
- **Fuente de datos:** CryptoPanic API (agregador de noticias crypto, free tier sin API key)
- **Interpretación:** Claude API (Anthropic) genera un párrafo de contexto
- **Frecuencia:** una vez al día (no cada 4 horas como el análisis técnico)
- **Requiere:** `ANTHROPIC_API_KEY` en el `.env`
- **Costo estimado:** centavos por día usando claude-haiku (modelo más económico)
- **Scope:** BTC primero, luego altcoins (máx 10 coins en total)

### Altcoins (roadmap)
- TAO (BitTensor) y Venice son las primeras en incorporarse
- Lógica: cuando BTC entra en zona de acumulación, alertar también sobre TAO y Venice
- Los altcoins históricamente siguen a BTC: si BTC acumula, ellos también pueden hacerlo

---

## Capa 4 — Output

### Consola (implementado)
Reporte estructurado con secciones:
- Precio actual
- SMA200 weekly (contexto macro)
- SMA200 daily (tendencia mediano plazo)
- SMA50 daily (tendencia corto plazo)
- Señal combinada con tabla resaltando la fila activa
- Contexto estratégico (explicación en lenguaje natural)
- Bitcoin Dominance

### Telegram (roadmap inmediato)
- La función `formatear_para_telegram()` ya está escrita en `outputs/notifier.py`
- Falta: crear bot en BotFather, agregar `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` al `.env`
- Librería a usar: `python-telegram-bot` (más completa que requests directo)

### HTML (roadmap)
- Reporte visual para toma rápida de decisiones
- Diseño limpio con semáforos de colores según señal

---

## Infraestructura de despliegue

### Testing (actual)
- VM Ubuntu Server 24.04 LTS (minimized) en HP ProLiant Gen8
- Docker + Docker Compose para portabilidad
- Cron job del host: `docker compose run --rm cryptoseeker` cada 4 horas
- Ver guía completa: [cryptoseeker_deploy_v1.md](cryptoseeker_deploy_v1.md)

### Producción (futuro)
- VPS o infraestructura más estable
- Posiblemente systemd en lugar de cron para mejor manejo de errores
- Monitoreo de uptime

---

## Coins monitoreadas

| Coin | Estado | Notas |
|------|--------|-------|
| BTC | ✅ Implementado | Base del sistema |
| TAO (BitTensor) | Roadmap | Altcoin de interés principal |
| Venice (VVV) | Roadmap | Altcoin de interés principal |
| Otras | Roadmap | Máximo 10 coins en total |

---

## Librerías principales

| Librería | Uso | Estado |
|----------|-----|--------|
| ccxt | Conexión a exchanges (Binance) | ✅ Instalada |
| pandas | Manipulación de datos | ✅ Instalada |
| requests | Llamadas HTTP a CoinGecko | ✅ Instalada |
| python-dotenv | Variables de entorno | ✅ Instalada |
| anthropic | Claude API para LLM | Roadmap |
| python-telegram-bot | Envío de alertas | Roadmap |
| pandas-ta | Indicadores técnicos adicionales | Removida temporalmente (conflicto con pandas 2.x) |
