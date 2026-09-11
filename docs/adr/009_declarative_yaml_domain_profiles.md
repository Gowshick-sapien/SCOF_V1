# ADR 009: Domain Profile Architecture — Declarative YAML Profiles vs. Hardcoded Business Logic

---

## 1. Context and Problem Statement

Enterprise supply chains vary radically across industries:
* A **consumer electronics** supply chain prioritizes semiconductor lead times, component obsolescence, and air freight.
* A **pharmaceutical** supply chain requires strict cold-chain temperature monitoring, regulatory compliance batches, and shelf-life expiration tracking.
* An **automotive** supply chain operates on Just-in-Time (JIT) sequencing, assembly plant buffer hours, and rail transport.

If the multi-agent decision platform hardcodes entities, disruption types, escalation thresholds, or evaluation metrics into Python source code, adapting SCOF to a new client or industry requires costly software forks and regression testing.

---

## 2. Decision Drivers

* **Domain Agnosticism**: The core platform engine (LangGraph coordinator, CD²F arbitration, observability, API gateway, desktop console) must be 100% agnostic to any specific supply chain vertical.
* **Zero-Code Domain Deployment**: Deploying SCOF into a new supply chain environment must be achieved purely by writing declarative configuration files, with zero modifications to platform code.
* **Human-Readable Schema**: Configurations must be editable and reviewable by non-software supply chain domain analysts.

---

## 3. Considered Options

* **Option 1: Hardcoded Python Schemas**: Embedding network topologies and agent rules directly in Python classes.
* **Option 2: Relational Database Configuration Tables**: Storing all configurations in PostgreSQL tables.
* **Option 3: Declarative YAML Domain Profiles (`profiles/<profile-name>/`)**.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Declarative YAML Domain Profiles**

### Rationale:
The platform architecture enforces a strict decoupling contract:
$$\text{SCOF Core Engine (Unchanged)} + \text{Domain Profile (Per Deployment)} = \text{Running System}$$

Each Domain Profile directory contains 7 standardized YAML files:
1. `profile.yaml`: Metadata (name, version, industry).
2. `topology.yaml`: Entities (manufacturers, suppliers, warehouses, distribution centers, routes, products).
3. `agents.yaml`: Active agent roster, models, confidence thresholds, historical weights.
4. `disruptions.yaml`: Disruption catalog (parameters, severity scales, triggering rules).
5. `consensus.yaml`: CD²F parameters, WCS thresholds, Fast-Path/Slow-Path criteria.
6. `data_bindings.yaml`: Database connection strings and MCP server mappings.
7. `dashboard.yaml`: Map coordinates, view configurations, and heatmap dimensions.

At startup, every microservice points to the active profile via the `SCOF_PROFILE_PATH` environment variable. Swapping the active profile from `mvp-electronics` to a future profile requires altering one environment variable.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Complete reusability of the multi-agent orchestration kernel across any supply chain industry.
* Version-controlled, auditable supply chain topologies stored in Git.
* Easy creation of synthetic or edge-case benchmark profiles for stress testing.

### Negative Consequences / Trade-offs:
* Requires building robust Pydantic profile validation loaders (`shared/scof_shared/profile/loader.py`) to catch syntax errors on startup.

---

## 6. Implementation & Compliance Notes

* Profile directory in [profiles/mvp-electronics/](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/).
* Pydantic loader in `shared/scof_shared/profile/loader.py`.
* Active profile configured via `SCOF_PROFILE_PATH=./profiles/mvp-electronics` in `.env`.

---

## 7. Related Decisions & Artifacts

* [ADR 006: Protocol Standardization (MCP & A2A)](./006_mcp_and_a2a_protocol_standardization.md)
* [Domain Binding Strategy Document](file:///d:/projects/SCOF_V1/SCOF/docs/domain_binding_strategy.md)
