"""Configuration for Demand Agent Service."""

import os
from pathlib import Path

AGENT_ID = "demand-agent"
AGENT_NAME = "Demand Forecast Agent"
DEFAULT_PORT = 8011

# Environment / Data Connection Config
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "scof_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

SCOF_PROFILE_PATH = os.getenv(
    "SCOF_PROFILE_PATH",
    str(Path(__file__).resolve().parents[4] / "profiles" / "mvp-electronics"),
)

MODEL_ARTIFACT_DIR = Path(os.getenv("MODEL_ARTIFACT_DIR", "models/demand"))

# Deterministic Random Seeds
NUMPY_SEED = 42
XGBOOST_SEED = 42
PYTHON_RANDOM_SEED = 42
