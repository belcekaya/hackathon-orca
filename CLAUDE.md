# CLAUDE.md

See @AGENTS.md for setup commands, code style, testing, and architecture.

## Workflow

- IMPORTANT: Always run `uv run ruff check src/ && uv run ruff format --check src/` before considering a task done
- Prefer running single tests over the full suite for speed
- When adding a new route, verify the server starts: `uv run uvicorn hackathon.api.app:app --host 0.0.0.0 --port 8000 &` then test with `curl`

## When compacting

When compacting, always preserve the full list of modified files and any test commands that were run.
