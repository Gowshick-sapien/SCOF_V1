"""Configuration settings for SCOF Coordinator Service."""

import os
from pathlib import Path

COORDINATOR_ID = "coordinator-agent"
COORDINATOR_NAME = "Supply Chain Cognitive Coordinator"
COORDINATOR_VERSION = "1.0.0"
DEFAULT_PORT = 8010

SCOF_PROFILE_PATH = Path(os.getenv("SCOF_PROFILE_PATH", "profiles/mvp-electronics"))
CONNECT_TIMEOUT_SECONDS = float(os.getenv("CONNECT_TIMEOUT_SECONDS", "2.0"))
READ_TIMEOUT_SECONDS = float(os.getenv("READ_TIMEOUT_SECONDS", "8.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
MAX_CONCURRENT_DISPATCH = int(os.getenv("MAX_CONCURRENT_DISPATCH", "8"))
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() in ("true", "1")
