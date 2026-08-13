import os
import logging
from pathlib import Path

ENGINE_VERSION = "1.0.0"

SCOF_PROFILE_PATH = Path(os.getenv("SCOF_PROFILE_PATH", "profiles/mvp-electronics"))
ACCURACY_STORE_PATH = Path(os.getenv("ACCURACY_STORE_PATH", "data/accuracy_tracker.json"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("cd2f_engine")
