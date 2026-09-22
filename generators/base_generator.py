"""
SCOF Base Generator Class
Provides standardized lifecycle, isolated RNG seeding, checkpointing hooks, and validation contracts.
"""

import os
import zlib
import hashlib
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseGenerator(ABC):
    def __init__(self, node_config: Dict[str, Any], context: Dict[str, Any]):
        self.node_config = node_config
        self.context = context
        self.node_id = node_config["generator_node"]
        self.name = node_config["name"]
        self.scheduling_tier = node_config["scheduling_tier"]
        self.storage_format = node_config["storage_format"]
        self.rng_namespace = node_config["rng_namespace"]
        self.cardinality_driver = node_config["cardinality_driver"]
        self.canonical_entities = node_config.get("canonical_entities", [])
        
        # Initialize isolated deterministic RNG stream
        self.rng = self._init_rng()

    def _init_rng(self) -> np.random.Generator:
        base_seed = self.context.get("rng_seed_base", 42)
        # Derive unique deterministic integer seed from namespace
        ns_hash = zlib.crc32(self.rng_namespace.encode("utf-8"))
        derived_seed = (base_seed + ns_hash) % (2**32)
        return np.random.default_rng(derived_seed)

    def get_rng(self) -> np.random.Generator:
        return self.rng

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """
        Executes generation logic.
        Must return a dictionary:
        {
            "status": "SUCCESS" | "FAILED",
            "row_count": int,
            "checksum": str,
            "output_files": List[str],
            "metrics": Dict[str, Any]
        }
        """
        pass

    def validate_output(self, result: Dict[str, Any]) -> bool:
        """
        Validates output invariants.
        Default checks: result must contain status == 'SUCCESS' and row_count >= 0.
        """
        if not isinstance(result, dict):
            return False
        if result.get("status") != "SUCCESS":
            return False
        if result.get("row_count", -1) < 0:
            return False
        return True

    def compute_file_checksum(self, filepath: str) -> str:
        """Computes SHA-256 checksum of an output artifact."""
        if not os.path.exists(filepath):
            return "FILE_NOT_FOUND"
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
