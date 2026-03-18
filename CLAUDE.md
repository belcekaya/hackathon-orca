# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run dev server (auto-reload)
uv run uvicorn hackathon.api.app:app --reload

# Lint
uv run ruff check src/
uv run ruff format --check src/

# Fix lint/format
uv run ruff check --fix src/
uv run ruff format src/

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_file.py::test_name
```

## Architecture

Python 3.12 project using **uv** for package management, **FastAPI** for the API layer, and **Agno** for AI agent orchestration.

- **`src/hackathon/api/`** — FastAPI app and routes. `app.py` is the ASGI entrypoint (`hackathon.api.app:app`). Routes are in `routes/` and mounted via `include_router`.
- **`src/hackathon/agents/`** — Agno `Agent` definitions (research, assistant). Each agent is a module-level singleton configured with a model and instructions.
- **`src/hackathon/infrastructure/config/settings.py`** — Pydantic Settings loaded from `.env`. Singleton `settings` instance imported throughout.
- **`src/hackathon/domain/`** — Domain entities and services (currently scaffolded).

## Key Details

- Ruff is configured with line-length 100 and rules: E, F, I, B, UP, S, RET, W (S101 ignored to allow `assert` in tests).
- Agents use `OpenAIChat(id="gpt-4o-mini")` by default — requires `OPENAI_API_KEY` in `.env`.
- Copy `.env.example` to `.env` for local configuration.
