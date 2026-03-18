# AGENTS.md

Instructions for AI coding agents working on this repository.

## Setup

```bash
# Install dependencies (requires uv: https://docs.astral.sh/uv/)
uv sync

# Copy environment file and add your API keys
cp .env.example .env

# Run provider agent (port 8000)
cd src/hackathon-18march-boilerplate/provider
pip install -r requirements.txt
python main.py

# Run consumer agent (port 8001) — separate terminal
cd src/hackathon-18march-boilerplate/consumer
pip install -r requirements.txt
python main.py
```

## Code style

- Python 3.13+ — use modern syntax (type unions with `|`, `match` statements, etc.)
- Ruff for linting and formatting — line-length 100
- Lint rules: E, F, I, B, UP, S, RET, W (S101 ignored in tests to allow `assert`)
- Use `from __future__ import annotations` only if needed for forward refs
- Imports sorted by isort (handled by Ruff `I` rule)

```bash
# Check lint and format
uv run ruff check src/
uv run ruff format --check src/

# Auto-fix
uv run ruff check --fix src/
uv run ruff format src/
```

## Testing

```bash
# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_file.py::test_name
```

- Use `pytest-asyncio` for async tests
- Place tests in `tests/` mirroring the `src/` structure
- Always run tests after making changes to verify nothing is broken

## Architecture

**Orca SDK** (`orca-platform-sdk-ui`) / **Anthropic Claude** / Python 3.13 / FastAPI (via Orca).

Two agents that communicate through Orca orchestration:

```
src/hackathon-18march-boilerplate/
├── provider/
│   ├── main.py              ← Provider agent (wraps travel APIs)
│   ├── requirements.txt     ← orca-platform-sdk-ui, uvicorn, fastapi
│   ├── Dockerfile
│   └── docker-compose.yml
├── consumer/
│   ├── main.py              ← Consumer agent (user-facing assistant)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
└── README.md                ← Full Orca SDK cheat sheet
```

### Provider Agent (port 8000)
- Connects to assigned travel APIs (hotel, restaurant, flight, car rental, tour, museum)
- Uses Anthropic Claude for NLU + tool use to map requests to API calls
- Returns concise, structured results to consumer agents
- Called by consumer agents via `session.ask_agent()`

### Consumer Agent (port 8001)
- Personal AI assistant facing end users
- Delegates to provider agents via `session.ask_agent("agent-slug", "question")`
- Synthesizes responses into friendly, formatted replies
- At demo time, connects to ALL provider agents from every team

### Orca SDK Key APIs
```python
from orca import create_agent_app, ChatMessage, OrcaHandler, Variables, ChatHistoryHelper

# Agent lifecycle
handler = OrcaHandler()
session = handler.begin(data)
session.stream("response text")
session.close()

# Variables (API keys delivered by Orca, not env vars)
variables = Variables(data.variables)
api_key = variables.get("ANTHROPIC_API_KEY")

# Agent-to-agent
response = session.ask_agent("agent-slug", "question")
for agent in session.available_agents:
    print(agent.slug, agent.name)

# Loading indicators
session.loading.start("thinking")
session.loading.end("thinking")

# Chat history
history = ChatHistoryHelper(data.chat_history)
recent = history.get_last_n_messages(10)

# Usage tracking
session.usage.track(tokens=1500, token_type="total")
```

## Environment

- Requires `ANTHROPIC_API_KEY` (agents use Anthropic Claude via tool use)
- API keys are delivered via Orca variables at runtime, not `.env`
- `ORCA_API_URL` and `ORCA_API_KEY` for CLI auth
- Never commit `.env` — it's in `.gitignore`

## Judging Criteria

| Criteria | Description |
|----------|-------------|
| **Functionality** | Does it work? Rate useful outputs (out of 10). |
| **API Integration** | Number and relevance of travel APIs used. |
| **Efficiency** | Optimization of prompts and tokens per request. |

## Conventions

- Use `pip` for the boilerplate agents (not `uv run` — Orca SDK uses pip)
- Use Anthropic tool use for mapping natural language to API calls
- Keep provider responses **short and structured** — consumer formats for users
- API keys come from `Variables(data.variables)`, not environment variables
- Async handlers in `process_message(data: ChatMessage)`
