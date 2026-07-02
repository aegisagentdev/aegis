# Deployment Guide

## Docker

```bash
# Build
docker build -t hoodtrade .

# Run doctor
docker run --env-file .env hoodtrade doctor

# Run a scan
docker run --env-file .env hoodtrade scan \
  --token 0xToken --quote 0xQuote --amount 1000
```

## Docker Compose

```bash
# Health check
docker compose run hoodtrade

# Scan
docker compose run scan --token 0x.. --quote 0x.. --amount 500
```

## PyPI (when published)

```bash
pip install hoodtrade
pip install 'hoodtrade[ai]'  # with Claude summaries
```

## From source

```bash
git clone https://github.com/hooddev/hoodtrade
cd hoodtrade
pip install -e '.[ai,dev]'
```

## Environment Variables

See [.env.example](../.env.example) for all configuration options.
The only required variable is `HOODTRADE_RPC_URL`.
