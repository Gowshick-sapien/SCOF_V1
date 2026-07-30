-- Deliverable D2 PostgreSQL pgvector Schema Initialization Script (v2.0.0)
-- Creates scof.schema_version, scof.decision_records, scof.evidence_snippets, scof.embeddings, and indexes.

CREATE SCHEMA IF NOT EXISTS scof;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- 0. Schema Migration Versioning
CREATE TABLE IF NOT EXISTS scof.schema_version (
    version VARCHAR(50) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO scof.schema_version (version, description)
VALUES ('2.0.0', 'D2 Knowledge Layer vector store schema with decision metadata & embedding tracking')
ON CONFLICT (version) DO NOTHING;

-- 1. Decision Records Table
CREATE TABLE IF NOT EXISTS scof.decision_records (
    id VARCHAR(50) PRIMARY KEY,
    scenario_id VARCHAR(50) REFERENCES scof.scenarios(scenario_id) ON DELETE SET NULL,
    run_id VARCHAR(50) REFERENCES scof.simulation_runs(run_id) ON DELETE SET NULL,
    disruption_id VARCHAR(50) REFERENCES scof.disruption_events(id) ON DELETE SET NULL,
    decision_type VARCHAR(50) NOT NULL,
    recommendation TEXT NOT NULL,
    confidence NUMERIC(5,4) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    impact_summary TEXT,
    created_by VARCHAR(50) NOT NULL DEFAULT 'SYSTEM',
    simulation_tick INT DEFAULT 0,
    outcome VARCHAR(50) DEFAULT 'PENDING',
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Evidence Snippets Table
CREATE TABLE IF NOT EXISTS scof.evidence_snippets (
    id VARCHAR(50) PRIMARY KEY,
    decision_id VARCHAR(50) REFERENCES scof.decision_records(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    snippet_text TEXT NOT NULL,
    metadata_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Vector Embeddings Table
CREATE TABLE IF NOT EXISTS scof.embeddings (
    id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    content_text TEXT NOT NULL,
    embedding_model VARCHAR(100) NOT NULL DEFAULT 'all-MiniLM-L6-v2',
    embedding_version VARCHAR(50) NOT NULL DEFAULT 'v1',
    embedding_dimension INT NOT NULL DEFAULT 384,
    embedding vector(384) NOT NULL,
    metadata_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance & Vector Similarity Indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw 
ON scof.embeddings 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_embeddings_metadata 
ON scof.embeddings(entity_type, embedding_model, embedding_version);

CREATE INDEX IF NOT EXISTS idx_decisions_scenario 
ON scof.decision_records(scenario_id, decision_type, outcome);

CREATE INDEX IF NOT EXISTS idx_evidence_decision 
ON scof.evidence_snippets(decision_id);
