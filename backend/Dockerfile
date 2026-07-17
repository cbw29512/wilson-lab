FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system wilsonlab \
    && adduser --system --ingroup wilsonlab wilsonlab \
    && mkdir -p /data/backups \
    && chown -R wilsonlab:wilsonlab /data

COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir .

USER wilsonlab
EXPOSE 8055

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8055", "--proxy-headers", "--forwarded-allow-ips", "*"]
