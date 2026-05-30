# CryptoSeeker — Guía de Despliegue v1

Guía completa para desplegar CryptoSeeker en una VM con Ubuntu 24.04 LTS (minimized)
usando Docker. Pensada para entornos de testing en servidores locales (ej: HP ProLiant Gen8).

---

## Paso 0 — Crear la VM con Ubuntu 24.04 LTS Minimized

1. Descargar la ISO de Ubuntu 24.04 LTS desde ubuntu.com
2. Crear una nueva VM en tu hypervisor (Proxmox, VMware, VirtualBox, etc.)
   - RAM mínima recomendada: 1 GB
   - Disco: 10 GB es suficiente para testing
3. Durante la instalación, seleccionar **Ubuntu Server (minimized)**
4. Configurar usuario, hostname y SSH según preferencia
5. Completar la instalación y reiniciar

---

## Paso 1 — Actualizar el sistema

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Paso 2 — Instalar nano (no incluido en la versión minimized)

```bash
sudo apt install -y nano
```

---

## Paso 3 — Instalar Git

```bash
sudo apt install -y git
```

---

## Paso 4 — Instalar Docker (método oficial)

```bash
# Dependencias
sudo apt install -y ca-certificates curl

# Agregar la clave GPG oficial de Docker
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Agregar el repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

## Paso 5 — Agregar tu usuario al grupo docker

Esto evita tener que usar `sudo` en cada comando de Docker.

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## Paso 6 — Verificar la instalación

```bash
docker --version
docker compose version
```

Deberías ver las versiones de Docker y Docker Compose sin errores.

---

## Paso 7 — Clonar y configurar CryptoSeeker

```bash
git clone https://github.com/JaraHector/CryptoSeeker.git
cd CryptoSeeker
cp .env.example .env
nano .env
```

Completar en el `.env`:

```
# Telegram — requerido para alertas
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# Claude API — requerido para análisis fundamental (roadmap, no obligatorio ahora)
# ANTHROPIC_API_KEY=tu_key_aqui
```

Guardar con `Ctrl+O`, salir con `Ctrl+X`.

---

## Paso 8 — Build y primera prueba

```bash
docker compose build
docker compose run --rm cryptoseeker
```

Si el reporte de BTC aparece en consola, todo está funcionando correctamente.

---

## Paso 9 — Configurar el cron para ejecución automática

```bash
crontab -e
```

Agregar la siguiente línea (ejecuta el análisis cada 4 horas):

```
0 */4 * * *  cd /home/$USER/CryptoSeeker && docker compose run --rm cryptoseeker >> logs/cron.log 2>&1
```

Guardar y salir. El sistema ya corre solo.

---

## Actualizar el código

Cuando haya cambios en el repositorio:

```bash
git pull
docker compose build
```

El cron no necesita modificarse.

---

## Resumen del stack

| Componente | Tecnología |
|------------|------------|
| OS | Ubuntu 24.04 LTS Minimized |
| Containerización | Docker + Docker Compose |
| Scheduler | cron (nativo del OS) |
| Lenguaje | Python 3.11 |
| Datos de precio | Binance, Coinbase, Kraken (via ccxt) |
| Datos de mercado | CoinGecko (dominance, market cap histórico) |
| Sentimiento | Alternative.me (Fear & Greed Index) |
| Fundamentals DeFi | DeFiLlama (P/S ratio, revenue) |
| Análisis LLM | Claude API / Anthropic (roadmap) |
