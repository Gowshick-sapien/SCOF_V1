"""Model Context Protocol (MCP) Client for discovering and invoking tools."""

from typing import Any, Dict, List, Optional
import httpx


class MCPClient:
    """Client for discovering and invoking domain tools over standard MCP protocol."""

    def __init__(self, timeout_sec: float = 5.0):
        self.timeout_sec = timeout_sec

    def list_tools(self, endpoint_url: str) -> List[Dict[str, Any]]:
        """Queries POST /mcp/tools/list on an agent service."""
        url = f"{endpoint_url.rstrip('/')}/mcp/tools/list"
        with httpx.Client(timeout=self.timeout_sec) as client:
            response = client.post(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("tools", [])
            return []

    def call_tool(
        self, endpoint_url: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Queries POST /mcp/tools/call on an agent service."""
        url = f"{endpoint_url.rstrip('/')}/mcp/tools/call"
        payload = {"name": tool_name, "arguments": arguments}
        with httpx.Client(timeout=self.timeout_sec) as client:
            response = client.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            return {
                "content": [{"type": "text", "text": f"HTTP {response.status_code}: {response.text}"}],
                "isError": True,
            }
