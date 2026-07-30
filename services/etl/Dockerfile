FROM python:3.11-slim

WORKDIR /app

COPY shared /app/shared
RUN pip install --no-cache-dir -e /app/shared

COPY services/etl /app/services/etl
RUN pip install --no-cache-dir -e /app/services/etl

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "services.etl.src.main", "--mode", "full"]
