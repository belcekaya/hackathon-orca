# Travel Agent System — MADHACK Hackathon

## Problem

MADHACK requiere construir **dos AI agents** que se comunican via Orca:
- **Provider**: envuelve travel APIs asignadas, responde a otros agentes
- **Consumer**: asistente personal de viaje, delega a providers

En demo, todos los consumers se conectan a TODOS los providers de todos los equipos.

## Scope

### In scope
- Provider agent con Anthropic Claude tool use para las 6 APIs (hotel, restaurant, flight, car, tour, museum)
- Consumer agent que descubre providers y delega inteligentemente
- Conexión via Ngrok + deploy a EC2 via Orca CLI
- Token efficiency (judging criteria)

### Out of scope
- UI propia (se usa chat de Orca)
- Persistencia entre sesiones
- Auth de usuarios finales

## Success criteria (aligned with judging)
1. **Functionality**: El sistema produce outputs útiles — búsqueda, pricing, booking, cancelación funcionan (target: 10/10)
2. **API Integration**: Máximo número de travel APIs integradas y usadas de forma relevante
3. **Efficiency**: Prompts optimizados, tokens minimizados por request

## Status: draft
