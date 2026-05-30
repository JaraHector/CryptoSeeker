# CryptoSeeker — Arquitectura del Sistema

## Visión general

CryptoSeeker es un sistema de análisis y alertas de criptomonedas organizado en 4 capas.
El objetivo es cubrir el ciclo completo de inversión: acumulación, hold, take profit y rotación,
usando señales técnicas + indicadores de ciclo macro + contexto fundamental.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Capa 1 — DATA SOURCES                                              │
│  Binance (ccxt) · CoinGecko · Alternative.me · DeFiLlama           │
│  CryptoPanic (roadmap) · TradingView webhook (roadmap)              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│  Capa 2 — DATA PIPELINE                                             │
│  SMAs (50/200 daily · 200 weekly) · RSI(14) · Pi Cycle (111/350d)  │
│  Dominance ajustada · Dominance trend 30d · SMA200w slope           │
│  ATH distance · Fear & Greed · P/S ratio (DeFiLlama)               │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│  Capa 3 — AGENTS                                                    │
│  analizar_btc() · analizar_ciclo_macro() · analizar_altcoin()       │
│  Análisis fundamental LLM (roadmap)                                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│  Capa 4 — OUTPUT                                                    │
│  Consola · Telegram · HTML + email (roadmap)                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Capa 1 — Data Sources

### Binance (via ccxt)
- Librería: `ccxt`
- Datos: candles OHLCV de cualquier par
- Timeframes: `1d` (diario, limit=400) y `1w` (semanal, limit=210)
- Exchanges soportados: Binance, Coinbase, Kraken (exchange-agnostic via parámetro)
- No requiere API key para datos públicos de mercado

### CoinGecko
- API pública gratuita, sin API key en el tier básico
- Datos actuales: market cap global, Bitcoin Dominance standard y ajustada
- Datos históricos: market cap chart de BTC y global (para dominance trend 30d)

### Alternative.me
- Fear & Greed Index — índice de sentimiento del mercado (0-100)
- API pública gratuita, devuelve hasta 30 días de historial
- Usado para detectar extremos de sentimiento (miedo extremo = bottom, codicia extrema = top)

### DeFiLlama
- API pública gratuita, sin API key
- Datos: fees/revenue de protocolos DeFi y market cap
- Usado para calcular P/S ratio de protocolos con revenue on-chain (ej: Hyperliquid)

### CryptoPanic (roadmap)
- Agregador de noticias crypto, free tier sin API key
- Fuente de noticias para el análisis fundamental diario con Claude API

---

## Capa 2 — Data Pipeline

### Indicadores de BTC

#### SMA50 Daily
- Promedio de los últimos 50 cierres diarios (~2 meses)
- Indica tendencia de corto/mediano plazo
- Cuando precio > SMA50 > SMA200: tendencia ALCISTA

#### SMA200 Daily
- Promedio de los últimos 200 cierres diarios (~9 meses)
- Referencia de mediano plazo, muy seguido por institucionales
- Usado para timing de entrada: indica si el momentum empezó a recuperarse

#### SMA200 Weekly
- Promedio de los últimos 200 cierres semanales (~4 años)
- Soporte macro histórico de BTC — nunca cerró mucho tiempo por debajo
- Base del sistema de zonas de acumulación:
  - `ZONA_ACUMULACION`: dentro del **15%** sobre SMA200w — zona real de compra en tranches
  - `ZONA_VIGILANCIA`: entre **15% y 20%** sobre SMA200w — empezar a prestar atención
  - `BAJO_SMA200_WEEKLY`: por debajo — zona extrema histórica, acumular fuerte
  - `MERCADO_ALTO`: más del 20% sobre SMA200w — fuera de zona óptima

#### SMA200 Weekly Slope
- Compara el valor actual de la SMA200w con el de hace 4 semanas
- SUBIENDO: tendencia macro alcista sostenida
- BAJANDO: deterioro de la tendencia macro

#### Pi Cycle Top Indicator
- Dos medias móviles: SMA_111 y 2×SMA_350 (requiere 350+ días de datos diarios)
- Cuando SMA_111 cruza POR ENCIMA de 2×SMA_350 → señal histórica de techo de ciclo
- Mientras SMA_111 < 2×SMA_350: bull market en progreso
- El gap porcentual indica cuán lejos estamos del cruce (top)

#### ATH Distance
- Distancia porcentual entre el precio actual y el máximo histórico
- Calculado sobre el historial de 210 semanas (cubre ciclos 2021 y 2024)
- En bull sano, el ATH del ciclo anterior actúa como soporte

### Indicadores de ciclo macro

#### Fear & Greed Index
- Escala 0-100: 0 = miedo extremo, 100 = codicia extrema
- Indicador contrarian: miedo extremo sostenido = bottom, codicia extrema sostenida = top
- Se calcula tendencia de 7 días para detectar si el sentimiento mejora o empeora

#### Bitcoin Dominance Trend (30d)
- Compara dominance de BTC hoy vs hace 30 días
- Dominance subiendo: capital fluyendo a BTC (early bull o refugio en bear)
- Dominance bajando: capital saliendo a alts — posible altseason (late bull)

### Indicadores de altcoins

#### RSI(14)
- Relative Strength Index con suavizado de Wilder (estándar)
- RSI < 35: sobrevendido fuerte → señal de acumulación
- RSI > 70: sobrecomprado → no acumular, esperar corrección
- Funciona desde ~30 velas, útil para coins con historial limitado

#### Ratio vs BTC (30d)
- Cuánto BTC vale 1 unidad de la altcoin, hoy vs hace 30 días
- Mide alpha real: si la altcoin no gana vs BTC, es mejor quedarse en BTC
- Para coins sin par BTC directo en el exchange: ratio sintético = precio_alt_USD / precio_BTC_USD

#### P/S Ratio (DeFiLlama)
- Market cap / revenue anualizado (fees últimos 30d × 12)
- Solo para protocolos DeFi con fees medibles (ej: Hyperliquid)
- Referencia TradFi: Robinhood ~6x, CME ~18x
- < 10x = potencialmente barato | 10–25x = razonable | > 25x = caro

---

## Capa 3 — Agents

### `analizar_btc()` — Señal combinada
Cruza el contexto macro (SMA200 weekly) con la tendencia daily (SMA50 + SMA200 daily):

| SMA200 Weekly         | SMA200 Daily        | Señal                |
|-----------------------|---------------------|----------------------|
| Bajo SMA200 weekly    | Cualquiera          | ACUMULAR             |
| Zona acumul. (≤15%)   | Recuperándose       | ACUMULAR             |
| Zona acumul. (≤15%)   | Todavía bajando     | ESPERAR CONFIRMACION |
| Zona vigil. (15–20%)  | Cualquiera          | ESPERAR CONFIRMACION |
| Lejos de zona (>20%)  | Cualquiera          | FUERA DE ZONA        |

### `analizar_ciclo_macro()` — Indicadores de ciclo
Consolida Fear & Greed, dominance trend, SMA200w slope, ATH distance y Pi Cycle Top
en un único objeto de análisis para mostrar en el reporte de ciclo macro.

### `analizar_altcoin()` — Señal por coin
Evalúa cada altcoin de forma independiente de BTC usando SMA200 daily, SMA50 daily,
RSI(14) y ratio vs BTC. La señal (ACUMULAR / ESPERAR / FUERA DE ZONA) es propia de
cada coin — la decisión de mostrarla depende del contexto macro de BTC.

### Análisis fundamental (roadmap)
- CryptoPanic → noticias recientes por coin
- Claude API → interpreta el contexto e indica si valida o invalida la thesis de inversión
- Frecuencia: una vez al día (no cada 4 horas)
- Requiere: `ANTHROPIC_API_KEY` en `.env`

---

## Capa 4 — Output

### Consola
Reporte estructurado con secciones en cada ejecución:
1. Precio actual
2. SMA200 weekly (contexto macro + zona)
3. SMA200 daily y SMA50 daily (tendencia)
4. Señal combinada con tabla resaltando la fila activa
5. Contexto estratégico
6. **Ciclo Macro**: Fear & Greed, dominance trend, SMA200w slope, ATH distance, Pi Cycle Top
7. Bitcoin Dominance ajustada
8. Altcoins (detallado si BTC en zona, resumen breve si no)

### Telegram
- Alerta enviada únicamente cuando la señal BTC **cambia** (sin spam)
- Estado de señal persistido en `logs/signal_state.json`
- Altcoins silenciadas excluidas del mensaje (salvo cambio de señal BTC)
- Incluye resumen compacto del ciclo macro (Fear & Greed, slope, ATH, Pi Cycle si hay alerta)

### HTML + email (roadmap)
- Dashboard organizado para el ciclo completo de inversión (acumulación y take profit)
- Sección BTC: ciclo, señal, indicadores macro con contexto narrativo
- Sección altcoins general: contexto de mercado, altseason, alpha vs BTC
- Sección individual por coin: señal, fundamentals, thesis, riesgos
- Envío por email en cada ejecución o solo al cambiar señal

---

## Coins monitoreadas

| Coin | Exchange | Señal individual | P/S ratio | Estado |
|------|----------|-----------------|-----------|--------|
| BTC | Binance | Señal combinada | — | ✅ Implementado |
| TAO (BitTensor) | Binance | ✅ SMA + RSI + ratio BTC | — | ✅ Implementado |
| VVV (Venice) | Coinbase | ✅ SMA + RSI + ratio sintético | — | ✅ Implementado |
| HYPE (Hyperliquid) | Binance | ✅ SMA + RSI + ratio sintético | ✅ DeFiLlama | ✅ Implementado |
| Solana y otras | TBD | Pendiente | TBD | Roadmap |

Máximo recomendado: ~10 coins para no sobrecargar el reporte.

---

## Infraestructura de despliegue

### Testing (actual)
- VM Ubuntu Server 24.04 LTS (minimized) en HP ProLiant Gen8
- Docker + Docker Compose para portabilidad
- Cron job del host: `docker compose run --rm cryptoseeker` cada 4 horas
- Logs: `~/CryptoSeeker/logs/cron.log`
- Estado de señal: `~/CryptoSeeker/logs/signal_state.json`
- Ver guía completa: [cryptoseeker_deploy_v1.md](cryptoseeker_deploy_v1.md)

### Producción (futuro)
- VPS o infraestructura más estable
- Posiblemente systemd en lugar de cron para mejor manejo de errores

---

## Librerías principales

| Librería | Uso | Estado |
|----------|-----|--------|
| ccxt | Conexión a exchanges (Binance, Coinbase, Kraken) | ✅ |
| pandas | Manipulación de DataFrames OHLCV | ✅ |
| requests | HTTP a CoinGecko, Alternative.me, DeFiLlama | ✅ |
| python-dotenv | Variables de entorno | ✅ |
| anthropic | Claude API para análisis fundamental LLM | Roadmap |
