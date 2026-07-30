import logging
from typing import Any, Dict
from services.etl.src.config import config
from services.etl.src.extract import DataExtractor
from services.etl.src.transform import DataTransformer
from services.etl.src.load_graph import GraphLoader
from services.etl.src.load_vector import VectorLoader
from services.etl.src.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class ETLPipeline:
    """
    Orchestrates the 5-step ETL pipeline:
    1. Extract (D1 PostgreSQL & Profile)
    2. Transform (Graph Payloads & Vector Objects)
    3. Load Graph (Neo4j Cypher UNWIND MERGE)
    4. Load Vector (PostgreSQL Decision & Evidence Tables)
    5. Generate Embeddings (Standalone EmbeddingService -> PostgreSQL pgvector)
    """

    def __init__(self, mode: str = "full"):
        self.mode = mode
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.graph_loader = GraphLoader()
        self.vector_loader = VectorLoader()
        self.embedding_service = EmbeddingService(
            model_name=config.embedding_model,
            dimension=config.embedding_dimension
        )

    def run(self) -> Dict[str, Any]:
        logger.info("Starting D2 ETL Pipeline Execution (mode: %s)...", self.mode)

        # 1. Extract
        logger.info("[1/5] Extracting operational data from PostgreSQL D1 tables...")
        raw_data = self.extractor.extract_all()

        # 2. Transform
        logger.info("[2/5] Transforming relational data into graph payloads & vector objects...")
        graph_payload = self.transformer.transform_graph_payloads(raw_data)
        vector_payload = self.transformer.transform_vector_payloads(raw_data)

        # 3. Load Graph
        logger.info("[3/5] Ingesting nodes and explicit edge properties into Neo4j...")
        self.graph_loader.load_all(graph_payload)

        # 4. Generate Embeddings via Standalone Service
        logger.info("[4/5] Computing vector embeddings via standalone EmbeddingService (%s, dim=%d)...",
                    self.embedding_service.model_name, self.embedding_service.dimension)
        embedding_items = vector_payload.get("embedding_items", [])
        for item in embedding_items:
            item["embedding"] = self.embedding_service.generate_embedding(item["content_text"])
            item["embedding_model"] = self.embedding_service.model_name
            item["embedding_dimension"] = self.embedding_service.dimension
            item["embedding_version"] = config.embedding_version

        # 5. Load Vector Store
        logger.info("[5/5] Ingesting decision records, evidence snippets, and vector embeddings into PostgreSQL...")
        self.vector_loader.load_all(vector_payload)

        stats = {
            "mode": self.mode,
            "manufacturers": len(graph_payload.get("manufacturers", [])),
            "suppliers": len(graph_payload.get("suppliers", [])),
            "products": len(graph_payload.get("products", [])),
            "warehouses": len(graph_payload.get("warehouses", [])),
            "distribution_centers": len(graph_payload.get("distribution_centers", [])),
            "routes": len(graph_payload.get("routes", [])),
            "decisions": len(vector_payload.get("decisions", [])),
            "evidence_snippets": len(vector_payload.get("evidence_snippets", [])),
            "embeddings": len(embedding_items)
        }
        logger.info("D2 ETL Pipeline Execution Completed Successfully: %s", stats)
        return stats
