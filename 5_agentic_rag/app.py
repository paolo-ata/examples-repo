"""Streamlit Web-UI für das Agentic RAG-System."""

import asyncio

import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner

from tools import vector_search, get_case_overview, list_cases

load_dotenv()

st.set_page_config(page_title="Bauhaftpflicht Agentic RAG", layout="wide")

st.title("Bauhaftpflicht Agentic RAG")
st.caption("Der Agent entscheidet selbst, welche Tools er braucht.")

# Sidebar: Info über die Tools
st.sidebar.header("Agent-Tools")
st.sidebar.markdown("""
- **vector_search** — Semantische Suche
- **get_case_overview** — Fall-Details laden
- **list_cases** — Fälle auflisten/zählen
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### Beispiel-Fragen")
st.sidebar.markdown("""
- Gibt es Fälle mit Wasserschäden?
- Was sind die Fakten zu Fall W3?
- Vergleiche Fall W1 mit H2
- Wie viele Fälle gibt es pro Cluster?
""")

# Agent erstellen
INSTRUCTIONS = """Du bist ein Experte für Bauhaftpflicht-Fälle in der Schweiz.
Du hilfst Sachbearbeitern, ihre Fälle zu analysieren und vergleichbare Fälle zu finden.

Wichtige Regeln:
1. Nutze IMMER deine Tools, um Informationen zu finden — erfinde nichts.
2. Wenn du mehrere Fälle vergleichen sollst, hole jeden Fall einzeln.
3. Gib immer die Fall-ID(s) an, aus denen die Information stammt.
4. Antworte auf Deutsch.
5. Wenn du Beträge nennst, nutze das Format 'CHF 50'000'.
6. Wenn du nicht genug Information findest, sage das klar.
"""

agent = Agent(
    name="Bauhaftpflicht Agent",
    instructions=INSTRUCTIONS,
    tools=[vector_search, get_case_overview, list_cases],
)

# Chat-History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Eingabefeld
question = st.chat_input("Frage zu den Bauhaftpflicht-Fällen...")

if question:
    # User-Nachricht anzeigen und speichern
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Agent antworten lassen
    with st.chat_message("assistant"):
        with st.spinner("Agent arbeitet..."):
            result = asyncio.run(Runner.run(agent, question))
            answer = result.final_output

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
