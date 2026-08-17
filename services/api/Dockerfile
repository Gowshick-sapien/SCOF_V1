FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_RETRIES=10
ENV PIP_PREFER_BINARY=1

# Install shared library
COPY shared /app/shared
RUN pip install -e /app/shared

# Install api service
COPY services/api /app/services/api
RUN pip install -e /app/services/api

# Copy profile configurations
COPY profiles /app/profiles

ENV SCOF_PROFILE_PATH=/app/profiles/mvp-electronics
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
