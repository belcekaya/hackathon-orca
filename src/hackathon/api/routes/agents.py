"""Agent routes."""

from fastapi import APIRouter
from pydantic import BaseModel

from hackathon.agents import research_agent, assistant_agent

router = APIRouter()


class AgentRequest(BaseModel):
    """Request model for agent endpoints."""

    message: str


class AgentResponse(BaseModel):
    """Response model for agent endpoints."""

    response: str


@router.post("/research", response_model=AgentResponse)
async def research(request: AgentRequest) -> AgentResponse:
    """Run research agent."""
    response = research_agent.run(request.message)
    return AgentResponse(response=response.content)


@router.post("/assistant", response_model=AgentResponse)
async def assistant(request: AgentRequest) -> AgentResponse:
    """Run assistant agent."""
    response = assistant_agent.run(request.message)
    return AgentResponse(response=response.content)
