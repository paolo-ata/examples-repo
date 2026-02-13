"""Streamlit Web-UI für das RAG-System."""

import streamlit as st
from rag_chain import ask
from retriever import get_collection_stats

st.set_page_config(page_title="Bauhaftpflicht RAG", layout="wide")

st.title("Bauhaftpflicht RAG-System")

# Sidebar: Filter
st.sidebar.header("Filter")
selected_case = st.sidebar.text_input("Fall-ID (z.B. W1)", value="")
selected_cluster = st.sidebar.text_input("Cluster (z.B. Wasser/Abdichtung)", value="")

# Collection-Statistiken in Sidebar
stats = get_collection_stats()
if "total_chunks" in stats:
    st.sidebar.metric("Indexierte Chunks", stats["total_chunks"])

# Hauptbereich
question = st.text_area("Frage zu den Bauhaftpflicht-Fällen:", height=100)

if st.button("Frage stellen") and question:
    with st.spinner("Analysiere Akten..."):
        # Filter aufbauen
        filter_dict = None
        if selected_case or selected_cluster:
            filter_dict = {}
            if selected_case:
                filter_dict["case_id"] = selected_case
            if selected_cluster:
                filter_dict["cluster"] = selected_cluster

        result = ask(question, filter_dict=filter_dict)

        st.markdown("### Antwort")
        st.write(result["answer"])

        if result["sources"]:
            st.markdown("### Quellen")
            for s in result["sources"]:
                st.markdown(
                    f"- **Fall {s['case_id']}**: {s['doc_typ']} "
                    f"({s['doc_datum']}) — {s['cluster']}"
                )
