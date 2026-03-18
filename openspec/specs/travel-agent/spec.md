# Travel Agent System

Sistema de dos agentes que trabajan juntos via Orca: un Provider que envuelve las APIs de viaje y un Consumer que asiste al usuario.

## Context

Construido con Orca SDK (`orca-platform-sdk-ui`) y Anthropic Claude (tool use). El Provider es "la parte difícil" (lógica de API), el Consumer es "la parte creativa" (UX/persona).

**LLM**: Anthropic Claude (via `anthropic` SDK con tool use)
**API keys**: Inyectadas por Orca via `Variables(data.variables)`, no `.env`

## Capabilities

### Provider Agent — Travel API Wrapper
- Recibe preguntas en lenguaje natural de consumer agents
- Usa Claude tool use para mapear intent → API calls
- Soporta todas las operaciones: search, availability, pricing, book, cancel, list
- Respuestas cortas y estructuradas (datos, no prosa)
- Manejo de errores con mensajes claros

### Consumer Agent — Travel Concierge
- Asistente personal de viaje facing usuarios finales
- Entiende peticiones en inglés y español
- Descubre providers disponibles via `session.available_agents`
- Delega a providers con `session.ask_agent(slug, question)`
- Sintetiza múltiples respuestas en formato amigable
- Usa `ChatHistoryHelper` para contexto conversacional
- Multi-step: search → compare → book

## Scenarios

### Provider: Search + Book
1. Consumer pide: "Find available hotels for 2 guests, March 20-22"
2. Provider usa Claude tool use → llama `GET /hotel-1/api/rooms/available?check_in=2026-03-20&check_out=2026-03-22&guests=2`
3. Devuelve JSON conciso con rooms disponibles y precios

### Consumer: Full trip planning
1. Usuario: "Quiero un viaje a NYC del 20 al 22 de marzo para 2 personas"
2. Consumer delega a providers: flights, hotels, restaurants, tours
3. Recoge respuestas, compara, presenta itinerario
4. Usuario elige → consumer pide booking a providers

### Provider: Error handling
1. Consumer pide reservar hotel sin disponibilidad
2. Provider llama API → recibe error/vacío
3. Devuelve mensaje claro: "No rooms available for those dates. Try March 23-25."

### Consumer: Multi-provider
1. Usuario: "Book me a hotel and a flight"
2. Consumer llama `session.ask_agent("hotel-provider", "...")` y `session.ask_agent("flight-provider", "...")`
3. Sintetiza ambas respuestas en un resumen unificado

## Judging Optimization

| Criteria | Strategy |
|----------|----------|
| **Functionality** | Cubrir CRUD completo en todas las APIs asignadas |
| **API Integration** | Máximo número de APIs integradas, todas relevantes |
| **Efficiency** | Prompts cortos, tool use (no parsing manual), respuestas concisas |
