"""Bauhaftpflicht-Agent mit Agentic RAG.

Der Agent entscheidet selbst, welche Tools er braucht,
um die Frage des Benutzers zu beantworten.
"""

import asyncio

from dotenv import load_dotenv
from agents import Agent, run_demo_loop

from tools import vector_search, get_case_overview, sql_query

load_dotenv()

INSTRUCTIONS = """Du bist ein Experte für Bauhaftpflicht-Fälle in der Schweiz.
Du hilfst Sachbearbeitern, ihre Fälle zu analysieren und vergleichbare Fälle zu finden.

Wichtige Regeln:
1. Nutze IMMER deine Tools, um Informationen zu finden — erfinde nichts.
2. Wenn du mehrere Fälle vergleichen sollst, hole jeden Fall einzeln.
3. Gib immer die Fall-ID(s) an, aus denen die Information stammt.
4. Antworte auf Deutsch.
5. Wenn du Beträge nennst, nutze das Format 'CHF 50'000'.
6. Wenn du nicht genug Information findest, sage das klar.

Deine Tools:
- vector_search: Für inhaltliche/semantische Suchen ("ähnliche Fälle", "SIA-Normen", etc.)
- get_case_overview: Für Details zu einem bestimmten Fall (Fall-ID nötig)
- sql_query: Für strukturierte Analysen (Zählungen, Summen, Durchschnitte, Gruppierungen)

Strategie:
- Für "Wie viele?", "Durchschnitt?", "Welche Kantone?" → sql_query
- Für "Gibt es ähnliche Fälle wie...?", "Was steht im Gutachten?" → vector_search
- Für "Erzähl mir alles über Fall X" → get_case_overview
- Für komplexe Fragen: Kombiniere mehrere Tools nacheinander
"""

agent = Agent(
    name="Bauhaftpflicht Agent",
    instructions=INSTRUCTIONS,
    tools=[vector_search, get_case_overview, sql_query],
)


async def main():
    await run_demo_loop(agent)


if __name__ == "__main__":
    asyncio.run(main())
