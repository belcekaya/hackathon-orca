# Tasks — Travel Agent System

## Phase 1: Provider Agent (Critical — "the hard part")

### T1: API Client
- [ ] Crear `provider/api_client.py` con clase `BookingAPIClient`
- [ ] Wrapper httpx async: `get(path, params)`, `post(path, body)`, `delete(path)`
- [ ] Auto-inject `X-API-Key` header
- [ ] Base URL configurable (desde Orca variables o default)
- **Files**: `provider/api_client.py`

### T2: Tool Definitions
- [ ] Crear `provider/tools.py` con tool definitions para Anthropic tool use
- [ ] Tools para las 6 APIs: hotel, restaurant, flight, car_rental, tour_guide, museum
- [ ] Cada tool: name, description, input_schema (JSON Schema)
- [ ] Funciones handler que ejecutan la API call via `BookingAPIClient`
- **Files**: `provider/tools.py`

### T3: Provider Logic
- [ ] Implementar `process_message` en `provider/main.py`
- [ ] Leer API keys de `Variables(data.variables)`
- [ ] Enviar mensaje + tools a Claude → ejecutar tool calls → devolver resultado
- [ ] Loop de tool use (Claude puede pedir múltiples calls)
- [ ] `session.loading.start/end` para indicadores
- [ ] `session.usage.track` para tracking de tokens
- [ ] Respuestas cortas y estructuradas
- **Files**: `provider/main.py`

### T4: Test Provider Locally
- [ ] Levantar provider en port 8000
- [ ] Enviar requests de test directamente (sin Orca)
- [ ] Verificar que llama a las APIs y devuelve datos correctos

## Phase 2: Consumer Agent

### T5: Consumer Logic
- [ ] Implementar `process_message` en `consumer/main.py`
- [ ] Leer `session.available_agents` para descubrir providers
- [ ] Usar Claude para parsear intent del usuario
- [ ] Delegar a provider(s) con `session.ask_agent(slug, question)`
- [ ] Sintetizar respuestas en formato amigable
- [ ] Usar `ChatHistoryHelper` para contexto conversacional
- [ ] `session.loading.start/end` + `session.usage.track`
- **Files**: `consumer/main.py`

### T6: Test Consumer Locally
- [ ] Levantar provider (8000) + consumer (8001)
- [ ] Verificar consumer → provider flow

## Phase 3: Orca Integration

### T7: Connect to Orca
- [ ] `ngrok http 8000` para provider
- [ ] `ngrok http 8001` para consumer (segundo tunnel)
- [ ] Registrar ambos agentes en Orca Admin
- [ ] Click "Connect and Test"
- [ ] Test end-to-end via chat Orca

### T8: Requirements Update
- [ ] Añadir `anthropic` y `httpx` a ambos `requirements.txt`
- **Files**: `provider/requirements.txt`, `consumer/requirements.txt`

## Phase 4: Polish & Deploy

### T9: Optimización de prompts
- [ ] Minimizar tokens en system prompts
- [ ] Asegurar respuestas concisas del provider
- [ ] Consumer: formato friendly pero no verboso

### T10: Docker & EC2 Deploy
- [ ] Build: `docker buildx build --platform linux/amd64 -t provider-agent:latest --load .`
- [ ] Ship: `orca ship ec2 deploy provider --image provider-agent:latest --internal-port 8000 --push`
- [ ] Repetir para consumer (port 8001)

## Status: draft
