# Multi-stage Dockerfile para u1-agrocount-platform (Cloud Run GPU L4 & API Scale-to-Zero)
FROM python:3.11-slim AS builder

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ ./src/

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PORT=8080

RUN groupadd -g 10001 agrocount && \
    useradd -u 10001 -g agrocount -m -s /bin/bash agrocount

WORKDIR /app
COPY --from=builder /app/src ./src
COPY --from=builder /app/README.md ./README.md
RUN mkdir -p /app/data/storage && chown -R agrocount:agrocount /app

USER 10001:10001
EXPOSE 8080

CMD ["python3", "-c", "from agrocount.api import create_http_server; srv = create_http_server('0.0.0.0', 8080); srv.serve_forever()"]
