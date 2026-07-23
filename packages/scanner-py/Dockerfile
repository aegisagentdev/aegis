FROM python:3.12-slim AS base

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src/ src/

RUN pip install --no-cache-dir .

FROM base AS with-ai
RUN pip install --no-cache-dir '.[ai]'

FROM base AS production
ENTRYPOINT ["aegis"]
CMD ["--help"]
