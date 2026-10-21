import asyncio
import inspect
import json
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from .protocol import MCPError, MCPResponse, MCPToolDefinition
from .telemetry import RouterTelemetry


class MCPRouter:
    """Production-grade Model Context Protocol (MCP) tool gateway router."""

    def __init__(self, server_name: str = "mcp-hub-router", server_version: str = "0.1.0"):
        self.server_name = server_name
        self.server_version = server_version
        self._tools: Dict[str, Tuple[MCPToolDefinition, Callable[..., Any]]] = {}
        self.telemetry = RouterTelemetry()

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        definition = MCPToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
        )
        self._tools[name] = (definition, handler)

    def tool(self, name: str, description: str, input_schema: Optional[Dict[str, Any]] = None) -> Callable:
        schema = input_schema or {"type": "object", "properties": {}}

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.register_tool(name=name, description=description, input_schema=schema, handler=fn)
            return fn

        return decorator

    async def handle_request(self, request_json: str) -> str:
        """Process incoming raw JSON-RPC string and return JSON-RPC response string."""
        req_id = None
        try:
            req = json.loads(request_json)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if not method:
                raise MCPError(-32600, "Invalid Request: missing method")

            result = await self.dispatch(method, params)
            response = {"jsonrpc": "2.0", "id": req_id, "result": result}
        except MCPError as e:
            response = {"jsonrpc": "2.0", "id": req_id, "error": e.to_dict()}
        except Exception as e:
            response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}

        return json.dumps(response)

    async def dispatch(self, method: str, params: Dict[str, Any]) -> Any:
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {"name": self.server_name, "version": self.server_version},
            }
        elif method == "ping":
            return {}
        elif method == "tools/list":
            tools_list = [t[0].to_mcp_format() for t in self._tools.values()]
            return {"tools": tools_list}
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            return await self.execute_tool(tool_name, args)
        else:
            raise MCPError(-32601, f"Method not found: {method}")

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._tools:
            raise MCPError(-32602, f"Unknown tool: {name}")

        definition, handler = self._tools[name]
        start_time = time.time()
        try:
            if inspect.iscoroutinefunction(handler):
                res = await handler(**arguments)
            else:
                res = handler(**arguments)

            duration_ms = (time.time() - start_time) * 1000
            self.telemetry.record(tool_name=name, duration_ms=duration_ms, success=True)

            if isinstance(res, MCPResponse):
                return res.to_dict()
            elif isinstance(res, dict) and "content" in res:
                return res
            else:
                return MCPResponse.text(str(res)).to_dict()
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.telemetry.record(tool_name=name, duration_ms=duration_ms, success=False, error_msg=str(e))
            return MCPResponse.text(f"Error executing {name}: {str(e)}", is_error=True).to_dict()


def mcp_tool(
    router: MCPRouter,
    name: str,
    description: str,
    input_schema: Optional[Dict[str, Any]] = None,
) -> Callable:
    return router.tool(name=name, description=description, input_schema=input_schema)
