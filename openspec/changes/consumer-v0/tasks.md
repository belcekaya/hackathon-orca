# Tasks — Consumer v0

## T1: Implementar consumer con Claude tool use
- [x] Añadir `anthropic` a `consumer/requirements.txt`
- [x] Implementar `process_message` en `consumer/main.py`:
  - Leer `ANTHROPIC_API_KEY` de `Variables(data.variables)`
  - Construir lista de providers desde `session.available_agents`
  - Definir tool `ask_provider` con params: `slug` (string), `question` (string)
  - Llamar a Claude con system prompt + user message + tool
  - Si Claude usa tool → `session.ask_agent(slug, question)` → devolver resultado a Claude
  - Stream respuesta final al usuario
- **Files**: `consumer/main.py`, `consumer/requirements.txt`

## T2: Test local y deploy
- [x] Verificar que el consumer arranca: `python main.py` en port 8001
- [ ] Test con curl o directamente via Orca
- [x] Deploy a Orca (EC2): deployment ID a154f5ba-308f-4cfc-9f3c-77cc359b9ddf, URL http://ckbnq.agent-1.orca
- **Files**: ninguno nuevo

## Status: draft
