# CryptoSeeker

Sistema de análisis y alertas de criptomonedas. Monitorea BTC y altcoins usando indicadores
técnicos, indicadores de ciclo macro y métricas fundamentales on-chain, generando señales para
identificar zonas de acumulación y toma de ganancias a lo largo del ciclo completo de inversión.

## ¿Qué hace?

**Análisis de BTC:**
- Candles diarias (400 días) y semanales (210 semanas / ~4 años) desde Binance
- SMA50 daily, SMA200 daily, SMA200 weekly
- Señal combinada: cruza contexto macro (weekly) con tendencia (daily)
- Dos niveles de alerta: `ZONA_ACUMULACION` (≤15% sobre SMA200w) y `ZONA_VIGILANCIA` (15–20%)

**Indicadores de ciclo macro (bull vs bear market):**
- Fear & Greed Index (Alternative.me) con tendencia 7 días
- Bitcoin Dominance trend 30 días (CoinGecko)
- SMA200 weekly slope (¿la tendencia macro está subiendo o bajando?)
- ATH distance (¿cuán lejos estamos del máximo histórico?)
- Pi Cycle Top Indicator (SMA111 vs 2×SMA350) — señal histórica de techo de ciclo

**Altcoins monitoreadas: TAO, VVV, HYPE:**
- SMA200 daily, SMA50 daily, RSI(14)
- Ratio vs BTC (30d) — mide alpha real vs quedarse en BTC
- Ratio sintético para coins sin par BTC directo (precio_alt / precio_BTC)
- P/S ratio via DeFiLlama para protocolos con revenue on-chain (HYPE/Hyperliquid)

**Alertas:**
- Reporte completo en consola en cada ejecución
- Telegram: alerta solo cuando la señal BTC **cambia** (sin spam)
- Altcoins silenciadas se muestran en consola pero no en Telegram

## Arquitectura

```
Capa 1 — Data:      Binance (ccxt) · CoinGecko · Alternative.me · DeFiLlama
Capa 2 — Pipeline:  SMAs · RSI · Pi Cycle · Dominance trend · ATH distance
Capa 3 — Agents:    Señal BTC · Ciclo macro · Altcoins · Análisis fundamental LLM (roadmap)
Capa 4 — Output:    Consola · Telegram · HTML + email (roadmap)
```

Ver arquitectura completa: [docs/architecture.md](docs/architecture.md)

## Inicio rápido

```bash
git clone https://github.com/JaraHector/CryptoSeeker.git
cd CryptoSeeker
cp .env.example .env
# Completar TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env
docker compose build
docker compose run --rm cryptoseeker
```

## Despliegue

Para instrucciones completas de instalación en una VM Ubuntu Server ver:
[docs/cryptoseeker_deploy_v1.md](docs/cryptoseeker_deploy_v1.md)

## Roadmap

- [x] Pipeline BTC: SMA50 daily, SMA200 daily, SMA200 weekly
- [x] Bitcoin Dominance ajustada (ex-stablecoins)
- [x] Señal combinada con tabla de contexto (ACUMULAR / ESPERAR / FUERA DE ZONA)
- [x] Alertas Telegram (solo al cambiar la señal)
- [x] Docker + cron job en Ubuntu Server
- [x] Altcoins TAO, VVV, HYPE: SMA, RSI, ratio vs BTC, señal individual
- [x] P/S ratio via DeFiLlama para protocolos con revenue (HYPE)
- [x] Indicadores de ciclo macro: Fear & Greed, dominance trend, Pi Cycle Top, ATH distance
- [x] Umbrales BTC: ZONA_ACUMULACION (15%) y ZONA_VIGILANCIA (20%)
- [ ] Análisis fundamental diario (CryptoPanic + Claude API)
- [ ] Más altcoins (Solana y otras por definir, máx ~10 total)
- [ ] Reportes HTML enviados por email
- [ ] Trading automatizado
