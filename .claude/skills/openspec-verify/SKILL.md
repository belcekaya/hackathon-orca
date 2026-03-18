---
name: openspec-verify
description: Verify an implemented change against its spec scenarios and acceptance criteria.
---

Verify that the implementation matches the spec.

## Steps

1. Read `openspec/changes/<slug>/specs/` for all requirements and scenarios
2. Read `openspec/changes/<slug>/tasks.md` — confirm all checkboxes are `[x]`
3. For each scenario in the spec:
   - Find the corresponding source code that implements the scenario
   - Verify the implementation covers the WHEN/THEN conditions
   - Flag any scenario without a matching implementation
4. Run linting: `uv run ruff check src/`
5. Run tests: `uv run pytest tests/ -v`
6. Verify API endpoints: `uv run python -c "from hackathon.api.app import app; print(f'{len(app.routes)} routes registered')"`

## Report Format

```
## Verification: <change-name>

### Spec Coverage
- [x] Scenario: <name> — implemented in <file>
- [ ] Scenario: <name> — MISSING IMPLEMENTATION

### Quality Gates
- Ruff lint: PASS/FAIL
- Tests: PASS/FAIL
- API routes: PASS/FAIL (X routes)

### Tasks Completion
- X/Y tasks completed in tasks.md

### Verdict
PASS — ready to archive / FAIL — issues listed above
```
