"""LangGraph orchestration graph compiler and execution engine for SCOF Coordinator."""

import hashlib
import json
import logging
import time
import uuid
from typing import Any, Dict, Optional
import httpx
from langgraph.graph import END, START, StateGraph
from scof_shared.protocols.a2a_client import A2AClient
from scof_shared.protocols.a2a_registry import A2ARegistry
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.decision_record import DecisionRecord
from scof_shared.schemas.orchestration_result import OrchestrationResult
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.observability.tracing import create_runnable_config
import datetime
from .agent_discovery import AgentDiscoveryService
from .claim_collector import ClaimCollector
from .state import CoordinatorExecutionState

logger = logging.getLogger(__name__)


class CoordinatorOrchestrator:
    """Compiles and executes the LangGraph StateGraph for multi-agent supply chain orchestration."""

    def __init__(
        self,
        registry: A2ARegistry,
        client: A2AClient,
        profile_name: str = "mvp-electronics",
        profile_version: str = "1.0.0",
    ):
        self.registry = registry
        self.client = client
        self.profile_name = profile_name
        self.profile_version = profile_version
        self.activity_producer = None
        self.graph = self._build_graph()
        self.app = self.graph.compile()
        self.graph_hash = self._compute_graph_hash()

    async def _publish_activity(self, state: CoordinatorExecutionState, agent_id: str, status: str, latency_ms: float = 0.0):
        if not self.activity_producer:
            return
        
        try:
            envelope = {
                "event_id": f"evt-{uuid.uuid4().hex}",
                "event_type": "agents.activity",
                "schema_version": "1.0.0",
                "producer": "scof-coordinator",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "correlation": {
                    "trace_id": state["trace_id"],
                    "scenario_id": state["scenario_context"].scenario_id,
                    "profile_version": state["profile_version"],
                    # request_id can be passed if we extract it, but trace_id is sufficient for now
                    "request_id": state.get("request_id", "")
                },
                "payload": {
                    "agent_id": agent_id,
                    "status": status,
                    "latency_ms": latency_ms,
                    "scenario_id": state["scenario_context"].scenario_id,
                    "trace_id": state["trace_id"]
                }
            }
            # The activity producer is expected to be an AIOKafkaProducer
            await self.activity_producer.send_and_wait(
                "scof.agents.activity",
                key=agent_id.encode("utf-8"),
                value=json.dumps(envelope).encode("utf-8")
            )
        except Exception as e:
            logger.warning("Failed to publish agent activity for %s: %s", agent_id, e)

    def _build_graph(self) -> StateGraph:
        """Constructs the LangGraph StateGraph."""
        builder = StateGraph(CoordinatorExecutionState)  # type: ignore

        # Register nodes
        builder.add_node("initialize_context", self._node_initialize_context)
        builder.add_node("discover_agents", self._node_discover_agents)
        builder.add_node("dispatch_parallel", self._node_dispatch_parallel)
        builder.add_node("finalize_bundle", self._node_finalize_bundle)
        builder.add_node("run_consensus", self._node_run_consensus)
        builder.add_node("persist_decision", self._node_persist_decision)

        # Wire edges
        builder.add_edge(START, "initialize_context")
        builder.add_edge("initialize_context", "discover_agents")

        # Conditional branch from discovery
        builder.add_conditional_edges(
            "discover_agents",
            self._route_after_discovery,
            {
                "dispatch": "dispatch_parallel",
                "empty": "finalize_bundle",
            },
        )

        builder.add_edge("dispatch_parallel", "finalize_bundle")
        builder.add_edge("finalize_bundle", "run_consensus")
        builder.add_edge("run_consensus", "persist_decision")
        builder.add_edge("persist_decision", END)

        return builder

    async def _node_initialize_context(
        self, state: CoordinatorExecutionState
    ) -> Dict[str, Any]:
        logs = list(state.get("execution_log", []))
        logs.append(
            f"Initialized orchestration for scenario '{state['scenario_context'].scenario_id}' with trace '{state['trace_id']}'"
        )
        return {
            "execution_log": logs,
            "status": "RUNNING",
        }

    async def _node_discover_agents(
        self, state: CoordinatorExecutionState
    ) -> Dict[str, Any]:
        targets = AgentDiscoveryService.resolve_targets(
            registry=self.registry,
            context=state["scenario_context"],
        )
        logs = list(state.get("execution_log", []))
        logs.append(
            f"Discovered {len(targets)} candidate specialist agents from A2ARegistry"
        )
        return {
            "target_agent_cards": targets,
            "execution_log": logs,
        }

    def _route_after_discovery(self, state: CoordinatorExecutionState) -> str:
        if state.get("target_agent_cards"):
            return "dispatch"
        return "empty"

    async def _node_dispatch_parallel(
        self, state: CoordinatorExecutionState
    ) -> Dict[str, Any]:
        targets = state["target_agent_cards"]
        
        # Best-effort pre-dispatch publishing
        for target in targets:
            await self._publish_activity(state, target.agent_id, "DISPATCHED")

        raw_claims, failed_agents, latencies = await ClaimCollector.dispatch_parallel(
            client=self.client,
            registry=self.registry,
            target_cards=targets,
            context=state["scenario_context"],
            trace_id=state["trace_id"],
            bundle_id=state["bundle_id"],
            profile_version=state["profile_version"],
        )
        
        # Best-effort post-dispatch publishing
        for agent_id, claim in raw_claims.items():
            await self._publish_activity(state, agent_id, "COMPLETED", latencies.get(agent_id, 0.0))
            
        for agent_id, error in failed_agents.items():
            await self._publish_activity(state, agent_id, "FAILED", latencies.get(agent_id, 0.0))
            
        logs = list(state.get("execution_log", []))
        logs.append(
            f"Parallel dispatch complete: {len(raw_claims)} successful, {len(failed_agents)} failed"
        )
        return {
            "raw_claims": raw_claims,
            "failed_agents": failed_agents,
            "agent_latencies_ms": latencies,
            "execution_log": logs,
        }

    async def _node_finalize_bundle(
        self, state: CoordinatorExecutionState
    ) -> Dict[str, Any]:
        bundle = ClaimCollector.build_claim_bundle(
            scenario_context=state["scenario_context"],
            trace_id=state["trace_id"],
            bundle_id=state["bundle_id"],
            profile_name=state["profile_name"],
            profile_version=state["profile_version"],
            target_cards=state.get("target_agent_cards", []),
            raw_claims=state.get("raw_claims", {}),
            failed_agents=state.get("failed_agents", {}),
            agent_latencies_ms=state.get("agent_latencies_ms", {}),
            start_time=state.get("start_time", time.time()),
        )
        logs = list(state.get("execution_log", []))
        logs.append(
            f"Assembled ClaimBundle '{bundle.bundle_id}' with status '{bundle.status}'"
        )
        return {
            "claim_bundle": bundle,
            "status": bundle.status,
            "execution_log": logs,
        }

    async def _node_run_consensus(self, state: CoordinatorExecutionState) -> Dict[str, Any]:
        bundle = state["claim_bundle"]
        if not bundle:
            raise RuntimeError("No ClaimBundle available for consensus")
            
        logs = list(state.get("execution_log", []))
        
        if getattr(self.client, "mock_mode", False):
            from datetime import datetime
            decision = DecisionRecord(
                decision_id=f"dec-mock-{uuid.uuid4().hex[:8]}",
                scenario_id=bundle.scenario_id,
                consensus_bundle_id=bundle.bundle_id,
                source_bundle_id=bundle.bundle_id,
                decision_method="CD2F",
                final_recommendation="Mock mode consensus approved",
                decision_confidence=0.99,
                weighted_consensus_stability=0.95,
                escalation_tier="FAST_PATH",
                escalation_rationale="Mock",
                agent_weights={},
                recommendation_tallies={},
                reasoning_trail=[],
                meeting_log_entries=[],
                timestamp=datetime.now(),
                profile_name=state.get("profile_name", "mvp-electronics"),
                profile_version=state.get("profile_version", "1.0.0"),
                engine_version="1.0.0"
            )
            logs.append(f"Generated Mock DecisionRecord '{decision.decision_id}'")
            return {"decision_record": decision, "execution_log": logs}
            
        async with httpx.AsyncClient() as client:
            try:
                # D6 Consensus runs on port 8020 in docker
                resp = await client.post(
                    "http://consensus:8020/arbitrate",
                    json={"bundle": bundle.model_dump(mode="json"), "profile_name": state["profile_name"]},
                    timeout=10.0
                )
                resp.raise_for_status()
                decision = DecisionRecord(**resp.json())
                logs.append(f"Generated DecisionRecord '{decision.decision_id}' via CD2F engine")
                return {"decision_record": decision, "execution_log": logs}
            except Exception as e:
                logs.append(f"Consensus generation failed: {e}")
                raise RuntimeError(f"Failed to generate consensus: {e}")

    async def _node_persist_decision(self, state: CoordinatorExecutionState) -> Dict[str, Any]:
        decision = state["decision_record"]
        if not decision:
            raise RuntimeError("No DecisionRecord available for persistence")
            
        logs = list(state.get("execution_log", []))
        
        if getattr(self.client, "mock_mode", False):
            logs.append(f"Mock persisted decision '{decision.decision_id}'")
            return {"execution_log": logs, "end_time": time.time()}
            
        async with httpx.AsyncClient() as client:
            # Implement bounded retries for D7 persistence
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # D7 Observability runs on port 8030
                    resp = await client.post(
                        "http://observability:8030/decisions",
                        json=decision.model_dump(mode="json"),
                        headers={"X-Trace-ID": state["trace_id"]},
                        timeout=5.0
                    )
                    resp.raise_for_status()
                    logs.append(f"Successfully persisted decision '{decision.decision_id}' to D7 (attempt {attempt+1})")
                    return {"execution_log": logs, "end_time": time.time()}
                except Exception as e:
                    if attempt == max_retries - 1:
                        logs.append(f"Failed to persist decision to D7 after {max_retries} attempts: {e}")
                        raise RuntimeError(f"D7 persistence failed: {e}")
                    # Brief backoff
                    import asyncio
                    await asyncio.sleep(0.5)
        raise RuntimeError("Unreachable")

    def _compute_graph_hash(self) -> str:
        structure = {
            "nodes": ["initialize_context", "discover_agents", "dispatch_parallel", "finalize_bundle"],
            "edges": [
                ("START", "initialize_context"),
                ("initialize_context", "discover_agents"),
                ("discover_agents", "dispatch_parallel"),
                ("discover_agents", "finalize_bundle"),
                ("dispatch_parallel", "finalize_bundle"),
                ("finalize_bundle", "END"),
            ],
            "state_schema": "CoordinatorExecutionState",
        }
        raw = json.dumps(structure, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_mermaid_diagram(self) -> str:
        """Returns Mermaid flowchart representing the orchestration graph."""
        return (
            "graph TD\n"
            "    __start__([Start]) --> initialize_context[Initialize Context]\n"
            "    initialize_context --> discover_agents[Discover Agents]\n"
            "    discover_agents -->|Agents Found| dispatch_parallel[Parallel Dispatch]\n"
            "    discover_agents -->|No Agents| finalize_bundle[Finalize Bundle]\n"
            "    dispatch_parallel --> finalize_bundle\n"
            "    finalize_bundle --> __end__([End])"
        )

    def get_metadata(self) -> Dict[str, Any]:
        """Returns orchestration graph structural metadata."""
        return {
            "nodes": [
                {"name": "initialize_context", "type": "function"},
                {"name": "discover_agents", "type": "function"},
                {"name": "dispatch_parallel", "type": "function"},
                {"name": "finalize_bundle", "type": "function"},
            ],
            "edges": [
                {"source": "START", "target": "initialize_context"},
                {"source": "initialize_context", "target": "discover_agents"},
                {"source": "discover_agents", "target": "dispatch_parallel"},
                {"source": "discover_agents", "target": "finalize_bundle"},
                {"source": "dispatch_parallel", "target": "finalize_bundle"},
                {"source": "finalize_bundle", "target": "END"},
            ],
            "graph_hash": self.graph_hash,
            "mermaid": self.get_mermaid_diagram(),
        }

    async def orchestrate(
        self,
        context: ScenarioContext,
        trace_id: Optional[str] = None,
        bundle_id: Optional[str] = None,
    ) -> ClaimBundle:
        """Runs the LangGraph orchestration pipeline for a scenario context."""
        trace = trace_id or str(uuid.uuid4())
        bundle = bundle_id or f"bundle-{uuid.uuid4().hex[:8]}"
        now = time.time()

        initial_state: CoordinatorExecutionState = {
            "scenario_context": context,
            "trace_id": trace,
            "bundle_id": bundle,
            "profile_name": self.profile_name,
            "profile_version": self.profile_version,
            "target_agent_cards": [],
            "raw_claims": {},
            "failed_agents": {},
            "agent_latencies_ms": {},
            "claim_bundle": None,
            "decision_record": None,
            "execution_log": [],
            "status": "INITIALIZING",
            "start_time": now,
            "end_time": 0.0,
        }

        # Apply LangSmith trace context
        run_config = create_runnable_config(
            scenario_id=context.scenario_id,
            bundle_id=bundle,
            trace_id=trace,
            profile_version=self.profile_version
        )

        final_state = await self.app.ainvoke(initial_state, config=run_config)  # type: ignore[reportArgumentType]
        claim_bundle = final_state.get("claim_bundle")
        decision_record = final_state.get("decision_record")

        if claim_bundle is None:
            raise RuntimeError("Orchestration finished without producing a ClaimBundle.")
            
        return claim_bundle

    async def orchestrate_full(
        self,
        context: ScenarioContext,
        trace_id: Optional[str] = None,
        bundle_id: Optional[str] = None,
    ) -> OrchestrationResult:
        """Runs the LangGraph orchestration pipeline for a scenario context and returns full result."""
        trace = trace_id or str(uuid.uuid4())
        bundle = bundle_id or f"bundle-{uuid.uuid4().hex[:8]}"
        now = time.time()

        initial_state: CoordinatorExecutionState = {
            "scenario_context": context,
            "trace_id": trace,
            "bundle_id": bundle,
            "profile_name": self.profile_name,
            "profile_version": self.profile_version,
            "target_agent_cards": [],
            "raw_claims": {},
            "failed_agents": {},
            "agent_latencies_ms": {},
            "claim_bundle": None,
            "decision_record": None,
            "execution_log": [],
            "status": "INITIALIZING",
            "start_time": now,
            "end_time": 0.0,
        }

        run_config = create_runnable_config(
            scenario_id=context.scenario_id,
            bundle_id=bundle,
            trace_id=trace,
            profile_version=self.profile_version
        )

        final_state = await self.app.ainvoke(initial_state, config=run_config)  # type: ignore[reportArgumentType]
        claim_bundle = final_state.get("claim_bundle")
        decision_record = final_state.get("decision_record")

        if claim_bundle is None:
            raise RuntimeError("Orchestration finished without producing a ClaimBundle.")
            
        return OrchestrationResult(
            claim_bundle=claim_bundle,
            decision_record=decision_record
        )
