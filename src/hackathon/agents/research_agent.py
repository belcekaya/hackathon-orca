"""Research agent using Agno framework."""

from agno.agent import Agent
from agno.models.openai import OpenAIChat


research_agent = Agent(
    name="Research Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You are a research assistant that helps find and synthesize information.",
        "Always cite your sources when providing information.",
        "Be concise but thorough in your responses.",
    ],
    markdown=True,
)
