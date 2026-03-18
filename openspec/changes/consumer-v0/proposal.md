# Consumer v0 — Minimal Viable Consumer Agent

## Problem

Necesitamos un consumer agent desplegado en Orca YA. No tiene que ser perfecto, tiene que funcionar. Iteraremos después.

El boilerplate tiene un consumer stub que solo dice "not implemented yet". Necesitamos convertirlo en un agente real que use Claude para entender al usuario y delegar a providers disponibles.

## Scope

### In scope
- Consumer agent funcional con Anthropic Claude tool use
- Routing inteligente a providers via `session.available_agents` (runtime discovery)
- Una tool para Claude: `ask_provider(slug, question)`
- Stream de respuesta al usuario
- Deployable en Orca (mismo `main.py`, misma estructura)

### Out of scope (v1+)
- Chat history / contexto conversacional
- Loading indicators
- Multi-step workflows (search → compare → book)
- System prompt elaborado con persona
- Formateo rico de respuestas
- Multi-provider en paralelo

## Success criteria
1. El consumer responde al usuario en Orca
2. Claude decide correctamente a qué provider delegar
3. La respuesta del provider llega al usuario formateada mínimamente
4. Funciona end-to-end: user → consumer → provider → consumer → user

## Status: draft
