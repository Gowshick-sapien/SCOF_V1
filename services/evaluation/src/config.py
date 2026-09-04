import os

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api:8000")
COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://coordinator:8010")
CONSENSUS_URL = os.getenv("CONSENSUS_URL", "http://consensus:8020")
OBSERVABILITY_URL = os.getenv("OBSERVABILITY_URL", "http://observability:8030")
EVALUATION_PORT = int(os.getenv("EVALUATION_PORT", "8040"))
CALIBRATION_DATASET_PATH = os.getenv("CALIBRATION_DATASET_PATH", "profiles/mvp-electronics/scenarios/calibration_set.json")
