FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_RETRIES=10
ENV PIP_PREFER_BINARY=1

RUN pip install --upgrade pip setuptools wheel

# Copy shared library and install it
COPY shared/ /app/shared/
RUN pip install -e /app/shared

# Copy demand agent package and install
COPY services/agents/demand/ /app/services/agents/demand/
RUN pip install -e /app/services/agents/demand/

# Expose HTTP port
EXPOSE 8011

ENV PYTHONPATH=/app/shared:/app/services/agents/demand
ENV SCOF_PROFILE_PATH=/app/profiles/mvp-electronics

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8011"]
