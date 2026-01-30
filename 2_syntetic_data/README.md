# Synthetic Insurance Case Data Generator

## What is this?

This is **Step 1** of a larger project. The goal of the bigger project is to build a **case comparison tool** for construction liability insurance ("Bauhaftpflicht") -- think of it as a search engine that finds similar past cases to help claims handlers make better decisions.

But before we can build that, we need data to work with. That's what this project does: it **generates realistic synthetic case documents** using an LLM (OpenAI API), so we have a proper dataset to develop and test the case comparison system.

## What it generates

- **20 insurance cases** across different categories (water damage, facades, HVAC, guarantees, etc.)
- **~10 documents per case** (claim reports, expert opinions, court filings, settlement agreements, etc.)
- **112 documents total**, in German and French, with realistic legal language and Swiss formatting

Each document is a JSON file with the full text (`content`) and structured metadata (`metadata`) like case ID, document type, canton, legal norms, and claim amount -- ready for embedding and retrieval in a RAG pipeline.

## How to use

```bash
# Install dependencies
uv sync

# Set your OpenAI API key in .env
# OPENAI_API_KEY=sk-...

# Generate all cases
uv run python main.py generate-all

# Generate a single case
uv run python main.py generate-case W1

# Check progress
uv run python main.py status
```

## Project structure

```
main.py              # CLI entry point
models.py            # Data models (Pydantic)
config.py            # Settings (model, paths, API key)
prompts.py           # Prompt templates for each document type
generator.py         # OpenAI API wrapper with retry logic
pipeline.py          # Orchestration: loads cases, generates docs, tracks progress
data/
  case_bibles.json   # 20 predefined case definitions
output/              # Generated documents (one folder per case)
progress.json        # Tracks what's been generated (enables resume)
```

## Next step

Use the generated documents as input for the **case comparison / RAG system** (separate project).
