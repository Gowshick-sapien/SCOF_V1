FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_RETRIES=10
ENV PIP_PREFER_BINARY=1

RUN pip install --upgrade pip setuptools wheel

# Copy shared library and install it
COPY shared /app/shared
RUN pip install -e /app/shared

# Copy simulation service and install dependencies
COPY services/simulation /app/services/simulation
WORKDIR /app/services/simulation
RUN pip install -e .

ENV PYTHONPATH=/app/services/simulation:/app/shared

CMD ["python", "-m", "src.main"]
