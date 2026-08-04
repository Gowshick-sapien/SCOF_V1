FROM python:3.11-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_RETRIES=10
ENV PIP_PREFER_BINARY=1

RUN pip install --upgrade pip setuptools wheel

COPY shared /app/shared
RUN pip install -e /app/shared

COPY services/etl /app/services/etl
RUN pip install -e /app/services/etl

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "services.etl.src.main", "--mode", "full"]
