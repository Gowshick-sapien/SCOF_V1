import json
import tempfile
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Literal, Dict, List
from pydantic import BaseModel
from services.consensus.src.config import logger

class OutcomeRecord(BaseModel):
    outcome_id: str
    was_correct: bool
    source: Literal["human_adjudication", "realized_simulation_outcome", "validated_operational_outcome", "calibration_ground_truth"]
    timestamp: datetime

class AgentAccuracyState(BaseModel):
    agent_id: str
    outcomes: List[OutcomeRecord] = []

class AccuracyTrackerStore(BaseModel):
    agents: Dict[str, AgentAccuracyState] = {}

class AccuracyTracker:
    def __init__(self, store_path: Path, window_size: int, default_accuracy: float):
        self.store_path = store_path
        self.window_size = window_size
        self.default_accuracy = default_accuracy
        self._ensure_initialized()

    def _ensure_initialized(self):
        if not self.store_path.exists():
            self._write_store(AccuracyTrackerStore())

    def _read_store(self) -> AccuracyTrackerStore:
        try:
            with open(self.store_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AccuracyTrackerStore(**data)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to read accuracy store at {self.store_path}: {e}. Falling back to empty state.")
            return AccuracyTrackerStore()

    def _write_store(self, store: AccuracyTrackerStore):
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic write using temp file
        fd, temp_path = tempfile.mkstemp(dir=self.store_path.parent, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(store.model_dump_json(indent=2))
            # Rename is atomic on POSIX, and roughly atomic enough on Windows with replace
            os.replace(temp_path, self.store_path)
        except Exception as e:
            logger.error(f"Failed to atomically write accuracy store: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def get_accuracy(self, agent_id: str) -> float:
        store = self._read_store()
        agent_state = store.agents.get(agent_id)
        if not agent_state or not agent_state.outcomes:
            return self.default_accuracy
        
        # Calculate accuracy over the window
        correct_count = sum(1 for o in agent_state.outcomes if o.was_correct)
        return float(correct_count) / len(agent_state.outcomes)

    def record_outcome(self, agent_id: str, outcome_id: str, was_correct: bool, source: Literal["human_adjudication", "realized_simulation_outcome", "validated_operational_outcome", "calibration_ground_truth"], timestamp: datetime):
        store = self._read_store()
        
        if agent_id not in store.agents:
            store.agents[agent_id] = AgentAccuracyState(agent_id=agent_id)
            
        record = OutcomeRecord(
            outcome_id=outcome_id,
            was_correct=was_correct,
            source=source,
            timestamp=timestamp
        )
        
        store.agents[agent_id].outcomes.append(record)
        
        # Enforce window size
        if len(store.agents[agent_id].outcomes) > self.window_size:
            # Keep only the latest `window_size` items (they are appended to the end)
            store.agents[agent_id].outcomes = store.agents[agent_id].outcomes[-self.window_size:]
            
        self._write_store(store)
