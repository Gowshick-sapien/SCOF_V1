FROM python:3.11-slim

WORKDIR /app

COPY shared/ /app/shared/
RUN pip install -e /app/shared

COPY services/consensus/ /app/services/consensus/
RUN pip install -e /app/services/consensus

EXPOSE 8020
CMD ["uvicorn", "services.consensus.src.main:app", "--host", "0.0.0.0", "--port", "8020"]
