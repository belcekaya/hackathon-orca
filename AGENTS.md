# AGENTS.md

Instructions for AI coding agents working on this repository.

## Setup

```bash
# Install dependencies (requires uv: https://docs.astral.sh/uv/)
uv sync

# Copy environment file and add your API keys
cp .env.example .env

# Run dev server (auto-reload on port 8000)
uv run uvicorn hackathon.api.app:app --reload
```

## Code style

- Python 3.12+ — use modern syntax (type unions with `|`, `match` statements, etc.)
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
- Place tests in `tests/` mirroring the `src/hackathon/` structure
- Always run tests after making changes to verify nothing is broken

## Architecture

Python 3.12 / FastAPI / Agno agents / Pydantic Settings.

```
src/hackathon/
├── api/              # FastAPI app and routes
│   ├── app.py        # ASGI entrypoint (hackathon.api.app:app)
│   └── routes/       # Route modules mounted via include_router
├── agents/           # Agno Agent singletons (research, assistant)
├── domain/           # Domain entities and services
│   ├── entities/
│   └── services/
└── infrastructure/   # Config and external integrations
    └── config/       # Pydantic Settings from .env
```

- **Routes**: add new route modules in `api/routes/`, then mount in `app.py` with `include_router`
- **Agents**: each agent is a module-level singleton in `agents/`, exported via `__init__.py`
- **Config**: `infrastructure/config/settings.py` — Pydantic `BaseSettings` loaded from `.env`, import the `settings` singleton

## Environment

- Requires `OPENAI_API_KEY` in `.env` (agents use `OpenAIChat(id="gpt-4o-mini")`)
- Optional: `ANTHROPIC_API_KEY`, `LOG_LEVEL`
- Never commit `.env` — it's in `.gitignore`

## Conventions

- Use `uv run` to execute all Python commands (not raw `python` or `pip`)
- Keep agent instructions as lists of strings in the Agent constructor
- Pydantic `BaseModel` for all request/response schemas in routes
- Async route handlers (`async def`)
