# Design — Consumer v0

## Architecture

```
User (Orca chat)
       │
       ▼
┌──────────────────────────┐
│   Consumer Agent          │
│   consumer/main.py        │
│                           │
│  1. Variables → API key   │
│  2. available_agents list │
│  3. Claude + tool use     │
│     tool: ask_provider    │
│  4. session.ask_agent()   │
│  5. Claude synthesizes    │
│  6. session.stream()      │
└──────────────────────────┘
       │
       ▼
  Provider(s) via Orca
```

## Key Decisions

### 1. Single file — everything in main.py
**Decision**: Todo el consumer v0 vive en `consumer/main.py`. Sin módulos extras.
**Why**: Hackathon. Minimizar complejidad. Iterar rápido. Un archivo = fácil de desplegar.

### 2. Claude tool use para routing (no if/else)
**Decision**: Claude recibe la lista de providers disponibles y una tool `ask_provider`. Él decide a quién llamar.
**Why**: En demo, habrá providers de TODOS los equipos. No podemos hardcodear slugs. Claude infiere el provider correcto de la descripción.

### 3. Tool loop simple (máximo 1 tool call por turno para v0)
**Decision**: Un ciclo: Claude decide → llama a un provider → Claude sintetiza respuesta.
**Why**: v0 es para tener algo corriendo. Multi-tool viene en v1.

### 4. System prompt mínimo
**Decision**: System prompt de ~100 tokens que explica: "eres un asistente de viaje, estos providers existen, usa ask_provider para delegar".
**Why**: Efficiency es criterio de judging. Menos tokens = mejor score.

## Message Flow

```
ChatMessage
    │
    ├── Variables(data.variables) → ANTHROPIC_API_KEY
    │
    ├── session.available_agents → [{slug, name, description}, ...]
    │
    ├── anthropic.messages.create(
    │     model="claude-sonnet-4-20250514",
    │     system="You are a travel assistant...",
    │     messages=[user_message],
    │     tools=[ask_provider_tool]
    │   )
    │
    ├── if tool_use → session.ask_agent(slug, question)
    │   │
    │   └── anthropic.messages.create(
    │         messages=[...tool_result...],
    │       )
    │
    └── session.stream(final_text) → session.close()
```

## Dependencies
- `anthropic` SDK (add to requirements.txt)
- Orca SDK (already in requirements.txt)
