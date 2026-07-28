FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library and install it
COPY shared /app/shared
RUN pip install --no-cache-dir -e /app/shared

# Copy simulation service and install dependencies
COPY services/simulation /app/services/simulation
WORKDIR /app/services/simulation
RUN pip install --no-cache-dir -e .

ENV PYTHONPATH=/app/services/simulation:/app/shared

CMD ["python", "-m", "src.main"]
