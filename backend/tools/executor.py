"""Multi-turn tool-calling execution loop."""

from backend.providers.base import BaseProvider, ProviderResponse
from backend.tools.registry import get_tools, has_tools

MAX_TOOL_ITERATIONS = 5


def _format_schemas(tools, provider_name: str) -> list[dict]:
    """Format tool schemas for the given provider."""
    if provider_name == "anthropic":
        return [t.to_anthropic_schema() for t in tools]
    if provider_name == "google":
        return [t.to_google_schema() for t in tools]
    return [t.to_openai_schema() for t in tools]


def _format_tool_result(tool_call_id: str, tool_name: str, result_message: str, provider_name: str) -> dict:
    """Format a tool result as a message for re-injection into the conversation."""
    if provider_name == "anthropic":
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call_id,
                    "content": result_message,
                }
            ],
        }
    # OpenAI-compatible (openai, grok, groq, deepseek, mistral, etc.)
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": tool_name,
        "content": result_message,
    }


async def execute_with_tools(
    provider: BaseProvider,
    messages: list[dict],
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    system_prompt: str | None = None,
    specialist_id: str | None = None,
) -> ProviderResponse:
    """Execute a provider call, invoking tools if the specialist has any registered.

    For specialists with no registered tools this is a zero-overhead passthrough
    to ``provider.send_message()``.
    """
    if not specialist_id or not has_tools(specialist_id):
        return await provider.send_message(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

    tools = get_tools(specialist_id)
    tool_schemas = _format_schemas(tools, provider.name)
    tool_map = {t.name: t for t in tools}

    current_messages = list(messages)

    for _ in range(MAX_TOOL_ITERATIONS):
        response = await provider.send_message_with_tools(
            messages=current_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            tools=tool_schemas,
        )

        if not response.tool_calls:
            return response

        # Append assistant message with tool-call info in the provider's expected format
        if provider.name == "anthropic":
            assistant_content = [
                {
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc.get("arguments", {}),
                }
                for tc in response.tool_calls
            ]
            if response.content:
                assistant_content.insert(0, {"type": "text", "text": response.content})
            current_messages.append({"role": "assistant", "content": assistant_content})
        else:
            current_messages.append({
                "role": "assistant",
                "content": response.content or "",
                "tool_calls": response.tool_calls,
            })

        # Execute each requested tool and inject results
        for tc in response.tool_calls:
            tool = tool_map.get(tc["name"])
            if tool is None:
                result_text = f"Unknown tool: {tc['name']}"
            else:
                result = await tool.execute(**tc.get("arguments", {}))
                result_text = result.as_message

            current_messages.append(
                _format_tool_result(tc["id"], tc["name"], result_text, provider.name)
            )

    # Fallback: final call without tools to get a text response
    return await provider.send_message(
        messages=current_messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
    )
