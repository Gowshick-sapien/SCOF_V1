import os
import json
from typing import List

API_NAME = "scof-api"
API_VERSION = "1.0.0"

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "scof")
POSTGRES_USER = os.getenv("POSTGRES_USER", "scof")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KAFKA_CONSUMER_MAX_RETRIES = 3

COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://localhost:8010")
OBSERVABILITY_URL = os.getenv("OBSERVABILITY_URL", "http://localhost:8030")
EVALUATION_URL = os.getenv("EVALUATION_URL", "http://localhost:8040")

CORS_ORIGINS: List[str] = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))
SCOF_PROFILE_PATH = os.getenv("SCOF_PROFILE_PATH", "../../profiles/mvp-electronics")
