# CryptoSeeker

Sistema de análisis y alertas de criptomonedas. Monitorea BTC usando indicadores técnicos
(SMA50 daily, SMA200 daily, SMA200 weekly) y Bitcoin Dominance ajustada (excluye stablecoins),
generando señales combinadas para identificar zonas de acumulación.

## ¿Qué hace?

- Trae candles diarias y semanales de BTC desde Binance
- Calcula SMA50 daily, SMA200 daily y SMA200 weekly
- Obtiene Bitcoin Dominance desde CoinGecko, excluyendo stablecoins
- Genera una **señal combinada** cruzando contexto macro (weekly) con tendencia (daily):
  - `ACUMULAR` — zona de acumulación macro activa y momentum recuperándose
  - `ESPERAR CONFIRMACION` — zona de acumulación pero precio aún cayendo
  - `FUERA DE ZONA` — precio lejos de la zona óptima de acumulación
- Imprime un reporte en consola con contexto estratégico

## Arquitectura

```
Capa 1 — Data:      Binance (ccxt) + CoinGecko
Capa 2 — Pipeline:  SMA50/200 daily · SMA200 weekly · Dominance · Fibonacci (roadmap)
Capa 3 — Agents:    Señal combinada · Análisis fundamental con LLM (roadmap)
Capa 4 — Output:    Consola · Telegram (roadmap) · HTML (roadmap)
```

Ver arquitectura completa: [docs/architecture.md](docs/architecture.md)

## Inicio rápido

```bash
git clone https://github.com/JaraHector/CryptoSeeker.git
cd CryptoSeeker
cp .env.example .env
# Las keys son opcionales para la versión actual (datos públicos no requieren auth)
docker compose build
docker compose run --rm cryptoseeker
```

## Despliegue

Para instrucciones completas de instalación en una VM Ubuntu Server ver:
[docs/cryptoseeker_deploy_v1.md](docs/cryptoseeker_deploy_v1.md)

## Roadmap

- [x] Pipeline BTC: SMA50 daily, SMA200 daily, SMA200 weekly
- [x] Bitcoin Dominance ajustada (ex-stablecoins)
- [x] Señal combinada con tabla de contexto
- [x] Docker + guía de despliegue en Ubuntu Server
- [ ] Fibonacci Retracement en el pipeline
- [ ] Alertas por Telegram
- [ ] Análisis fundamental diario (CryptoPanic + Claude API)
- [ ] Soporte para TAO (BitTensor) y Venice
- [ ] Reportes en HTML
- [ ] Trading automatizado
