# PHASE 5 — Specialist Agents

**Status**: ✅ Completed

## Scope
- Medicine, Symptom, Commerce, Support specialist sub-graphs
- Tool-bound agents using Phase 2 registry subsets
- Generic `run_tool_agent` loop (reason → act → observe)
- Product suggestion extraction for UI
- Integration into main graph via supervisor routing

## Key Files
- `app/agents/specialists.py`
- `app/agents/tool_agent.py`
- `app/agents/graph.py` (specialist nodes)
- `app/tools/registry.py` (TOOL_CATALOG)
- `app/core/prompts.py` (Phase 5 specialist prompts)

## Acceptance Criteria Met
- Each specialist successfully calls only its allowed tools
- Tool results feed back into the conversation
- Products surfaced from search/alternative/product_details calls
- Full end-to-end flow: query → supervisor → specialist → tools → answer

## Notes
Completes the core agentic loop. Later phases add RAG enhancements, safety, eval, etc.
