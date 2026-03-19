import logging

import anthropic
from orca import ChatHistoryHelper, ChatMessage, OrcaHandler, Variables, create_agent_app

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Coral, a friendly and efficient travel concierge. You speak in a warm, professional tone and use markdown formatting to make responses scannable.

Rules:
- Delegate to providers via ask_provider. Call MULTIPLE providers in parallel when the user asks about different travel categories (e.g. hotel + car + restaurant).
- Keep your questions to providers specific and data-rich (include dates, location, guest count, etc.).
- Format final answers with clear sections, bullet points, and key details highlighted in **bold**.
- If no provider matches, say so and suggest what you CAN help with.
- Be concise. Users want answers, not essays.

Available providers:
{agents}"""

ASK_PROVIDER_TOOL = {
    "name": "ask_provider",
    "description": (
        "Ask a provider agent a travel-related question. "
        "Pick the provider whose description best matches. "
        "You can call this tool multiple times in one turn to query several providers in parallel."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "slug": {
                "type": "string",
                "description": "The slug of the provider agent to ask",
            },
            "question": {
                "type": "string",
                "description": "A specific, detailed question for the provider",
            },
        },
        "required": ["slug", "question"],
    },
}


def _build_chat_messages(data: ChatMessage) -> list[dict]:
    """Convert Orca chat history into Anthropic messages format."""
    messages = []
    history = ChatHistoryHelper(data.chat_history)
    for msg in history.get_last_n_messages(10):
        role = "user" if msg.role == "user" else "assistant"
        # Avoid consecutive same-role messages
        if messages and messages[-1]["role"] == role:
            messages[-1]["content"] += f"\n{msg.content}"
        else:
            messages.append({"role": role, "content": msg.content})

    # Always end with current user message
    if messages and messages[-1]["role"] == "user":
        messages[-1]["content"] += f"\n{data.message}"
    else:
        messages.append({"role": "user", "content": data.message})
    return messages


def _serialize_content(content) -> list[dict]:
    """Serialize Anthropic content blocks for the messages API."""
    result = []
    for block in content:
        if block.type == "text":
            result.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            result.append(
                {
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                }
            )
    return result


async def process_message(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)
    total_tokens = 0

    try:
        variables = Variables(data.variables)
        api_key = variables.get("ANTHROPIC_API_KEY")

        # Build provider list
        agents_list = "\n".join(
            f"- **{a.slug}**: {a.name} — {a.description}" for a in session.available_agents
        )

        client = anthropic.Anthropic(api_key=api_key)
        system = SYSTEM_PROMPT.format(agents=agents_list or "No providers connected yet.")

        # Build messages with chat history for context
        messages = _build_chat_messages(data)

        session.loading.start("thinking")

        # First LLM call — route intent
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            system=system,
            messages=messages,
            tools=[ASK_PROVIDER_TOOL],
        )
        total_tokens += response.usage.input_tokens + response.usage.output_tokens

        session.loading.end("thinking")

        # Tool use loop — handle multiple provider calls per turn
        max_rounds = 5
        round_count = 0
        while response.stop_reason == "tool_use" and round_count < max_rounds:
            round_count += 1

            # Collect ALL tool_use blocks (parallel provider calls)
            tool_blocks = [b for b in response.content if b.type == "tool_use"]

            session.loading.start("asking providers")

            # Execute all provider calls
            tool_results = []
            for tool_block in tool_blocks:
                slug = tool_block.input["slug"]
                question = tool_block.input["question"]
                try:
                    provider_response = session.ask_agent(slug, question)
                except (ValueError, RuntimeError) as e:
                    provider_response = f"Provider '{slug}' unavailable: {e}"

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": str(provider_response),
                    }
                )

            session.loading.end("asking providers")

            # Append assistant turn + all tool results
            messages.append({"role": "assistant", "content": _serialize_content(response.content)})
            messages.append({"role": "user", "content": tool_results})

            session.loading.start("preparing answer")

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system,
                messages=messages,
                tools=[ASK_PROVIDER_TOOL],
            )
            total_tokens += response.usage.input_tokens + response.usage.output_tokens

            session.loading.end("preparing answer")

        # Extract final text
        final_text = "".join(b.text for b in response.content if hasattr(b, "text"))
        session.stream(final_text or "I couldn't process that request. Could you rephrase?")

        # Track token usage
        session.usage.track(tokens=total_tokens, token_type="total")
        session.close()

    except Exception as e:
        logger.exception("Error processing message")
        session.error("Something went wrong. Please try again.", exception=e)


app, orca = create_agent_app(
    process_message_func=process_message,
    title="Coral — Travel Concierge",
    description="Personal travel assistant that delegates to specialized provider agents",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
