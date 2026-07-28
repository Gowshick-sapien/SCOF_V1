"""Configuration management for SCOF Simulation Service."""

import os
from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "scof")
    postgres_user: str = os.getenv("POSTGRES_USER", "scof")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "changeme")

    random_seed: int = int(os.getenv("RANDOM_SEED", "42"))
    history_days: int = int(os.getenv("HISTORY_DAYS", "180"))
    profile_path: Path = Path(os.getenv("SCOF_PROFILE_PATH", "./profiles/mvp-electronics"))

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Config()
