# Orca Integration

Integración con la plataforma Orca usando el SDK `orca-platform-sdk-ui`.

## Context

Orca es un Agentic AI Gateway que orquesta la comunicación entre agentes. No escribimos endpoints raw — el SDK crea la app FastAPI y gestiona el endpoint `/api/v1/send_message` internamente.

## SDK

**Package**: `pip install orca-platform-sdk-ui`

### Core API

```python
from orca import create_agent_app, ChatMessage, OrcaHandler, Variables, ChatHistoryHelper

async def process_message(data: ChatMessage):
    handler = OrcaHandler()
    session = handler.begin(data)

    # Read variables (API keys injected by Orca)
    variables = Variables(data.variables)
    api_key = variables.get("ANTHROPIC_API_KEY")

    # Stream response
    session.stream("response text")
    session.close()

app, orca = create_agent_app(
    process_message_func=process_message,
    title="Agent Name",
    description="Agent description",
)
```

### Session API
- `session.stream(text)` — envía texto al caller
- `session.close()` — cierra la sesión
- `session.error(msg, exception=e)` — reporta error
- `session.loading.start(label)` / `session.loading.end(label)` — indicador de carga
- `session.usage.track(tokens=N, token_type="total")` — tracking de tokens
- `session.available_agents` — lista agentes provider conectados
- `session.ask_agent(slug, question)` — delega a otro agente (consumer → provider)

### Variables
API keys no vienen de `.env` — Orca las inyecta en cada request via `data.variables`.
```python
variables = Variables(data.variables)
anthropic_key = variables.get("ANTHROPIC_API_KEY")
api_base_url = variables.get("API_BASE_URL")
```

## Capabilities

### Provider Agent (port 8000)
- Recibe preguntas de consumer agents
- Usa LLM (Anthropic Claude) para entender la petición
- Llama a las travel APIs asignadas
- Devuelve resultados estructurados y concisos

### Consumer Agent (port 8001)
- Recibe mensajes del usuario final via chat Orca
- Delega a providers con `session.ask_agent(slug, question)`
- Sintetiza respuestas en formato amigable
- En demo: conectado a TODOS los providers de todos los equipos

### Connectivity
- **Dev**: Ngrok tunnel → registrar en Orca Admin
- **Prod**: Docker → `orca ship ec2 deploy`

## Scenarios

### Provider receives request
1. Consumer agent llama `session.ask_agent("our-provider", "Find hotels for 2, March 20-22")`
2. Orca enruta a nuestro provider
3. Provider recibe `ChatMessage`, usa Claude para parsear intent
4. Llama a Hotel API, formatea respuesta corta
5. `session.stream(result)` → `session.close()`

### Consumer handles user
1. Usuario escribe en chat Orca
2. Consumer recibe `ChatMessage` con `data.chat_history`
3. Usa Claude para entender intent
4. Delega a provider(s) relevantes
5. Sintetiza y formatea respuesta amigable
6. `session.stream(response)` → `session.close()`
