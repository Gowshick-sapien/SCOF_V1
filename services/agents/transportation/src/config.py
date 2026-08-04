"""Configuration settings for Transportation Agent."""

import os
from typing import Dict, List
from pydantic import BaseModel, Field


class TransportAgentConfig(BaseModel):
    """Runtime configuration for Transportation Agent."""

    agent_id: str = "transport-agent"
    name: str = "Transportation Agent"
    version: str = "1.0.0"
    host: str = Field(default_factory=lambda: os.getenv("TRANSPORT_AGENT_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("TRANSPORT_AGENT_PORT", "8014")))
    seed: int = Field(default_factory=lambda: int(os.getenv("SCOF_RANDOM_SEED", "42")))

    # Confidence calculation thresholds
    confidence_floor: float = 0.55
    confidence_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "agreement": 0.40,
            "interval": 0.30,
            "historical": 0.30,
        }
    )

    # Ensemble model weights
    ensemble_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "delay_predictor": 0.65,
            "route_scorer": 0.35,
        }
    )

    # Database settings
    db_host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    db_name: str = Field(default_factory=lambda: os.getenv("DB_NAME", "scof_db"))
    db_user: str = Field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    db_password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", "postgres"))

    # Neo4j settings
    neo4j_uri: str = Field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    neo4j_user: str = Field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    neo4j_password: str = Field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "scofpassword"))

    # Artifact storage
    model_dir: str = Field(
        default_factory=lambda: os.getenv("MODEL_DIR", os.path.join(os.getcwd(), "models", "transportation"))
    )

    # MCP tools
    mcp_tools: List[str] = Field(
        default_factory=lambda: [
            "get_route_details",
            "get_carrier_performance",
            "predict_shipment_delay",
            "recommend_alternate_route",
        ]
    )


def get_config() -> TransportAgentConfig:
    """Returns singleton config instance."""
    return TransportAgentConfig()
