"""LangGraph orchestration graph compiler and execution engine for SCOF Coordinator."""

import hashlib
import json
import logging
import time
import uuid
from typing import Any, Dict, Optional
from langgraph.graph import END, START, StateGraph
from scof_shared.protocols.a2a_client import A2AClient
from scof_shared.protocols.a2a_registry import A2ARegistry
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.scenario_context import ScenarioContext
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
        self.graph = self._build_graph()
        self.app = self.graph.compile()
        self.graph_hash = self._compute_graph_hash()

    def _build_graph(self) -> StateGraph:
        """Constructs the LangGraph StateGraph."""
        builder = StateGraph(CoordinatorExecutionState)

        # Register nodes
        builder.add_node("initialize_context", self._node_initialize_context)
        builder.add_node("discover_agents", self._node_discover_agents)
        builder.add_node("dispatch_parallel", self._node_dispatch_parallel)
        builder.add_node("finalize_bundle", self._node_finalize_bundle)

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
        builder.add_edge("finalize_bundle", END)

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
        raw_claims, failed_agents, latencies = await ClaimCollector.dispatch_parallel(
            client=self.client,
            registry=self.registry,
            target_cards=targets,
            context=state["scenario_context"],
            trace_id=state["trace_id"],
            bundle_id=state["bundle_id"],
            profile_version=state["profile_version"],
        )
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
            "end_time": time.time(),
            "execution_log": logs,
        }

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
            "execution_log": [],
            "status": "INITIALIZING",
            "start_time": now,
            "end_time": 0.0,
        }

        final_state = await self.app.ainvoke(initial_state)
        claim_bundle = final_state["claim_bundle"]

        if claim_bundle is None:
            raise RuntimeError("Orchestration finished without producing a ClaimBundle.")

        return claim_bundle
