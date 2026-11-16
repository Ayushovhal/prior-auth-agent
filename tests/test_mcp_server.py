import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from mcp_server.server import mcp

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ["check_criteria", "draft_request", "get_patient", "search_policy"]


def test_server_registers_four_tools():
    async def listed() -> list[str]:
        tools = await mcp.list_tools()
        return sorted(tool.name for tool in tools)

    assert asyncio.run(listed()) == EXPECTED


def test_tool_descriptions_name_what_they_return():
    async def described() -> dict[str, str]:
        tools = await mcp.list_tools()
        return {tool.name: tool.description or "" for tool in tools}

    text = asyncio.run(described())
    assert "synthetic" in text["get_patient"].lower()
    assert "section_id" in text["search_policy"]
    assert "ready to submit" in text["check_criteria"]
    assert "citation" in text["draft_request"].lower()


def test_get_patient_tool_returns_chart():
    async def called() -> object:
        return await mcp.call_tool("get_patient", {"patient_id": "pat-001"})

    assert "pat-001" in str(asyncio.run(called()))


def test_unknown_patient_is_an_error_object():
    async def called() -> object:
        return await mcp.call_tool("get_patient", {"patient_id": "pat-999"})

    assert "unknown patient" in str(asyncio.run(called()))


def test_stdio_server_lists_tools():
    """The server has to answer a real MCP client, which is what the inspector does."""

    async def listed() -> list[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server.server"],
            cwd=str(ROOT),
            env=env,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return sorted(tool.name for tool in result.tools)

    assert asyncio.run(listed()) == EXPECTED
