# Deliverable D02 -- PostgreSQL pgvector Semantic Memory Schema

## 1. Architectural Overview

The semantic memory substrate in Deliverable D02 provides qualitative and historical contextual retrieval for SCOF V2 cognitive agents. Implemented in PostgreSQL using the `pgvector` extension, it stores dense vector embeddings of historical disruption scenarios, agent evidence snippets, decision rationales, CD2F consensus arbitration transcripts, and dynamic agent capability cards.

### Core Architectural Invariants
1. **Three-Tier Decoupling**: Separate tables for models (`embedding_model`), text documents (`semantic_document`), and raw embeddings (`semantic_embedding`).
2. **Fixed Dimension Invariant**: Standardized 384-dimensional dense vectors using `sentence-transformers/all-MiniLM-L6-v2`.
3. **Relational Provenance**: 100% of operational memory documents must link to valid entity records in the relational System of Record.
4. **Non-Vectorization of Numbers**: Numerical stock levels, prices, and lead times are strictly excluded from embedding ([ADR 007b (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/007b_amendment_durable_semantic_memory_and_evidence_substrate.md)).
5. **Encapsulated Access**: All operations are mediated through [`SemanticMemoryStore`](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/semantic_memory_store.py).

---

## 2. Three-Tier Schema DDL Specification

```sql
-- Create Schema and Enable Vector Extension
CREATE SCHEMA IF NOT EXISTS scof;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Tier 1: Embedding Model Registry
CREATE TABLE IF NOT EXISTS scof.embedding_model (
    model_id VARCHAR(100) PRIMARY KEY,
    provider_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    dimension INT NOT NULL CHECK (dimension > 0),
    distance_metric VARCHAR(50) NOT NULL CHECK (distance_metric IN ('cosine', 'l2', 'inner_product')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tier 2: Canonical Semantic Documents
CREATE TABLE IF NOT EXISTS scof.semantic_document (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_type VARCHAR(50) NOT NULL CHECK (
        document_type IN (
            'DISRUPTION_SCENARIO',
            'AGENT_EVIDENCE',
            'DECISION_RECORD',
            'CONSENSUS_LOG',
            'CAPABILITY_CARD'
        )
    ),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    content_sha256 VARCHAR(64) NOT NULL,
    metadata_json JSONB DEFAULT '{}'::jsonb,
    source_entity_type VARCHAR(100), -- E.g. 'supplier', 'facility', 'transport_lane'
    source_entity_id VARCHAR(100),   -- E.g. 'SUP-0012', 'FAC-DC-01'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_document_sha UNIQUE (content_sha256)
);

-- Tier 3: Vector Embeddings
CREATE TABLE IF NOT EXISTS scof.semantic_embedding (
    embedding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES scof.semantic_document(document_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES scof.embedding_model(model_id),
    CONSTRAINT uq_doc_model UNIQUE (document_id, model_id)
);

-- Indexes for Fast Provenance and Metadata Filtering
CREATE INDEX IF NOT EXISTS idx_sem_doc_type ON scof.semantic_document(document_type);
CREATE INDEX IF NOT EXISTS idx_sem_doc_provenance ON scof.semantic_document(source_entity_type, source_entity_id);
CREATE INDEX IF NOT EXISTS idx_sem_emb_model ON scof.semantic_embedding(model_id);
```

---

## 3. Embedding Model Specifications & Metrics

| Specification Parameter | Value |
|---|---|
| **Active Model Identifier** | `minilm-l6-v2` |
| **Hugging Face Model Name** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Output Dimension** | `384` |
| **Distance Metric** | `Cosine Distance` (`<=>` operator in pgvector) |
| **Text Normalization** | Whitespace trimming, lowercased headers, deterministic punctuation stripping |
| **Idempotency Check** | SHA-256 hash of normalized text stored in `content_sha256` |

---

## 4. Similarity Search Query Template

High-speed cosine similarity retrieval template joining Tier 2 and Tier 3:

```sql
SELECT 
    d.document_id,
    d.document_type,
    d.title,
    d.content,
    d.metadata_json,
    d.source_entity_type,
    d.source_entity_id,
    (1 - (e.embedding <=> $1::vector)) AS similarity_score
FROM scof.semantic_embedding e
JOIN scof.semantic_document d ON e.document_id = d.document_id
WHERE e.model_id = $2
  AND ($3::text[] IS NULL OR d.document_type = ANY($3::text[]))
ORDER BY e.embedding <=> $1::vector ASC
LIMIT $4;
```

---

## 5. High-Level Python API (`SemanticMemoryStore`)

To prevent cognitive agents from executing raw SQL or directly handling database drivers ([ADR 007b (Amendment)](file:///d:/projects/SCOF_V1/SCOF/docs/adr/007b_amendment_durable_semantic_memory_and_evidence_substrate.md)), all memory operations are encapsulated in [`SemanticMemoryStore`](file:///d:/projects/SCOF_V1/SCOF/shared/scof_shared/knowledge/semantic_memory_store.py):

```python
from scof_shared.knowledge.semantic_memory_store import SemanticMemoryStore, SemanticDocumentInput

store = SemanticMemoryStore()

# 1. Insert Document with Relational Provenance
doc_id = store.insert_document(SemanticDocumentInput(
    document_type="DISRUPTION_SCENARIO",
    title="Chiller Malfunction at DC-01",
    content="Cold-chain temperature exceeded 4C in refrigeration zone B.",
    metadata={"affected_skus": ["SKU-000492"], "loss_estimate_usd": 14200.00},
    source_entity_type="facility",
    source_entity_id="FAC-DC-01"
))

# 2. Query Memory via Semantic Similarity
results = store.similarity_search(
    query_text="historical refrigeration unit temperature failures",
    document_types=["DISRUPTION_SCENARIO"],
    top_k=5
)

for item in results:
    print(f"[{item.score:.4f}] {item.title} (Source: {item.source_entity_id})")
```
