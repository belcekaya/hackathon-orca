# Hackathon Agno Template

A hackathon starter template with Agno agents and FastAPI.

## Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Copy environment file
cp .env.example .env
# Edit .env with your API keys
```

## Run

```bash
# Start the API server
uv run uvicorn hackathon.api.app:app --reload
```

## API Endpoints

- `GET /health` - Health check
- `POST /agents/research` - Run research agent
- `POST /agents/assistant` - Run assistant agent

## Project Structure

```
src/hackathon/
├── agents/           # Agno agent definitions
├── api/              # FastAPI routes
├── domain/           # Domain entities and services
└── infrastructure/   # Config and external services
```
