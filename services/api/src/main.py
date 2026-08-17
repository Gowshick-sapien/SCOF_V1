from contextlib import asynccontextmanager
import logging
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from .config import (
    API_NAME,
    API_VERSION,
    CORS_ORIGINS,
    REDIS_HOST,
    REDIS_PORT,
    KAFKA_BOOTSTRAP_SERVERS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
redis_client: redis.Redis | None = None
event_bus: Any | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, event_bus
    logger.info("Starting up SCOF API Gateway...")

    # Initialize Redis
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    await redis_client.ping()
    logger.info("Redis connected.")

    from .events.bus import EventBus
    from .events.topics import (
        TOPIC_DISRUPTIONS_TRIGGERED,
        TOPIC_WHATIF_REQUESTED,
        TOPIC_DECISIONS_COMPLETED,
        TOPIC_ORCHESTRATION_FAILED,
        TOPIC_AGENTS_ACTIVITY,
    )
    from .events.handlers import (
        handle_disruption_triggered,
        handle_whatif_requested,
        handle_decision_completed,
        handle_agent_activity,
        handle_orchestration_failed,
    )
    from .websocket.manager import manager as ws_manager

    event_bus = EventBus(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, redis_client=redis_client)
    
    # Register handlers
    event_bus.register_handler(
        TOPIC_DISRUPTIONS_TRIGGERED, 
        lambda env: handle_disruption_triggered(env, event_bus)
    )
    event_bus.register_handler(
        TOPIC_WHATIF_REQUESTED, 
        lambda env: handle_whatif_requested(env, event_bus, redis_client)
    )
    event_bus.register_handler(
        TOPIC_DECISIONS_COMPLETED, 
        lambda env: handle_decision_completed(env, ws_manager, redis_client)
    )
    event_bus.register_handler(
        TOPIC_AGENTS_ACTIVITY, 
        lambda env: handle_agent_activity(env, ws_manager)
    )
    event_bus.register_handler(
        TOPIC_ORCHESTRATION_FAILED, 
        lambda env: handle_orchestration_failed(env, ws_manager)
    )
    
    await event_bus.start()
    
    app.state.redis_client = redis_client
    app.state.event_bus = event_bus
    
    yield
    
    logger.info("Shutting down SCOF API Gateway...")
    await event_bus.stop()
    if redis_client:
        await redis_client.aclose()


app = FastAPI(
    title=API_NAME,
    version=API_VERSION,
    description="SCOF D08 Backend API and Real-Time Gateway",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .middleware.error_handler import ErrorHandlerMiddleware
app.add_middleware(ErrorHandlerMiddleware)

from .websocket.channels import router as websocket_router
from .routers.scenarios import router as scenarios_router
from .routers.whatif import router as whatif_router
from .routers.dashboard import router as dashboard_router
from .routers.decisions import router as decisions_router
from .routers.evaluation import router as evaluation_router
from .routers.chat import router as chat_router
from .routers.profile import router as profile_router

app.include_router(websocket_router)
app.include_router(scenarios_router)
app.include_router(whatif_router)
app.include_router(dashboard_router)
app.include_router(decisions_router)
app.include_router(evaluation_router)
app.include_router(chat_router)
app.include_router(profile_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": API_NAME, "version": API_VERSION}
