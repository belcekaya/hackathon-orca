# Design — Travel Agent System

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       ORCA CLOUD                            │
│                    (orchestration)                           │
└──────────────┬────────────────────────────┬─────────────────┘
               │                            │
        User messages               session.ask_agent()
               │                            │
               ▼                            ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│   Consumer Agent     │    │     Provider Agent           │
│   (port 8001)        │    │     (port 8000)              │
│                      │    │                              │
│ • Anthropic Claude   │───▶│ • Anthropic Claude           │
│ • Intent parsing     │    │ • Tool use (API mapping)     │
│ • Provider routing   │    │ • httpx → Travel APIs        │
│ • Response synthesis │    │ • Structured responses       │
│ • Chat history       │    │                              │
│ • Friendly UX        │    │  ┌─────────────────────┐     │
└──────────────────────┘    │  │ Tools:              │     │
                            │  │ • search_hotels     │     │
  At demo time, Consumer    │  │ • book_hotel        │     │
  connects to ALL teams'    │  │ • search_flights    │     │
  providers via Orca        │  │ • book_flight       │     │
                            │  │ • search_restaurants│     │
                            │  │ • book_restaurant   │     │
                            │  │ • search_cars       │     │
                            │  │ • ...               │     │
                            │  └─────────────────────┘     │
                            │            │                  │
                            │            ▼                  │
                            │  ┌─────────────────────┐     │
                            │  │ Booking APIs        │     │
                            │  │ (hacketon-18march-  │     │
                            │  │  api.orcaplatform)  │     │
                            │  └─────────────────────┘     │
                            └──────────────────────────────┘
```

## Key Decisions

### 1. Anthropic Claude (not OpenAI)
**Decision**: Usar Anthropic Claude para ambos agentes.
**Why**: Equipo tiene clave Anthropic. Claude tool use es robusto y eficiente en tokens.

### 2. Tool use para Provider (no prompt engineering manual)
**Decision**: Definir tools como funciones JSON para Claude, no parsear respuestas manualmente.
**Why**: Judging criteria incluye "efficiency" — tool use es más preciso y usa menos tokens que few-shot prompting. Anthropic recomienda esta aproximación.

### 3. httpx para API calls
**Decision**: Usar `httpx` (async) para llamadas HTTP a las booking APIs.
**Why**: Ya está en las dependencias del proyecto, soporta async, manejo robusto de errores.

### 4. Provider responses: datos, no prosa
**Decision**: Provider devuelve datos estructurados (JSON-like text). Consumer formatea para el usuario.
**Why**: Boilerplate README lo recomienda explícitamente. Reduce tokens entre agentes. Consumer puede adaptar formato según contexto.

### 5. Variables from Orca, not .env
**Decision**: API keys vienen de `Variables(data.variables)`, no de variables de entorno.
**Why**: Orca inyecta las keys en cada request. Esto permite que en demo, diferentes providers usen diferentes keys sin reconfigurar.

## File Structure

```
src/hackathon-18march-boilerplate/
├── provider/
│   ├── main.py              ← Entry point + process_message
│   ├── tools.py             ← Anthropic tool definitions (JSON schemas)
│   ├── api_client.py        ← httpx wrapper para booking APIs
│   ├── requirements.txt     ← + anthropic, httpx
│   ├── Dockerfile
│   └── docker-compose.yml
├── consumer/
│   ├── main.py              ← Entry point + process_message
│   ├── requirements.txt     ← + anthropic
│   ├── Dockerfile
│   └── docker-compose.yml
└── README.md
```

## Message Flow

### Provider
```
ChatMessage from Orca
       │
       ▼
 Parse variables (API keys)
       │
       ▼
 Send user question + tool defs to Claude
       │
       ▼
 Claude returns tool_use → execute API call via httpx
       │
       ▼
 Return tool result to Claude → Claude synthesizes short answer
       │
       ▼
 session.stream(answer) → session.close()
```

### Consumer
```
ChatMessage from user (via Orca)
       │
       ▼
 Get chat history (ChatHistoryHelper)
 Get available providers (session.available_agents)
       │
       ▼
 Send to Claude: "user wants X, these providers exist"
       │
       ▼
 Claude decides which provider(s) to call
       │
       ▼
 session.ask_agent(slug, question) for each
       │
       ▼
 Collect responses → send back to Claude for synthesis
       │
       ▼
 session.stream(friendly_response) → session.close()
```

## Error Handling

- **API 4xx/5xx**: httpx catches, returns clear error to Claude, Claude explains to caller
- **Agent timeout**: `session.ask_agent()` raises `RuntimeError` → Consumer explains and suggests retry
- **Agent not found**: `ValueError` from `ask_agent()` → Consumer lists available providers
- **LLM error**: catch in `process_message` → `session.error(msg, exception=e)`

## Token Efficiency Strategy (Judging criteria: Efficiency)

- System prompts cortos y directos (no verbosidad)
- Tool use en vez de few-shot examples
- Provider responde solo datos relevantes (no "Here are the results...")
- Consumer reusa chat history solo últimos N mensajes
- Track usage: `session.usage.track(tokens=N, token_type="total")`
