FROM python:3.11-slim

WORKDIR /app

COPY shared/ /app/shared/
RUN pip install -e /app/shared

COPY services/evaluation/ /app/services/evaluation/
RUN pip install -e /app/services/evaluation

EXPOSE 8040
CMD ["uvicorn", "services.evaluation.src.main:app", "--host", "0.0.0.0", "--port", "8040"]
