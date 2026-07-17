FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system --gid 10001 wilsonlab \
    && adduser --system --uid 10001 --ingroup wilsonlab --home /nonexistent --no-create-home wilsonlab \
    && mkdir -p /data/backups \
    && chown -R 10001:10001 /data

COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir .

USER 10001:10001
EXPOSE 8055

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8055", "--proxy-headers", "--forwarded-allow-ips", "*"]
