"""Assistant agent using Agno framework."""

from agno.agent import Agent
from agno.models.openai import OpenAIChat


assistant_agent = Agent(
    name="Assistant Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You are a helpful assistant that answers questions and helps with tasks.",
        "Be friendly and professional in your responses.",
        "Ask clarifying questions when needed.",
    ],
    markdown=True,
)
