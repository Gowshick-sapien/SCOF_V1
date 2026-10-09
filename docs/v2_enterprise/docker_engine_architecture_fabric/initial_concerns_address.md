Yes. **The Docker requirement is still preserved by the current architecture — but there is a gap in the V2 refinement we have been doing.**

The existing documents already make Docker a first-class deployment constraint:

- D1 explicitly provisions PostgreSQL, Redis, Kafka/RabbitMQ and Neo4j as standalone containers. srs
- The architecture already defines a Docker Compose service map containing the databases, Kafka, FastAPI, agents, and UI. architecture
- The repository structure already has `infrastructure/docker/`, Docker Compose files, database initialization, Kafka configuration, and setup scripts. repository_structure
- The V2 architecture still describes Docker as the deployment environment and retains the four-specialist architecture. scof_v2_architecture_evolution

**However:** our newer specialist-agent design — LangChain + Qwen/Ollama + RAG + analytical capabilities + MCP + A2A + Twin + CD²F — has been specified mostly at the **logical architecture level**, not yet as an explicit **container/deployment layer**.

That should be fixed now.

And importantly, this does **not** require changing the core architecture.

The correct principle is:

> **Docker contains the architectural services; it does not redefine the architecture.**

So I would add the following as the Docker/deployment layer around the frozen core engine.

# SCOF — Core Engine Docker Deployment Layer

## 1. Purpose

SCOF shall remain a **containerized platform from D1 onward**.

Docker is the deployment and isolation layer surrounding the SCOF core engine. It does not alter the logical architecture, agent responsibilities, A2A/MCP contracts, LangGraph orchestration, CD²F arbitration, Digital Twin, or knowledge-layer boundaries.

The architecture therefore has two distinct views:

```text
LOGICAL ARCHITECTURE
    What each SCOF component does

DEPLOYMENT ARCHITECTURE
    Where each deployable component runs
```

These must not be conflated.

A Python module does not automatically become a container. A container boundary exists where an independently deployable, independently restartable, or independently resource-controlled service is required.

---

# 2. Docker Deployment Principle

The SCOF runtime shall be deployed as a **Docker Compose service fleet** for the MVP.

```text
                    SCOF DOCKER ENVIRONMENT
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  CONTROL / COGNITIVE SERVICES                                       │
│                                                                      │
│   ┌───────────────┐       ┌─────────────────────┐                   │
│   │ API / Gateway │──────▶│ Coordinator /       │                   │
│   │   Container   │       │ LangGraph Runtime   │                   │
│   └───────────────┘       └──────────┬──────────┘                   │
│                                      │                               │
│                         ┌────────────┼────────────┐                  │
│                         │            │            │                  │
│                         ▼            ▼            ▼                  │
│                    Specialist   Specialist   Specialist ...          │
│                     Agent          Agent        Agent                │
│                    Containers     Containers   Containers            │
│                                                                      │
│   ┌──────────────────┐       ┌─────────────────────┐                │
│   │ Digital Twin     │       │ Capability / MCP    │                │
│   │ Service          │       │ Access Layer        │                │
│   └──────────────────┘       └─────────────────────┘                │
│                                                                      │
│  MODEL / KNOWLEDGE / EVENT SERVICES                                 │
│                                                                      │
│   ┌─────────┐ ┌─────────┐ ┌────────┐ ┌─────────┐ ┌──────────────┐   │
│   │Postgres │ │ Neo4j   │ │ Redis  │ │ Kafka   │ │ Ollama       │   │
│   │+pgvector│ │         │ │        │ │         │ │ Qwen 2.5 3B │   │
│   └─────────┘ └─────────┘ └────────┘ └─────────┘ └──────────────┘   │
│                                                                      │
│  OBSERVABILITY / SUPPORT                                             │
│   ┌────────────────┐  ┌─────────────────┐                           │
│   │ Trace / Logs   │  │ Profile / Config │                           │
│   └────────────────┘  └─────────────────┘                           │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

# 3. Container Boundary Rules

SCOF shall follow these rules:

### Rule 1 — One container per independently deployable service

Examples:

- Coordinator runtime
- Demand Agent
- Inventory Agent
- Supplier Agent
- Transportation Agent
- Digital Twin Service
- API service
- Ollama model service

### Rule 2 — Do not containerize every internal Python module

The following are normally **libraries/components inside their owning service**, not separate containers:

```text
LangChain
Prompt Policy
RAG orchestration
Evidence Fusion
Structured Claim Builder
CD²F implementation
Capability client
A2A client
MCP client
Domain reasoning logic
```

Creating a container for every one of these would unnecessarily turn the MVP into a distributed system of tiny services.

### Rule 3 — Stateful infrastructure remains independently containerized

```text
PostgreSQL + pgvector
Neo4j
Redis
Kafka
```

These already have independent persistence and lifecycle requirements.

### Rule 4 — The model runtime is independently containerized

Ollama is a runtime service.

The Qwen model is loaded by Ollama.

The specialist agent does **not** embed the model directly into its Python container.

---

# 4. Core Cognitive Engine Containers

## 4.1 Coordinator / Orchestration Container

```text
scof-coordinator
```

Responsibilities:

- LangGraph orchestration
- Deliberation management
- agent discovery
- A2A delegation
- parallel fan-out/fan-in
- claim collection
- deliberation readiness
- invoking downstream Twin/CD²F workflow
- workflow state management
- resolution lifecycle coordination

It communicates with specialists through A2A.

It must **not** directly reach into specialist internal databases or Python modules.

```text
Coordinator
     │
     ├── A2A → Demand Agent
     ├── A2A → Inventory Agent
     ├── A2A → Supplier Agent
     └── A2A → Transportation Agent
```

---

# 5. Specialist Agent Containers

Each specialist remains an independently deployable service.

```text
scof-agent-demand
scof-agent-inventory
scof-agent-supplier
scof-agent-transportation
```

Each container contains the complete cognitive runtime for its domain:

```text
┌─────────────────────────────────────────────┐
│           SPECIALIST AGENT CONTAINER        │
│                                             │
│  Domain Prompt Policy                       │
│          │                                  │
│          ▼                                  │
│  LangChain Cognitive Runtime                │
│          │                                  │
│          ▼                                  │
│  Qwen 2.5 3B via Ollama                    │
│          │                                  │
│  ┌───────┼──────────┬──────────────┐       │
│  ▼       ▼          ▼              ▼       │
│ RAG    Current     Analytical     Graph    │
│        Facts       Capabilities   Queries  │
│  │       │          │              │       │
│  └───────┴──────────┴──────────────┘       │
│              │                              │
│              ▼                              │
│        Evidence Fusion                      │
│              │                              │
│              ▼                              │
│       Structured Claim                      │
│              │                              │
│              ▼                              │
│             A2A                             │
└─────────────────────────────────────────────┘
```

The container therefore encapsulates the **specialist**, not merely its predictive model.

---

# 6. Ollama / LLM Container

```text
scof-llm
```

This container provides the local model runtime.

```text
Ollama
   │
   └── Qwen 2.5 3B
```

The specialist agents communicate with it over the Docker network:

```text
Demand Agent ─────┐
Inventory Agent ──┤
Supplier Agent ───┼──▶ Ollama ──▶ Qwen 2.5 3B
Transport Agent ──┘
```

The specialist agent owns:

- prompt policy
- context construction
- LangChain runtime
- retrieval policy
- evidence fusion
- reasoning protocol
- structured output validation

Ollama owns:

- model serving
- model loading
- inference execution

This is important because **Qwen is a shared inference capability, not four separate models embedded inside four agent images.**

A model volume should be persistent:

```text
ollama_models:/root/.ollama
```

so that container recreation does not require downloading the model again.

---

# 7. Analytical Model Layer

Analytical models must remain separate conceptually from the LLM.

They may initially execute **inside the specialist container** if their computational footprint is modest.

For example:

```text
Demand Agent
 ├── XGBoost
 ├── Prophet
 └── Chronos capability
```

The cognitive runtime does not hardcode:

```python
xgboost.predict(...)
```

Instead it invokes a registered capability:

```text
forecast_demand(...)
```

The capability registry resolves the implementation.

Therefore:

```text
                 Capability Contract
                       │
                       ▼
             forecast_demand(...)
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          XGBoost    Prophet   Chronos
```

The initial MVP may package these implementations within the relevant agent image.

If a model later requires independent GPU scaling or a separate serving runtime, it can become a separate container without changing the agent contract.

---

# 8. RAG / Semantic Memory

RAG does **not** require a separate vector database container.

SCOF already uses:

```text
PostgreSQL
     +
pgvector
```

Therefore:

```text
Specialist Agent
      │
      ▼
RAG Capability
      │
      ▼
PostgreSQL + pgvector
```

The agent decides whether historical retrieval is useful according to its domain retrieval policy.

The Coordinator does not decide:

> "Use RAG now."

The Coordinator delegates the deliberation.

The specialist's cognitive runtime determines whether historical evidence is required.

---

# 9. Current Operational Knowledge

Current facts remain outside RAG.

```text
Specialist Agent
      │
      ├── Current transactional fact
      │        ↓
      │    PostgreSQL
      │
      ├── Current topology
      │        ↓
      │      Neo4j
      │
      ├── Historical precedent
      │        ↓
      │   pgvector / RAG
      │
      └── Derived analytical result
               ↓
        Registered Capability
```

MCP remains the bounded access mechanism.

The Docker layer must never collapse these data boundaries merely because all services happen to run on the same Docker network.

---

# 10. Digital Twin Container

```text
scof-twin
```

The Digital Twin receives isolated scenario requests and owns the counterfactual simulation execution.

```text
Coordinator
     │
     ▼
Digital Twin Service
     │
     ├── Scenario A
     ├── Scenario B
     └── Scenario C
```

The Twin must maintain the V2 state isolation boundary:

```text
Layer 1 — Frozen Ground Truth
        │
        ▼
Layer 2 — Baseline Operational State
        │
        ▼
Layer 3 — Ephemeral Scenario Runtime
```

The Twin must never mutate the frozen reference dataset.

Its scenario runtime is disposable/isolated.

This is a **service boundary**, not merely a Python class, because the Twin has a distinct state lifecycle and resource profile.

---

# 11. CD²F Decision Engine

The final CD²F contract remains unchanged.

For the MVP, CD²F should **not automatically become another network service merely because it is architecturally important**.

It may be packaged as a library inside the Coordinator / decision runtime:

```text
scof-coordinator
    │
    ├── LangGraph
    ├── Deliberation
    ├── CD²F
    └── execution policy
```

This avoids unnecessary network hops.

The logical architecture still treats CD²F as its own decision-engine boundary.

The Docker boundary is simply:

```text
LOGICAL:
Coordinator → CD²F

DEPLOYMENT:
Coordinator Container
        └── CD²F Runtime
```

If future load or deployment requirements justify independent CD²F scaling, it can be extracted later because its contract is already frozen.

---

# 12. API Container

```text
scof-api
```

Responsibilities:

- REST endpoints
- scenario trigger
- what-if requests
- decision retrieval
- trace retrieval
- dashboard state
- WebSocket connections
- operator/HITL interaction

The API does not implement specialist reasoning.

```text
Client
  │
  ▼
API Container
  │
  ▼
Coordinator
```

This keeps the external interface separate from orchestration.

---

# 13. Event Backbone

Kafka remains independently containerized:

```text
scof-kafka
```

Primary role:

```text
Enterprise / Simulation Event
          │
          ▼
        Kafka
          │
          ▼
     Coordinator
          │
          ▼
   Deliberation workflow
```

Examples:

```text
demand_signal
inventory_alert
supplier_disruption
transport_disruption
domain_issue
deliberation_update
claim_submitted
decision_created
resolution_updated
```

Kafka is the asynchronous event backbone.

It should not become the storage location for authoritative business state.

---

# 14. Redis Container

```text
scof-redis
```

Redis remains for ephemeral/runtime state such as:

- short-lived coordination state
- caching
- locks where required
- transient worker state
- WebSocket/session support
- bounded runtime coordination

It must not replace PostgreSQL as the system of record.

---

# 15. PostgreSQL + pgvector Container

```text
scof-postgres
```

Owns:

```text
Operational facts
Decision records
Evidence metadata
Semantic-memory records
Embeddings
Audit metadata
Configuration/runtime metadata where appropriate
```

Persistent volume:

```text
pgdata:/var/lib/postgresql/data
```

---

# 16. Neo4j Container

```text
scof-neo4j
```

Owns the materialized topology projection.

Persistent volume:

```text
neo4jdata:/data
```

Specialists access it through bounded MCP capabilities rather than arbitrary direct graph access.

---

# 17. Domain Profile Mount

The Domain Profile remains configuration, not application code.

Example:

```text
profiles/
    scof-retail-reference/
        profile.yaml
        topology.yaml
        agents.yaml
        disruptions.yaml
        consensus.yaml
        evaluation.yaml
        dashboard.yaml
        data_bindings.yaml
```

The Docker environment mounts it read-only:

```yaml
volumes:
  - ./profiles:/profiles:ro
```

Services receive:

```text
SCOF_PROFILE_PATH=/profiles/scof-retail-reference
```

This preserves the profile-driven architecture.

---

# 18. Recommended MVP Compose Fleet

The Docker Compose deployment should therefore conceptually contain:

```text
┌─────────────────────────────────────────────────────────────┐
│                    SCOF APPLICATION                         │
│                                                             │
│  scof-api                                                   │
│      │                                                      │
│      ▼                                                      │
│  scof-coordinator                                           │
│      │                                                      │
│      ├──── A2A ──── scof-agent-demand                       │
│      ├──── A2A ──── scof-agent-inventory                    │
│      ├──── A2A ──── scof-agent-supplier                     │
│      └──── A2A ──── scof-agent-transportation               │
│                                                             │
│  scof-twin                                                  │
│                                                             │
│  scof-llm                                                   │
│      └──── Qwen 2.5 3B                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE                              │
│                                                             │
│  scof-postgres (+ pgvector)                                │
│  scof-neo4j                                                 │
│  scof-redis                                                 │
│  scof-kafka                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

The desktop application remains outside the server-side core-engine containers when packaged as a native Tauri application.

During development, its Vite development server may also run as a container, consistent with the existing deployment architecture.

---

# 19. Development vs Production Docker Boundaries

The same logical services shall support two modes.

### Development

```text
docker-compose.yml
+
docker-compose.override.yml
```

Development overrides may provide:

- source-code mounts
- hot reload
- debug ports
- development logging
- local profile mounting
- test model configuration

### MVP Runtime

Use built immutable images:

```text
scof-api:<version>
scof-coordinator:<version>
scof-agent-demand:<version>
scof-agent-inventory:<version>
scof-agent-supplier:<version>
scof-agent-transportation:<version>
scof-twin:<version>
```

Infrastructure images remain version-pinned.

---

# 20. Image Ownership

Each application service shall have its own Dockerfile where independent deployment is required.

Example:

```text
services/
    api/
        Dockerfile

    coordinator/
        Dockerfile

    agents/
        demand/
            Dockerfile
        inventory/
            Dockerfile
        supplier/
            Dockerfile
        transportation/
            Dockerfile

    twin/
        Dockerfile
```

Shared Python libraries should not require their own containers.

They should be packaged into the relevant application images.

---

# 21. Container Networking

All server-side services communicate over a private Docker network.

Example:

```text
scof-net
```

Internal service discovery uses Docker service names:

```text
postgres
neo4j
redis
kafka
ollama
coordinator
agent-demand
agent-inventory
agent-supplier
agent-transport
twin
api
```

External exposure should be minimized.

Only required entry points are published to the host:

```text
API
Desktop development UI
Neo4j browser (development only)
```

Internal agent, database, Kafka, Redis, and Ollama ports should not be unnecessarily exposed to the host.

---

# 22. Persistence Rules

Docker volumes must correspond to actual durable state.

```text
pgdata
neo4jdata
redisdata       # only if persistence is required
kafkadata
ollama_models
```

The following must remain disposable:

```text
agent containers
coordinator container
API container
Twin runtime container
temporary scenario workers
```

Most importantly:

```text
Layer 1 Frozen Dataset
        ≠
Docker writable volume
```

The frozen benchmark/reference dataset must remain immutable.

---

# 23. Health and Startup Dependencies

Docker Compose health checks should establish readiness rather than relying only on container startup order.

Conceptually:

```text
Postgres ───────┐
Neo4j ──────────┤
Redis ──────────┤
Kafka ──────────┼──▶ Core Services Ready
Ollama ─────────┘
                       │
                       ▼
                Coordinator Ready
                       │
                       ▼
                Specialist Agents
                       │
                       ▼
                    API Ready
```

An agent should not report `READY` merely because its Python process started.

It should verify that its required dependencies are reachable.

---

# 24. Model Lifecycle

The Qwen model is infrastructure, not application state.

Startup sequence:

```text
Ollama container starts
        │
        ▼
Model volume available
        │
        ▼
Qwen 2.5 3B available
        │
        ▼
Specialist agents become READY
```

Model version/configuration must be recorded with the agent execution metadata so that decisions can later be evaluated against:

```text
agent version
model name/version
prompt policy version
RAG policy/version
analytical capability version
profile version
```

This is required for reproducibility and D10 evaluation.

---

# 25. Security Boundary

The Docker layer must enforce least privilege.

A specialist agent should not receive:

```text
arbitrary PostgreSQL credentials
arbitrary Neo4j credentials
arbitrary Kafka administration access
arbitrary filesystem access
```

Instead:

```text
Specialist
    │
    ▼
Bounded MCP / Capability
    │
    ▼
Authorized data/service
```

The container boundary therefore complements, but does not replace, the MCP capability boundary.

---

# 26. What Docker Does NOT Change

The following remain exactly as architecturally defined:

```text
PostgreSQL        → System of Record
Neo4j             → Topology Projection
pgvector          → Semantic Memory
Redis             → Ephemeral State / Cache
Kafka             → Event Backbone

Specialist Agent  → Domain Observer + Domain Reasoner
Coordinator       → Orchestration
LangGraph         → Cross-Agent Workflow
LangChain         → Specialist Cognitive Runtime
Qwen              → Cognitive LLM
MCP               → Bounded Capability/Data Access
A2A               → Agent Interoperability
Digital Twin      → Counterfactual Simulation
CD²F              → Decision Arbitration
HITL              → Execution Governance
```

Docker simply provides the runtime isolation around these components.

---

# 27. Final Deployment Principle

The final SCOF architecture should therefore be understood as:

```text
                    SCOF LOGICAL ENGINE
┌──────────────────────────────────────────────────────┐
│                                                      │
│  Specialist Cognition                                │
│  Coordinator / LangGraph                             │
│  Deliberation                                        │
│  Digital Twin                                        │
│  CD²F                                                 │
│                                                      │
└──────────────────────────────────────────────────────┘
                         │
                         │ deployed as
                         ▼
                    DOCKER LAYER
┌──────────────────────────────────────────────────────┐
│                                                      │
│  API Container                                       │
│  Coordinator Container                               │
│  Specialist Agent Containers                         │
│  Twin Container                                      │
│  Ollama Container                                    │
│                                                      │
│  PostgreSQL / pgvector Container                     │
│  Neo4j Container                                     │
│  Redis Container                                     │
│  Kafka Container                                     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**The Docker layer is therefore a deployment realization of the existing architecture, not another cognitive layer.**

## Architectural decision

**GO — add this Docker deployment layer to the implementation specification.**

Do **not** redesign the core engine around Docker.

The important correction is simply that every major V2 deployable runtime now has an explicit container boundary, while internal mechanisms such as LangChain, prompt policy, RAG orchestration, Evidence Fusion, Structured Claim Builder, and CD²F remain inside their owning service rather than becoming unnecessary microservices.

### My final assessment

So the answer to your first question is:

**Yes, the project has obeyed the Docker requirement from V1 onward.** D1, the SRS, architecture, and repository structure all explicitly support it. 

**But our latest V2 core-engine refinement was missing the deployment mapping.** That is the gap worth closing.

And I would **freeze the above as the Docker/deployment layer** rather than introducing any more containers.

The most important architectural choice here is actually the negative one:

> **Do not make every logical component a microservice.**

`Prompt Policy`, `LangChain`, `RAG`, `Evidence Fusion`, `Claim Builder`, and `CD²F` are logical components. The **Coordinator, specialist agents, Twin, API, and infrastructure dependencies** are the meaningful deployment boundaries.

That keeps SCOF both **container-native** and **architecturally sane**.