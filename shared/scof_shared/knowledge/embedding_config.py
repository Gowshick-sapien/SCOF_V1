from pathlib import Path
from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field, field_validator
import yaml

class ModelSpec(BaseModel):
    provider: Literal["sentence-transformers", "mock"]
    model_name: str
    dimension: int = Field(384, description="Strictly frozen to 384 for Deliverable D02")
    distance_metric: Literal["cosine"] = "cosine"
    model_version: str = "1.0.0"
    normalize_embeddings: bool = True
    batch_size: int = Field(32, ge=1, le=256)
    device: str = "cpu"
    is_active: bool = True

    @field_validator("dimension")
    @classmethod
    def validate_dimension(cls, v: int) -> int:
        if v != 384:
            raise ValueError(f"D02 embedding space is strictly frozen to 384 dimensions; received {v}")
        return v

class EmbeddingSystemConfig(BaseModel):
    version: str = "2.1.0"
    active_model_id: str
    models: Dict[str, ModelSpec]
    similarity_threshold: float = 0.50
    max_top_k: int = 20

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "EmbeddingSystemConfig":
        if config_path is None:
            config_path = Path(__file__).resolve().parent.parent / "config" / "embedding.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Embedding configuration not found at {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        cfg = cls(**data)
        if cfg.active_model_id not in cfg.models:
            raise KeyError(f"Active model '{cfg.active_model_id}' is not registered in models dictionary")
        return cfg
