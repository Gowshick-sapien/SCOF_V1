"""FastAPI Application entry point for SCOF Coordinator Microservice."""

from contextlib import asynccontextmanager
import logging
import os
import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.orchestration_result import OrchestrationResult
from scof_shared.schemas.scenario_context import ScenarioContext
from aiokafka import AIOKafkaProducer
from .config import (
    CONNECT_TIMEOUT_SECONDS,
    COORDINATOR_ID,
    COORDINATOR_NAME,
    COORDINATOR_VERSION,
    MAX_CONCURRENT_DISPATCH,
    MAX_RETRIES,
    MOCK_MODE,
    READ_TIMEOUT_SECONDS,
    SCOF_PROFILE_PATH,
)
from .orchestrator import CoordinatorOrchestrator
from .runtime import CoordinatorRuntime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coordinator")

runtime: Optional[CoordinatorRuntime] = None
orchestrator: Optional[CoordinatorOrchestrator] = None
kafka_producer: Optional[AIOKafkaProducer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes Coordinator runtime, domain profile, A2A registry, and LangGraph orchestrator."""
    global runtime, orchestrator, kafka_producer
    logger.info("Initializing SCOF Coordinator Service...")

    mock_mode = os.getenv("MOCK_MODE", "false").lower() in ("true", "1")
    runtime = CoordinatorRuntime(
        profile_path=SCOF_PROFILE_PATH,
        connect_timeout_sec=CONNECT_TIMEOUT_SECONDS,
        read_timeout_sec=READ_TIMEOUT_SECONDS,
        max_retries=MAX_RETRIES,
        max_concurrent_dispatch=MAX_CONCURRENT_DISPATCH,
        mock_mode=mock_mode,
    )
    runtime.load_domain_profile()

    # Initial agent discovery
    discovered_count = runtime.refresh_discovery()
    logger.info("Initial discovery registered %d specialist agents", discovered_count)

    # Initialize LangGraph orchestrator
    profile_name = runtime.profile.meta.name if (runtime.profile and runtime.profile.meta) else "mvp-electronics"
    orchestrator = CoordinatorOrchestrator(
        registry=runtime.registry,
        client=runtime.a2a_client,
        profile_name=profile_name,
        profile_version=COORDINATOR_VERSION,
        runtime=runtime,
    )
    runtime.compiled_graph = orchestrator.app
    runtime.graph_metadata = orchestrator.get_metadata()

    # Initialize Kafka Producer for agent activity events
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
    try:
        kafka_producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            enable_idempotence=True
        )
        await kafka_producer.start()
        orchestrator.activity_producer = kafka_producer
        logger.info("Kafka producer initialized for agent activity events.")
    except Exception as e:
        logger.warning(f"Failed to initialize Kafka producer (running without activity publishing): {e}")

    yield
    logger.info("Shutting down SCOF Coordinator Service...")
    if kafka_producer:
        await kafka_producer.stop()


app = FastAPI(
    title=COORDINATOR_NAME,
    version=COORDINATOR_VERSION,
    description="LangGraph Cognitive Coordinator for Multi-Agent Supply Chain Orchestration.",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Rich health check reporting registry status, graph compilation, and uptime."""
    if not runtime or not orchestrator:
        raise HTTPException(status_code=503, detail="Coordinator runtime not initialized")

    healthy_agents = [r.card.agent_id for r in runtime.registry.get_all() if r.health_status == "HEALTHY"]

    return {
        "status": "healthy",
        "agent_id": COORDINATOR_ID,
        "name": COORDINATOR_NAME,
        "version": COORDINATOR_VERSION,
        "registered_agents_count": len(runtime.registry),
        "healthy_agents": healthy_agents,
        "graph_compiled": runtime.compiled_graph is not None,
        "graph_hash": orchestrator.graph_hash,
        "mock_mode": runtime.a2a_client.mock_mode,
        "metrics": runtime.metrics.to_dict(),
    }


@app.get("/metrics")
def get_metrics() -> Dict[str, Any]:
    """Operational telemetry for multi-agent orchestrations."""
    if not runtime:
        raise HTTPException(status_code=503, detail="Coordinator runtime not initialized")
    return runtime.metrics.to_dict()


@app.get("/.well-known/agent.json", response_model=AgentCard)
def get_agent_card() -> AgentCard:
    """A2A discovery agent card for the Coordinator."""
    return AgentCard(
        agent_id=COORDINATOR_ID,
        name=COORDINATOR_NAME,
        description="Coordinates multi-agent consensus, evidence aggregation, and claim bundle assembly.",
        version=COORDINATOR_VERSION,
        capabilities=["orchestrate", "aggregate_claims", "agent_discovery"],
        tags=["coordinator", "langgraph", "a2a"],
        supported_contexts=["all", "baseline_assessment", "supplier_delay", "transport_failure", "demand_spike"],
        endpoint=f"http://localhost:{os.getenv('PORT', 8010)}",
    )


@app.get("/agents")
def list_agents() -> Dict[str, Any]:
    """Lists all registered specialist agents in the A2A registry and their health states."""
    if not runtime:
        raise HTTPException(status_code=503, detail="Coordinator runtime not initialized")

    registrations = runtime.registry.get_all()
    return {
        "total_registered": len(registrations),
        "agents": [
            {
                "agent_id": reg.card.agent_id,
                "name": reg.card.name,
                "endpoint": reg.endpoint_url,
                "health_status": reg.health_status,
                "failure_count": reg.failure_count,
                "consecutive_failures": reg.consecutive_failures,
                "average_latency_ms": reg.average_latency_ms,
                "last_seen": reg.last_seen.isoformat() if reg.last_seen else None,
                "capabilities": reg.card.capabilities,
                "supported_contexts": reg.card.supported_contexts,
            }
            for reg in registrations
        ],
    }


@app.post("/agents/refresh")
def refresh_agents(request_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Triggers an atomic copy-on-write discovery refresh of active specialist agents."""
    if not runtime or not orchestrator:
        raise HTTPException(status_code=503, detail="Coordinator runtime not initialized")

    host_map = request_data.get("host_map") if request_data else None
    count = runtime.refresh_discovery(host_map=host_map)
    orchestrator.registry = runtime.registry

    return {
        "status": "success",
        "registered_agents_count": count,
        "discovery_duration_ms": runtime.metrics.last_discovery_duration_ms,
        "agents": [r.card.agent_id for r in runtime.registry.get_all()],
    }


@app.get("/graph")
def get_graph() -> Dict[str, Any]:
    """Returns the LangGraph structural topology, nodes, edges, hash, and Mermaid diagram."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Coordinator orchestrator not initialized")
    return orchestrator.get_metadata()


@app.post("/orchestrate", response_model=ClaimBundle)
async def orchestrate_scenario(context: ScenarioContext, request: Request) -> ClaimBundle:
    """Executes the multi-agent orchestration pipeline for a scenario context."""
    if not orchestrator or not runtime:
        raise HTTPException(status_code=503, detail="Coordinator service not initialized")

    if len(runtime.registry) == 0:
        logger.info("Registry is empty prior to orchestrate. Triggering discovery refresh...")
        runtime.refresh_discovery()
        orchestrator.registry = runtime.registry

    start_time = time.time()
    trace_id = request.headers.get("X-Trace-ID")
    bundle_id = request.headers.get("X-Bundle-ID")

    try:
        bundle = await orchestrator.orchestrate(
            context=context,
            trace_id=trace_id,
            bundle_id=bundle_id,
        )

        latency_ms = (time.time() - start_time) * 1000
        runtime.metrics.orchestrations_executed += 1
        runtime.metrics.total_orchestration_latency_ms += latency_ms

        if bundle.status == "COMPLETE":
            runtime.metrics.orchestrations_successful += 1
        elif bundle.status == "PARTIAL":
            runtime.metrics.orchestrations_partial += 1
        else:
            runtime.metrics.orchestrations_failed += 1

        return bundle

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        runtime.metrics.orchestrations_executed += 1
        runtime.metrics.orchestrations_failed += 1
        runtime.metrics.total_orchestration_latency_ms += latency_ms
        logger.exception("Orchestration failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=ClaimBundle)
async def analyze_scenario_alias(context: ScenarioContext, request: Request) -> ClaimBundle:
    """A2A-compatible alias for /orchestrate."""
    return await orchestrate_scenario(context, request)


@app.post("/orchestrate/full", response_model=OrchestrationResult)
async def orchestrate_scenario_full(context: ScenarioContext, request: Request) -> OrchestrationResult:
    """Executes the multi-agent orchestration pipeline for a scenario context and returns full result."""
    if not orchestrator or not runtime:
        raise HTTPException(status_code=503, detail="Coordinator service not initialized")

    if len(runtime.registry) == 0:
        logger.info("Registry is empty prior to orchestrate/full. Triggering discovery refresh...")
        runtime.refresh_discovery()
        orchestrator.registry = runtime.registry

    start_time = time.time()
    trace_id = request.headers.get("X-Trace-ID")
    bundle_id = request.headers.get("X-Bundle-ID")

    try:
        result = await orchestrator.orchestrate_full(
            context=context,
            trace_id=trace_id,
            bundle_id=bundle_id,
        )

        latency_ms = (time.time() - start_time) * 1000
        runtime.metrics.orchestrations_executed += 1
        runtime.metrics.total_orchestration_latency_ms += latency_ms

        if result.claim_bundle.status == "COMPLETE":
            runtime.metrics.orchestrations_successful += 1
        elif result.claim_bundle.status == "PARTIAL":
            runtime.metrics.orchestrations_partial += 1
        else:
            runtime.metrics.orchestrations_failed += 1

        return result

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        runtime.metrics.orchestrations_executed += 1
        runtime.metrics.orchestrations_failed += 1
        runtime.metrics.total_orchestration_latency_ms += latency_ms
        logger.exception("Orchestration failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
