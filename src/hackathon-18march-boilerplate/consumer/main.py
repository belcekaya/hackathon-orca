import logging

import anthropic
from orca import ChatMessage, OrcaHandler, Variables, create_agent_app

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a travel assistant. You help users with travel-related requests.

Available provider agents:
{agents}

Use the ask_provider tool to delegate requests to the right provider based on its description. If no provider matches, say so politely."""

ASK_PROVIDER_TOOL = {
    "name": "ask_provider",
    "description": "Ask a provider agent a travel-related question. Pick the provider whose description best matches the user's request.",
    "input_schema": {
        "type": "object",
        "properties": {
            "slug": {
                "type": "string",
                "description": "The slug of the provider agent to ask",
            },
            "question": {
                "type": "string",
                "description": "The question to send to the provider",
            },
        },
        "required": ["slug", "question"],
    },
}


async def process_message(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    try:
        variables = Variables(data.variables)
        api_key = variables.get("ANTHROPIC_API_KEY")

        # Build provider list for Claude
        agents_list = "\n".join(
            f"- {a.slug}: {a.name} — {a.description}" for a in session.available_agents
        )

        client = anthropic.Anthropic(api_key=api_key)
        system = SYSTEM_PROMPT.format(agents=agents_list or "No providers connected yet.")

        # First call: Claude decides whether to delegate
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": data.message}],
            tools=[ASK_PROVIDER_TOOL],
        )

        # Handle tool use loop
        messages = [{"role": "user", "content": data.message}]
        while response.stop_reason == "tool_use":
            tool_block = next(b for b in response.content if b.type == "tool_use")
            slug = tool_block.input["slug"]
            question = tool_block.input["question"]

            # Delegate to provider via Orca
            try:
                provider_response = session.ask_agent(slug, question)
            except (ValueError, RuntimeError) as e:
                provider_response = f"Provider '{slug}' is unavailable: {e}"

            # Send tool result back to Claude for synthesis
            messages.append({"role": "assistant", "content": response.content})
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,
                            "content": str(provider_response),
                        }
                    ],
                }
            )

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system,
                messages=messages,
                tools=[ASK_PROVIDER_TOOL],
            )

        # Extract final text and stream to user
        final_text = "".join(b.text for b in response.content if hasattr(b, "text"))
        session.stream(final_text or "I couldn't process that request.")
        session.close()

    except Exception as e:
        logger.exception("Error processing message")
        session.error("Something went wrong.", exception=e)


app, orca = create_agent_app(
    process_message_func=process_message,
    title="Consumer Agent",
    description="Personal travel assistant with agent delegation",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
