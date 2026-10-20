
import asyncio
import json
import sys
from contextlib import AsyncExitStack
from pathlib import Path

import ollama
from mcp import Client, StdioServerParameters

BASE_DIR = Path(__file__).parent
MODEL = "qwen3:4b"

SERVER_FILES = {
    "tasks": BASE_DIR / "task_server.py",
    "notes": BASE_DIR / "notes_server.py",
    "math": BASE_DIR / "math_server.py",
}



def to_ollama_tool(tool):
    """Convert an MCP tool definition into Ollama's tool format."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or tool.name,
            "parameters": tool.input_schema,
        },
    }



def result_to_text(result):
    """Convert an MCP tool result into text for the model."""
    if result.structuredContent is not None:
        return json.dumps(result.structuredContent, ensure_ascii=False)

    parts = []

    for item in result.content:
        if hasattr(item, "text"):
            parts.append(item.text)
        else:
            parts.append(str(item))

    return "\n".join(parts) or "Tool completed without text output."


async def main():
    ollama_client = ollama.AsyncClient()

    async with AsyncExitStack() as stack:
        sessions = {}
        tool_routes = {}
        all_tools = []

        # 1. Launch and connect to all three MCP servers.
        for server_name, script_path in SERVER_FILES.items():
            params = StdioServerParameters(
                command=sys.executable,
                args=[str(script_path)],
            )

            client = await stack.enter_async_context(Client(params))
            sessions[server_name] = client

            # 2. Discover the tools exposed by this server.
            response = await client.list_tools()

            print(f"\nConnected to {server_name} server:")

            for tool in response.tools:
                # Prefix names to avoid collisions across servers.
                public_name = f"{server_name}__{tool.name}"

                tool_routes[public_name] = (
                    client,
                    tool.name,
                )

                # Give Ollama a unique name and the MCP input schema.
                definition = to_ollama_tool(tool)
                definition["function"]["name"] = public_name
                all_tools.append(definition)

                print(f"  - {public_name}")

        print(f"\nLoaded {len(all_tools)} tools.")
        print("Type 'exit' to quit.\n")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful personal assistant. "
                    "Use the available tools when the user asks you to "
                    "manage tasks, save or search notes, or calculate "
                    "values. Do not claim a tool succeeded unless its "
                    "result confirms success."
                ),
            }
        ]

        # 3. Start the conversation.
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                break

            if not user_input:
                continue

            messages.append({
                "role": "user",
                "content": user_input,
            })

            # 4. Ask Ollama whether it needs to call tools.
            for _ in range(5):
                response = await ollama_client.chat(
                    model=MODEL,
                    messages=messages,
                    tools=all_tools,
                )

                assistant_message = response.message
                messages.append(assistant_message)

                if not assistant_message.tool_calls:
                    print(f"\nAssistant: {assistant_message.content}\n")
                    break

                # 5. Route each model-requested tool to its MCP server.
                for call in assistant_message.tool_calls:
                    public_name = call.function.name
                    arguments = call.function.arguments

                    if public_name not in tool_routes:
                        tool_output = f"Unknown tool: {public_name}"
                    else:
                        client, original_name = tool_routes[public_name]

                        print(f"Calling {public_name}({arguments})")

                        try:
                            result = await client.call_tool(
                                original_name,
                                arguments=arguments,
                            )
                            tool_output = result_to_text(result)

                            if result.isError:
                                tool_output = f"Tool error: {tool_output}"

                        except Exception as exc:
                            tool_output = (
                                f"Tool execution failed: "
                                f"{type(exc).__name__}: {exc}"
                            )

                    # 6. Return the result to Ollama.
                    messages.append({
                        "role": "tool",
                        "tool_name": public_name,
                        "content": tool_output,
                    })
            else:
                print(
                    "\nAssistant: Stopped after 5 tool-calling rounds. "
                    "Please try a simpler request.\n"
                )


if __name__ == "__main__":
    asyncio.run(main())
