"""Model Context Protocol (MCP) Server Router for SCOF Specialist Agents.

Exposes standard POST /mcp/tools/list and POST /mcp/tools/call endpoints.
"""

from typing import Any, Callable, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field


class MCPToolCallRequest(BaseModel):
    """Request payload for MCP tool execution."""

    name: str = Field(..., description="Tool name to execute")
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="Arguments for tool execution"
    )


class MCPToolResponseContent(BaseModel):
    """Standard MCP response content block."""

    type: str = Field("json", description="Content type (json or text)")
    data: Optional[Any] = Field(None, description="Structured data payload")
    text: Optional[str] = Field(None, description="Text message or error detail")


class MCPToolCallResponse(BaseModel):
    """Standard MCP tool execution response."""

    content: List[MCPToolResponseContent] = Field(default_factory=list)
    isError: bool = Field(False, description="Whether tool execution failed")


def create_mcp_router(
    tools: List[Any],
    execution_handlers: Dict[str, Callable[[Dict[str, Any]], Any]],
) -> APIRouter:
    """Creates a FastAPI APIRouter exposing standardized MCP tool endpoints."""
    router = APIRouter(prefix="/mcp", tags=["Model Context Protocol"])

    @router.post("/tools/list")
    def list_tools():
        """Lists all registered MCP domain business tools and their schemas."""
        tool_schemas = []
        for t in tools:
            if hasattr(t, "to_mcp_schema"):
                tool_schemas.append(t.to_mcp_schema())
            elif isinstance(t, dict):
                tool_schemas.append(t)
            else:
                tool_schemas.append(
                    {
                        "name": getattr(t, "name", str(t)),
                        "description": getattr(t, "description", ""),
                        "inputSchema": getattr(t, "input_schema", {}),
                    }
                )
        return {"tools": tool_schemas}

    @router.post("/tools/call", response_model=MCPToolCallResponse)
    def call_tool(request: MCPToolCallRequest):
        """Executes a registered MCP domain business tool."""
        handler = execution_handlers.get(request.name)
        if not handler:
            return MCPToolCallResponse(
                content=[
                    MCPToolResponseContent(
                        type="text",
                        text=f"Tool '{request.name}' is not registered on this agent.",
                    )
                ],
                isError=True,
            )

        try:
            result = handler(request.arguments)
            return MCPToolCallResponse(
                content=[MCPToolResponseContent(type="json", data=result)],
                isError=False,
            )
        except Exception as e:
            return MCPToolCallResponse(
                content=[MCPToolResponseContent(type="text", text=str(e))],
                isError=True,
            )

    return router
