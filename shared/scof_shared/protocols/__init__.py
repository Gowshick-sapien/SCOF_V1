"""SCOF Protocols Package for A2A and MCP communication."""

from scof_shared.protocols.a2a_registry import A2ARegistry, AgentRegistration, HealthStatus
from scof_shared.protocols.a2a_client import A2AClient
from scof_shared.protocols.mcp_server import (
    create_mcp_router,
    MCPToolCallRequest,
    MCPToolCallResponse,
    MCPToolResponseContent,
)
from scof_shared.protocols.mcp_client import MCPClient

__all__ = [
    "A2ARegistry",
    "AgentRegistration",
    "HealthStatus",
    "A2AClient",
    "create_mcp_router",
    "MCPToolCallRequest",
    "MCPToolCallResponse",
    "MCPToolResponseContent",
    "MCPClient",
]
