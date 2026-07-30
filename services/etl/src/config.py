import os
from pydantic import BaseModel

class ETLConfig(BaseModel):
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "scof")
    postgres_user: str = os.getenv("POSTGRES_USER", "scof")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "changeme")

    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "changeme")

    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    embedding_version: str = os.getenv("EMBEDDING_VERSION", "v1")

    profile_path: str = os.getenv("PROFILE_PATH", "profiles/mvp-electronics")
    batch_size: int = int(os.getenv("ETL_BATCH_SIZE", "100"))

    @property
    def postgres_connection_string(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

config = ETLConfig()
