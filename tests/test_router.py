import asyncio
import json
import unittest
from mcp_router import MCPRouter, MCPResponse


class TestMCPRouter(unittest.TestCase):
    def test_initialize_and_tool_list(self):
        async def run_test():
            router = MCPRouter()

            @router.tool(
                name="calculate_sum",
                description="Adds two integers",
                input_schema={
                    "type": "object",
                    "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                    "required": ["a", "b"],
                },
            )
            def add(a: int, b: int) -> int:
                return a + b

            # 1. Initialize
            init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
            init_res = json.loads(await router.handle_request(init_req))
            self.assertEqual(init_res["result"]["serverInfo"]["name"], "mcp-hub-router")

            # 2. Tools list
            list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
            list_res = json.loads(await router.handle_request(list_req))
            tools = list_res["result"]["tools"]
            self.assertEqual(len(tools), 1)
            self.assertEqual(tools[0]["name"], "calculate_sum")

            # 3. Call tool
            call_req = json.dumps({
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "calculate_sum", "arguments": {"a": 15, "b": 27}},
            })
            call_res = json.loads(await router.handle_request(call_req))
            content = call_res["result"]["content"]
            self.assertEqual(content[0]["text"], "42")

            # 4. Check Telemetry
            summary = router.telemetry.summary()
            self.assertEqual(summary["total_calls"], 1)
            self.assertEqual(summary["success_rate"], 1.0)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
