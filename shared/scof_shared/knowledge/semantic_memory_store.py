import hashlib
import json
import logging
import os
import re
import unicodedata
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
import psycopg
from psycopg import sql
from scof_shared.knowledge.embedding_config import EmbeddingSystemConfig
from scof_shared.knowledge.embedding_provider import EmbeddingProvider, create_embedding_provider

logger = logging.getLogger(__name__)

def canonicalize_text(text: str) -> str:
    """
    Applies deterministic text normalization prior to hashing and embedding:
    1. Unicode NFC normalization.
    2. Newline canonicalization to '\\n'.
    3. Trimming lines and collapsing redundant horizontal whitespace.
    """
    if not text:
        return ""
    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.split("\n")]
    # Strip leading/trailing empty lines while preserving internal single linebreaks
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


class SemanticDocumentInput(BaseModel):
    document_type: Literal[
        "SCENARIO", "AGENT_EVIDENCE", "DECISION", 
        "CONSENSUS", "INCIDENT_REPORT", "CAPABILITY_CARD"
    ]
    title: Optional[str] = None
    content: str
    source_system: str = "SCOF"
    source_entity_type: Optional[str] = None
    source_entity_id: Optional[str] = None
    scenario_id: Optional[str] = None
    run_id: Optional[str] = None
    agent_id: Optional[str] = None
    logical_key: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class SemanticDocumentRecord(BaseModel):
    semantic_document_id: str
    document_type: str
    title: Optional[str]
    content: str
    content_hash: str
    source_system: str
    source_entity_type: Optional[str]
    source_entity_id: Optional[str]
    scenario_id: Optional[str]
    run_id: Optional[str]
    agent_id: Optional[str]
    metadata_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class SemanticSearchResult(BaseModel):
    semantic_document_id: str
    similarity_score: float
    document_type: str
    title: Optional[str]
    content: str
    source_entity_type: Optional[str]
    source_entity_id: Optional[str]
    scenario_id: Optional[str]
    run_id: Optional[str]
    agent_id: Optional[str]
    metadata_json: Dict[str, Any]


class SemanticMemoryStore:
    """
    Authoritative Deliverable D02 Semantic Memory Access Substrate.
    Guarantees isolation of vector operations, model versioning,
    transactional atomic writes, and named-parameter similarity search.
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        config: Optional[EmbeddingSystemConfig] = None,
        provider: Optional[EmbeddingProvider] = None
    ):
        if db_url is None:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                user = os.getenv("POSTGRES_USER")
                pw = os.getenv("POSTGRES_PASSWORD")
                host = os.getenv("POSTGRES_HOST", "localhost")
                port = os.getenv("POSTGRES_PORT", "5432")
                db = os.getenv("POSTGRES_DB", "scof")
                if not user or not pw:
                    raise ValueError(
                        "PostgreSQL credentials not configured. "
                        "Set DATABASE_URL or POSTGRES_USER and POSTGRES_PASSWORD environment variables."
                    )
                db_url = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
        self.db_url = db_url

        self.config = config or EmbeddingSystemConfig.load()
        active_spec = self.config.models[self.config.active_model_id]
        self.provider = provider or create_embedding_provider(active_spec, self.config.active_model_id)
        try:
            self.sync_active_model_registry()
        except Exception as e:
            logger.debug("Automatic model registry sync deferred: %s", e)

    def _get_connection(self) -> psycopg.Connection:
        return psycopg.connect(self.db_url, autocommit=False)

    @staticmethod
    def compute_content_hash(content: str) -> str:
        canonical = canonicalize_text(content)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def derive_document_id(doc: SemanticDocumentInput) -> str:
        """
        Derives stable, deterministic document identity from composite business keys.
        Crucially includes run_id to prevent multi-run state collisions.
        """
        parts = [
            doc.source_system,
            doc.document_type,
            doc.source_entity_type or "GENERIC",
            doc.source_entity_id or "NONE",
            doc.scenario_id or "BASE",
            doc.run_id or "GLOBAL",
            doc.agent_id or "SYSTEM",
            doc.logical_key or ""
        ]
        composite_key = ":".join(parts)
        key_hash = hashlib.sha256(composite_key.encode("utf-8")).hexdigest()[:12]
        return f"SD-{doc.document_type[:3]}-{key_hash}"

    def sync_active_model_registry(self) -> None:
        """Enforces fail-closed synchronization between config and database catalog."""
        spec = self.config.models[self.config.active_model_id]
        check_sql = "SELECT dimension, distance_metric FROM scof.embedding_model WHERE model_id = %(id)s;"
        upsert_sql = """
        INSERT INTO scof.embedding_model (
            model_id, provider, model_name, dimension, distance_metric, model_version, is_active
        ) VALUES (%(id)s, %(prov)s, %(name)s, %(dim)s, %(metric)s, %(ver)s, %(act)s)
        ON CONFLICT (model_id) DO UPDATE SET
            is_active = EXCLUDED.is_active;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(check_sql, {"id": self.config.active_model_id})
                existing = cur.fetchone()
                if existing:
                    db_dim, db_metric = existing
                    if db_dim != spec.dimension or db_metric != spec.distance_metric:
                        raise RuntimeError(
                            f"Model registry mismatch: DB has {db_dim}d/{db_metric}, "
                            f"config expects {spec.dimension}d/{spec.distance_metric}. Schema migration required."
                        )
                cur.execute(upsert_sql, {
                    "id": self.config.active_model_id,
                    "prov": spec.provider,
                    "name": spec.model_name,
                    "dim": spec.dimension,
                    "metric": spec.distance_metric,
                    "ver": spec.model_version,
                    "act": spec.is_active
                })
            conn.commit()

    def upsert_document(
        self,
        doc: SemanticDocumentInput,
        document_id: Optional[str] = None,
        auto_embed: bool = True
    ) -> SemanticDocumentRecord:
        """
        Transactionally inserts or updates a semantic document.
        When auto_embed=True, embedding generation and concurrency-safe versioning
        execute within the identical transaction, guaranteeing no orphan documents.
        """
        canonical_content = canonicalize_text(doc.content)
        content_hash = hashlib.sha256(canonical_content.encode("utf-8")).hexdigest()
        doc_id = document_id or self.derive_document_id(doc)

        check_sql = """
        SELECT content_hash FROM scof.semantic_document 
        WHERE semantic_document_id = %(id)s 
        FOR UPDATE;
        """
        upsert_doc_sql = """
        INSERT INTO scof.semantic_document (
            semantic_document_id, document_type, title, content, content_hash,
            source_system, source_entity_type, source_entity_id,
            scenario_id, run_id, agent_id, metadata_json, updated_at
        ) VALUES (
            %(id)s, %(type)s, %(title)s, %(content)s, %(hash)s,
            %(sys)s, %(ent_type)s, %(ent_id)s,
            %(scen)s, %(run)s, %(agent)s, %(meta)s, CURRENT_TIMESTAMP
        ) ON CONFLICT (semantic_document_id) DO UPDATE SET
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            content_hash = EXCLUDED.content_hash,
            metadata_json = EXCLUDED.metadata_json,
            updated_at = CURRENT_TIMESTAMP
        RETURNING semantic_document_id, document_type, title, content, content_hash,
                  source_system, source_entity_type, source_entity_id,
                  scenario_id, run_id, agent_id, metadata_json, created_at, updated_at;
        """

        with self._get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(check_sql, {"id": doc_id})
                    prior = cur.fetchone()
                    content_changed = (prior is None) or (prior[0] != content_hash)

                    cur.execute(upsert_doc_sql, {
                        "id": doc_id,
                        "type": doc.document_type,
                        "title": doc.title,
                        "content": canonical_content,
                        "hash": content_hash,
                        "sys": doc.source_system,
                        "ent_type": doc.source_entity_type,
                        "ent_id": doc.source_entity_id,
                        "scen": doc.scenario_id,
                        "run": doc.run_id,
                        "agent": doc.agent_id,
                        "meta": json.dumps(doc.metadata_json)
                    })
                    row = cur.fetchone()
                    if row is None:
                        raise RuntimeError(f"Upsert failed to return a record for document '{doc_id}'")
                    record = SemanticDocumentRecord(
                        semantic_document_id=row[0],
                        document_type=row[1],
                        title=row[2],
                        content=row[3],
                        content_hash=row[4],
                        source_system=row[5],
                        source_entity_type=row[6],
                        source_entity_id=row[7],
                        scenario_id=row[8],
                        run_id=row[9],
                        agent_id=row[10],
                        metadata_json=row[11],
                        created_at=row[12],
                        updated_at=row[13]
                    )

                    if auto_embed and content_changed:
                        self._atomic_embed_document(cur, doc_id, canonical_content, content_hash)

                conn.commit()
                return record
            except Exception:
                conn.rollback()
                raise

    def _atomic_embed_document(
        self,
        cur: psycopg.Cursor,
        semantic_document_id: str,
        content: str,
        content_hash: str
    ) -> str:
        """
        Concurrency-safe embedding creation within the active transaction.
        Acquires row-level locks on existing embedding versions to prevent race conditions.
        """
        vector = self.provider.embed_text(content)
        vector_str = f"[{','.join(str(x) for x in vector)}]"

        # Row-lock existing embeddings for this document and model to prevent concurrent version collision
        lock_sql = """
        SELECT embedding_version FROM scof.semantic_embedding 
        WHERE semantic_document_id = %(doc_id)s AND model_id = %(model_id)s 
        FOR UPDATE;
        """
        cur.execute(lock_sql, {
            "doc_id": semantic_document_id,
            "model_id": self.provider.model_id
        })
        existing_versions = [r[0] for r in cur.fetchall()]
        next_version = (max(existing_versions) + 1) if existing_versions else 1

        # Mark previous versions as historical
        deprecate_sql = """
        UPDATE scof.semantic_embedding 
        SET is_current = FALSE 
        WHERE semantic_document_id = %(doc_id)s AND model_id = %(model_id)s AND is_current = TRUE;
        """
        cur.execute(deprecate_sql, {
            "doc_id": semantic_document_id,
            "model_id": self.provider.model_id
        })

        # Insert new active version
        emb_id = f"EMB-{content_hash[:10]}-v{next_version}"
        insert_sql = """
        INSERT INTO scof.semantic_embedding (
            embedding_id, semantic_document_id, model_id, embedding_version, is_current, embedding, content_hash
        ) VALUES (
            %(emb_id)s, %(doc_id)s, %(model_id)s, %(ver)s, TRUE, %(vec)s::vector, %(hash)s
        );
        """
        cur.execute(insert_sql, {
            "emb_id": emb_id,
            "doc_id": semantic_document_id,
            "model_id": self.provider.model_id,
            "ver": next_version,
            "vec": vector_str,
            "hash": content_hash
        })
        return emb_id

    def similarity_search(
        self,
        query_text: str,
        *,
        model_id: Optional[str] = None,
        document_types: Optional[List[str]] = None,
        scenario_id: Optional[str] = None,
        run_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        source_entity_type: Optional[str] = None,
        min_similarity: float = 0.0,
        top_k: int = 5
    ) -> List[SemanticSearchResult]:
        """
        Executes exact cosine nearest-neighbor search using named parameters.
        Enforces model consistency between query vector generation and stored vector catalog.
        """
        target_model = model_id or self.provider.model_id
        if target_model != self.provider.model_id:
            if target_model not in self.config.models:
                raise KeyError(f"Requested model '{target_model}' is not registered in configuration.")
            target_spec = self.config.models[target_model]
            query_provider = create_embedding_provider(target_spec, target_model)
        else:
            query_provider = self.provider

        canonical_query = canonicalize_text(query_text)
        query_vector = query_provider.embed_text(canonical_query)
        query_str = f"[{','.join(str(x) for x in query_vector)}]"

        where_clauses = [
            sql.SQL("e.model_id = %(model_id)s"),
            sql.SQL("e.is_current = TRUE")
        ]
        sql_params: Dict[str, Any] = {
            "model_id": target_model,
            "query_vec": query_str,
            "min_sim": min_similarity,
            "limit_k": top_k
        }

        if document_types:
            where_clauses.append(sql.SQL("d.document_type = ANY(%(doc_types)s)"))
            sql_params["doc_types"] = document_types
        if scenario_id:
            where_clauses.append(sql.SQL("d.scenario_id = %(scen_id)s"))
            sql_params["scen_id"] = scenario_id
        if run_id:
            where_clauses.append(sql.SQL("d.run_id = %(run_id)s"))
            sql_params["run_id"] = run_id
        if agent_id:
            where_clauses.append(sql.SQL("d.agent_id = %(agent_id)s"))
            sql_params["agent_id"] = agent_id
        if source_entity_type:
            where_clauses.append(sql.SQL("d.source_entity_type = %(ent_type)s"))
            sql_params["ent_type"] = source_entity_type

        where_sql = sql.SQL(" AND ").join(where_clauses)

        # Named parameter SQL prevents any parameter ordering confusion
        query_sql = sql.SQL("""
        SELECT 
            d.semantic_document_id,
            1 - (e.embedding <=> %(query_vec)s::vector) AS similarity_score,
            d.document_type,
            d.title,
            d.content,
            d.source_entity_type,
            d.source_entity_id,
            d.scenario_id,
            d.run_id,
            d.agent_id,
            d.metadata_json
        FROM scof.semantic_embedding e
        JOIN scof.semantic_document d ON d.semantic_document_id = e.semantic_document_id
        WHERE {where_sql}
          AND 1 - (e.embedding <=> %(query_vec)s::vector) >= %(min_sim)s
        ORDER BY e.embedding <=> %(query_vec)s::vector
        LIMIT %(limit_k)s;
        """).format(where_sql=where_sql)
        results = []
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query_sql, sql_params)
                for row in cur.fetchall():
                    results.append(SemanticSearchResult(
                        semantic_document_id=row[0],
                        similarity_score=float(row[1]),
                        document_type=row[2],
                        title=row[3],
                        content=row[4],
                        source_entity_type=row[5],
                        source_entity_id=row[6],
                        scenario_id=row[7],
                        run_id=row[8],
                        agent_id=row[9],
                        metadata_json=row[10]
                    ))
        return results
