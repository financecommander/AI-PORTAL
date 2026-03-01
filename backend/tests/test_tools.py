"""Tests for tools infrastructure: registry, executor, skiptrace tool, and base classes."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from backend.tools.base import BaseTool, ToolResult
from backend.tools.registry import register_tools, get_tools, has_tools, list_all
from backend.tools.skiptrace_tool import SkipTraceTool
from backend.tools.executor import execute_with_tools, _format_schemas, _format_tool_result
from backend.providers.base import ProviderResponse


# ── ToolResult tests ───────────────────────────────────────────


def test_tool_result_success_as_message():
    result = ToolResult(tool_name="my_tool", success=True, data={"key": "val"})
    msg = result.as_message
    assert '"key"' in msg
    assert '"val"' in msg


def test_tool_result_failure_as_message():
    result = ToolResult(tool_name="my_tool", success=False, data={}, error="Something failed")
    msg = result.as_message
    assert "my_tool" in msg
    assert "Something failed" in msg


# ── BaseTool schema helpers ────────────────────────────────────


class DummyTool(BaseTool):
    @property
    def name(self) -> str:
        return "dummy"

    @property
    def description(self) -> str:
        return "A dummy tool"

    @property
    def parameters(self) -> dict:
        return {"type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(tool_name=self.name, success=True, data={"x": kwargs.get("x")})


def test_to_openai_schema():
    tool = DummyTool()
    schema = tool.to_openai_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "dummy"
    assert schema["function"]["description"] == "A dummy tool"
    assert "parameters" in schema["function"]


def test_to_anthropic_schema():
    tool = DummyTool()
    schema = tool.to_anthropic_schema()
    assert schema["name"] == "dummy"
    assert schema["description"] == "A dummy tool"
    assert "input_schema" in schema


def test_to_google_schema():
    tool = DummyTool()
    schema = tool.to_google_schema()
    assert schema["name"] == "dummy"
    assert "parameters" in schema


# ── Registry tests ─────────────────────────────────────────────


def test_register_and_get_tools():
    tool = DummyTool()
    register_tools("_test_specialist_", [tool])
    tools = get_tools("_test_specialist_")
    assert len(tools) == 1
    assert tools[0].name == "dummy"


def test_has_tools_true():
    register_tools("_test_has_", [DummyTool()])
    assert has_tools("_test_has_") is True


def test_has_tools_false():
    assert has_tools("_nonexistent_specialist_") is False


def test_get_tools_empty_for_unknown():
    assert get_tools("_unknown_specialist_") == []


def test_list_all_includes_registered():
    register_tools("_list_test_", [DummyTool()])
    summary = list_all()
    assert "_list_test_" in summary
    assert "dummy" in summary["_list_test_"]


# ── SkipTraceTool tests ────────────────────────────────────────


@pytest.mark.asyncio
async def test_skiptrace_execute_success():
    tool = SkipTraceTool()
    result = await tool.execute(full_name="John Doe", state="TX")
    assert result.success is True
    assert result.tool_name == "skiptrace_search"
    assert result.data["query"]["full_name"] == "John Doe"
    assert "disclaimer" in result.data


@pytest.mark.asyncio
async def test_skiptrace_execute_missing_name():
    tool = SkipTraceTool()
    result = await tool.execute(full_name="")
    assert result.success is False
    assert result.error is not None


@pytest.mark.asyncio
async def test_skiptrace_execute_no_args():
    tool = SkipTraceTool()
    result = await tool.execute()
    assert result.success is False


def test_skiptrace_name():
    assert SkipTraceTool().name == "skiptrace_search"


def test_skiptrace_parameters_required():
    params = SkipTraceTool().parameters
    assert "full_name" in params["required"]


# ── Executor helpers ───────────────────────────────────────────


def test_format_schemas_anthropic():
    tools = [DummyTool()]
    schemas = _format_schemas(tools, "anthropic")
    assert schemas[0]["name"] == "dummy"
    assert "input_schema" in schemas[0]


def test_format_schemas_google():
    tools = [DummyTool()]
    schemas = _format_schemas(tools, "google")
    assert schemas[0]["name"] == "dummy"
    assert "parameters" in schemas[0]


def test_format_schemas_openai_default():
    tools = [DummyTool()]
    schemas = _format_schemas(tools, "openai")
    assert schemas[0]["type"] == "function"


def test_format_tool_result_openai():
    msg = _format_tool_result("id-1", "dummy", "result text", "openai")
    assert msg["role"] == "tool"
    assert msg["tool_call_id"] == "id-1"
    assert msg["content"] == "result text"


def test_format_tool_result_anthropic():
    msg = _format_tool_result("id-2", "dummy", "result text", "anthropic")
    assert msg["role"] == "user"
    assert msg["content"][0]["type"] == "tool_result"
    assert msg["content"][0]["tool_use_id"] == "id-2"


# ── Executor: no-tools passthrough ────────────────────────────


@pytest.mark.asyncio
async def test_execute_with_tools_no_tools_passthrough():
    """Specialists without tools call send_message directly."""
    mock_provider = AsyncMock()
    mock_response = ProviderResponse(
        content="Hello", model="test", input_tokens=5, output_tokens=10, latency_ms=50.0
    )
    mock_provider.send_message = AsyncMock(return_value=mock_response)
    mock_provider.name = "openai"

    result = await execute_with_tools(
        provider=mock_provider,
        messages=[{"role": "user", "content": "hi"}],
        model="gpt-4o",
        specialist_id="_no_tools_specialist_",
    )

    mock_provider.send_message.assert_called_once()
    mock_provider.send_message_with_tools.assert_not_called()
    assert result.content == "Hello"


@pytest.mark.asyncio
async def test_execute_with_tools_none_specialist_passthrough():
    """specialist_id=None calls send_message directly."""
    mock_provider = AsyncMock()
    mock_response = ProviderResponse(
        content="Hi", model="test", input_tokens=5, output_tokens=5, latency_ms=10.0
    )
    mock_provider.send_message = AsyncMock(return_value=mock_response)

    result = await execute_with_tools(
        provider=mock_provider,
        messages=[{"role": "user", "content": "hi"}],
        model="gpt-4o",
        specialist_id=None,
    )

    mock_provider.send_message.assert_called_once()
    assert result.content == "Hi"


@pytest.mark.asyncio
async def test_execute_with_tools_with_tool_call():
    """When provider returns tool_calls, tools are executed and result injected."""
    register_tools("_exec_test_", [DummyTool()])

    mock_provider = AsyncMock()
    mock_provider.name = "openai"

    # First call returns a tool call; second call returns final text
    tool_response = ProviderResponse(
        content="", model="test", input_tokens=5, output_tokens=5, latency_ms=10.0,
        tool_calls=[{"id": "call-1", "name": "dummy", "arguments": {"x": "hello"}}],
    )
    final_response = ProviderResponse(
        content="Done!", model="test", input_tokens=10, output_tokens=10, latency_ms=20.0,
    )
    mock_provider.send_message_with_tools = AsyncMock(side_effect=[tool_response, final_response])

    result = await execute_with_tools(
        provider=mock_provider,
        messages=[{"role": "user", "content": "run dummy"}],
        model="gpt-4o",
        specialist_id="_exec_test_",
    )

    assert result.content == "Done!"
    assert mock_provider.send_message_with_tools.call_count == 2


# ── register_all_tools ─────────────────────────────────────────


def test_register_all_tools_registers_skiptrace():
    from backend.tools import register_all_tools
    register_all_tools()
    assert has_tools("skiptrace")
    tools = get_tools("skiptrace")
    assert any(t.name == "skiptrace_search" for t in tools)
