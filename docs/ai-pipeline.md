# AI Pipeline

## Provider Abstraction

`backend/app/agents/llm_provider.py` supports OpenAI-compatible APIs via environment variables.

## Agents

- **Research Agent** — Evidence retrieval (fallback fixtures)
- **PRO/CON Agents** — Claim generation
- **Critic Agent** — Counterargument generation
- **Contradiction Agent** — Conflict analysis
- **Synthesis Agent** — Evidence-weighted synthesis

## Fallback Mode

When `LLM_API_KEY` is empty, deterministic rule-based logic generates labeled fallback output.

## Structured Output

AI responses validated via Pydantic schemas. Malformed outputs rejected.
