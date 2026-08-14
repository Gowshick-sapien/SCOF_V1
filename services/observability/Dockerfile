FROM python:3.12-slim

WORKDIR /app

COPY services/observability/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared models and code
COPY shared/ ./shared/
RUN pip install -e ./shared

COPY services/observability/src ./src

ENV PYTHONPATH=/app
ENV PORT=8030

CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT}
