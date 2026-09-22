# Deliverable D05 -- Agent-to-Agent (A2A) Protocol & Discovery Design

## 1. Executive Overview

This document specifies the **Agent-to-Agent (A2A)** protocol, discovery lifecycle, and registry health management for Deliverable D05.

Per SRS FR-5.3 and FR-5.5, the Coordinator does not maintain hardcoded endpoint lists or domain-specific dispatch routines. Instead, it discovers specialist agents dynamically through standard A2A Agent Cards (`GET /.well-known/agent.json`), maintains a thread-safe registry with operational health telemetry, and delegates scenario evaluations using standardized HTTP contracts.

---

## 2. A2A Agent Card Specification

Each specialist agent publishes a self-describing Agent Card containing capability declarations, supported contexts, and protocol version metadata:

```python
class AgentCard(BaseModel):
    """Universal A2A self-describing agent metadata contract."""

    agent_id: str = Field(..., description="Unique ID of the agent")
    name: str = Field(..., description="Human-readable agent display name")
    description: str = Field(..., description="Detailed functional description")
    version: str = Field("1.0.0", description="Semantic version string")
    capabilities: List[str] = Field(default_factory=list, description="List of capability names")
    tags: List[str] = Field(default_factory=list, description="Classification tags")
    supported_contexts: List[str] = Field(
        default_factory=list, description="Disruption types this agent processes"
    )
    dependencies: List[str] = Field(
        default_factory=list, description="External systems or databases required"
    )
    input_schema: Dict[str, str] = Field(
        default_factory=lambda: {"context": "ScenarioContext"},
        description="Input payload contract schema name"
    )
    output_schema: str = Field(
        "StructuredClaim", description="Output contract schema name"
    )
    protocol: str = Field("A2A/1.0", description="Supported protocol standard")
    protocol_version: str = Field("A2A/1.0", description="A2A protocol version")
    agent_version: str = Field("1.0.0", description="Agent release version")
    profile_version: Optional[str] = Field("1.0.0", description="Profile compatibility version")
    endpoint: str = Field(..., description="Base HTTP URL for agent service")
```

### 2.1 Example Published Agent Cards

#### Supplier Intelligence Agent (`supplier-agent`, port 8013)
```json
{
  "agent_id": "supplier-agent",
  "name": "Supplier Intelligence Agent",
  "description": "Assesses vendor reliability and predicts supplier failure risks.",
  "version": "1.0.0",
  "capabilities": [
    "supplier_reliability_scoring",
    "failure_prediction",
    "alternate_supplier_recommendation"
  ],
  "tags": ["supplier", "reliability", "graph", "risk"],
  "supported_contexts": ["supplier_delay", "baseline_assessment"],
  "dependencies": ["postgres", "neo4j"],
  "input_schema": {"context": "ScenarioContext"},
  "output_schema": "StructuredClaim",
  "protocol": "A2A/1.0",
  "protocol_version": "A2A/1.0",
  "agent_version": "1.0.0",
  "profile_version": "1.0.0",
  "endpoint": "http://supplier-agent:8013"
}
```

---

## 3. Dynamic Discovery & Registry Lifecycle

```
 +-----------------------------+
 | profiles/agents.yaml Roster |
 +-----------------------------+
               |
               v
 +-----------------------------+
 |       Startup Trigger       |
 +-----------------------------+
               |
               v
 +-----------------------------+
 |   A2AClient.discover_roster |  ---> Parallel GET /.well-known/agent.json
 +-----------------------------+
               |
               v
 +-----------------------------+
 | Atomic Copy-on-Write Swap   |  ---> Installs new immutable A2ARegistry snapshot
 +-----------------------------+
               |
               v
 +-----------------------------+
 | Cached Registry In-Memory   |  ---> Serves /orchestrate without per-request probe
 +-----------------------------+
```

### 3.1 Registry Caching and Copy-on-Write Refresh

1. **Startup Discovery**:
   - The Coordinator reads the active `agents.yaml` file from the configured `SCOF_PROFILE_PATH`.
   - It queries `GET /.well-known/agent.json` for each declared agent, validating response schema and recording endpoint URLs.
   - Populates the initial `A2ARegistry`.

2. **Atomic Copy-on-Write Swap**:
   - When a refresh is triggered (via `POST /agents/refresh` or profile file change detection), a new `A2ARegistry` instance is constructed out-of-band.
   - The Coordinator performs an **atomic reference swap**: `self.registry = new_registry`.
   - In-flight orchestrations reading the previous reference snapshot continue undisturbed without lock contention or data race conditions.

---

## 4. Deterministic Health-State Machine & Telemetry

The `A2ARegistry` tracks operational telemetry and manages agent health transitions:

```
  +-------------+
  |   UNKNOWN   |  (Initial state before first communication)
  +-------------+
         |
    [Probe OK]
         |
         v
  +-------------+  [2 to 4 consecutive failures OR latency > 5000ms]
  |   HEALTHY   | -----------------------------------------------------> +-------------+
  +-------------+                                                        |  DEGRADED   |
         ^                                                               +-------------+
         |                                                                      |
         +------------------- [Successful Recovery] <---------------------------+
         |                                                                      |
         |                                                           [>= 5 consecutive failures]
         |                                                                      |
         |                                                                      v
         +------------------- [Successful Recovery] <------------------- +-------------+
                                                                         |  UNHEALTHY  |
                                                                         +-------------+
```

### 4.1 State Definitions & Thresholds

- **`UNKNOWN`**: Default state before the agent has been probed or delegated to.
- **`HEALTHY`**: Agent responded successfully with a valid `StructuredClaim` within acceptable latency (< 5000ms). Consecutive failure counter is reset to 0.
- **`DEGRADED`**: Agent experienced 2 to 4 consecutive communication failures, or responded with latency exceeding 5000ms. The agent remains in the dispatch pool but is flagged for degraded performance in the registry telemetry.
- **`UNHEALTHY`**: Agent experienced 5 or more consecutive communication failures. The agent is marked offline in registry summaries.

### 4.2 Registry Telemetry Data Model

```python
@dataclass
class AgentRegistration:
    """Registered agent entry in the A2A registry."""
    card: AgentCard
    endpoint_url: str
    health_status: Literal["UNKNOWN", "HEALTHY", "DEGRADED", "UNHEALTHY"] = "UNKNOWN"
    last_seen: Optional[datetime] = None
    consecutive_failures: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_latency_ms: float = 0.0

    @property
    def average_latency_ms(self) -> float:
        if self.success_count == 0:
            return 0.0
        return round(self.total_latency_ms / self.success_count, 2)
```

---

## 5. Parallel Delegation & Throttling Architecture

### 5.1 Semaphore Bounded Concurrency

To prevent socket exhaustion and latency spikes when scaling to dozens of specialist agents, `A2AClient` enforces bounded concurrency via an `asyncio.Semaphore`:

```python
MAX_CONCURRENT_DISPATCH = 8

async def delegate_analyze_parallel(
    self,
    agent_cards: List[AgentCard],
    context: ScenarioContext,
    trace_id: str,
    bundle_id: str,
    profile_version: str,
) -> Dict[str, Tuple[Optional[StructuredClaim], Optional[str], float]]:
    semaphore = asyncio.Semaphore(self.max_concurrent_dispatch)

    async def _bounded_call(card: AgentCard):
        async with semaphore:
            return await self.delegate_analyze(card, context, trace_id, bundle_id, profile_version)

    tasks = [_bounded_call(card) for card in agent_cards]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    ...
```

### 5.2 Granular Timeouts & Differentiated Retry Policy

- **`CONNECT_TIMEOUT = 2.0s`**: Fast failure if agent container or network port is completely unreachable.
- **`READ_TIMEOUT = 8.0s`**: Sufficient window for ML inference and graph traversal under load.
- **Status-Code-Aware Retries**:
  - `4xx Client Errors` (e.g. 400, 404, 422): **Do not retry** (indicates invalid contract or unhandled context).
  - `5xx Server Errors` (e.g. 500, 502, 503) & `ReadTimeout`: **Retry up to 2 times** with exponential backoff (initial delay 200ms, backoff factor 2.0).

### 5.3 Correlation & Lineage Header Propagation

Every outgoing HTTP request sent by `A2AClient` attaches distributed tracing headers:
- `X-Scenario-ID`: Scenario identifier being evaluated.
- `X-Bundle-ID`: Unique UUID generated for the current `ClaimBundle`.
- `X-Trace-ID`: Distributed trace identifier passed down to downstream services.
- `X-Profile-Version`: Active domain profile semantic version.
- `X-Agent-ID`: Target specialist agent ID.

---

## 6. Zero Concrete Agent Invariants

The Coordinator maintains total domain agnosticism:
- **No Agent Name Literals**: Nowhere in the Coordinator orchestration code exists any string comparison or branch such as `if agent_id == "demand"` or `if agent == "supplier"`.
- **Capability Matching**: Target agents are matched dynamically using `AgentCard.supported_contexts` and `AgentCard.capabilities`.
- **Profile Independence**: Adding a new specialist agent (e.g., `sustainability-agent` in a future deliverable) requires only adding an entry in `agents.yaml` -- zero Coordinator code modifications required.
