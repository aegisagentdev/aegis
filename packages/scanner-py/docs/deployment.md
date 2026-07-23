# Deployment Guide

## Docker

```bash
# Build
docker build -t aegis .

# Run doctor
docker run --env-file .env aegis doctor

# Run a scan
docker run --env-file .env aegis scan \
  --token 0xToken --quote 0xQuote --amount 1000
```

## Docker Compose

```bash
# Health check
docker compose run aegis

# Scan
docker compose run scan --token 0x.. --quote 0x.. --amount 500
```

## PyPI (when published)

```bash
pip install aegis
pip install 'aegis[ai]'  # with Claude summaries
```

## From source

```bash
git clone https://github.com/aegis/aegis
cd aegis
pip install -e '.[ai,dev]'
```

## Environment Variables

See [.env.example](../.env.example) for all configuration options.
The only required variable is `AEGIS_RPC_URL`.
