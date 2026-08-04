FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_DEFAULT_TIMEOUT=100

# Copy shared library and install it
COPY shared/ /app/shared/
RUN pip install --default-timeout=100 --no-cache-dir -e /app/shared

# Copy inventory agent package and install
COPY services/agents/inventory/ /app/services/agents/inventory/
RUN pip install --default-timeout=100 --no-cache-dir -e /app/services/agents/inventory/

# Expose HTTP port
EXPOSE 8012

ENV PYTHONPATH=/app/shared:/app/services/agents/inventory
ENV SCOF_PROFILE_PATH=/app/profiles/mvp-electronics

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8012"]
