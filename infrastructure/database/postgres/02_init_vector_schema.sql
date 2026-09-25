-- Deliverable D02 PostgreSQL pgvector Schema Initialization Script (v2.1.0)
-- Establishing Durable Semantic-Memory & Evidence Substrate for Downstream Agents
-- Certified for 384-dimensional cosine similarity embeddings without premature HNSW.

CREATE SCHEMA IF NOT EXISTS scof;
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Embedding Model Registry (Immutable Model Identity name@version)
CREATE TABLE IF NOT EXISTS scof.embedding_model (
    model_id VARCHAR(120) PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    dimension INTEGER NOT NULL CHECK (dimension = 384),
    distance_metric VARCHAR(20) NOT NULL DEFAULT 'cosine',
    model_version VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Semantic Document Store (Identity & Provenance)
CREATE TABLE IF NOT EXISTS scof.semantic_document (
    semantic_document_id VARCHAR(64) PRIMARY KEY,
    document_type VARCHAR(50) NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    content_hash CHAR(64) NOT NULL,
    source_system VARCHAR(50) NOT NULL DEFAULT 'SCOF',
    source_entity_type VARCHAR(100),
    source_entity_id VARCHAR(100),
    scenario_id VARCHAR(64),
    run_id VARCHAR(64),
    agent_id VARCHAR(64),
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Semantic Vector Store (Embeddings with Versioning)
CREATE TABLE IF NOT EXISTS scof.semantic_embedding (
    embedding_id VARCHAR(64) PRIMARY KEY,
    semantic_document_id VARCHAR(64) NOT NULL REFERENCES scof.semantic_document(semantic_document_id) ON DELETE CASCADE,
    model_id VARCHAR(120) NOT NULL REFERENCES scof.embedding_model(model_id),
    embedding_version INTEGER NOT NULL DEFAULT 1,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    embedding vector(384) NOT NULL,
    content_hash CHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_doc_model_version UNIQUE (semantic_document_id, model_id, embedding_version)
);

-- 4. Bounded Lookup and Provenance Indexes
CREATE INDEX IF NOT EXISTS idx_sem_doc_hash 
    ON scof.semantic_document(content_hash);

CREATE INDEX IF NOT EXISTS idx_sem_doc_lookup 
    ON scof.semantic_document(document_type, scenario_id, run_id, agent_id);

CREATE INDEX IF NOT EXISTS idx_sem_doc_provenance 
    ON scof.semantic_document(source_entity_type, source_entity_id);

CREATE INDEX IF NOT EXISTS idx_sem_embedding_current 
    ON scof.semantic_embedding(semantic_document_id, model_id, is_current);
