import os
import json
import time
import streamlit as st
from dotenv import load_dotenv

from ara.graph import build_graph
from ara.schemas import ResearchState
from ara.logger import InMemoryLogger
from ara.agents.reporter import export_pdf_bytes

load_dotenv()

st.set_page_config(page_title="Autonomous Research Agent (ARA)", layout="wide")

st.title("Autonomous Research Agent (ARA)")
st.caption("Agentic research: plan → search → analyze → synthesize → cite → report")

with st.sidebar:
    st.header("Run Settings")
    show_debug = st.toggle("Show debug logs", value=True)
    st.divider()
    st.write("**Memory (ChromaDB)**")
    st.write(f"Persist dir: `{os.getenv('CHROMA_PERSIST_DIR', './chroma_db')}`")
    st.write(f"Collection: `{os.getenv('CHROMA_COLLECTION', 'ara_memory')}`")

query = st.text_area(
    "Research Task",
    placeholder='e.g., "Research impact of AI on software engineering jobs (2023-2026). Provide key findings with sources."',
    height=120,
)

colA, colB, colC = st.columns([1, 1, 2])
run_btn = colA.button("Run Research", type="primary", use_container_width=True)
clear_btn = colB.button("Clear", use_container_width=True)

if clear_btn:
    st.session_state.clear()
    st.rerun()

if run_btn:
    if not query.strip():
        st.error("Please enter a research query.")
        st.stop()

    logger = InMemoryLogger()
    graph = build_graph(logger)

    # Initial State
    state = ResearchState(
        query=query.strip(),
        status="running",
        created_at=time.time(),
        logs=[],
        plan=[],
        tool_results=[],
        sources=[],
        memory_context=[],
        draft_report="",
        final_report="",
    ).model_dump()

    st.session_state["run_started"] = True
    st.session_state["logger"] = logger

    # UI placeholders
    status_box = st.empty()
    plan_box = st.container()
    logs_box = st.container()
    report_box = st.container()

    status_box.info("Status: Planning...")

    # Stream execution (simple “step updates” via logger + state updates)
    try:
        result = graph.invoke(state)
    except Exception as e:
        status_box.error("Status: Failed")
        st.error(f"Research run failed: {e}")
        st.stop()

    status_box.success("Status: Completed ✅")

    # Render outputs
    with plan_box:
        st.subheader("Plan")
        plan = result.get("plan", [])
        if plan:
            for i, step in enumerate(plan, 1):
                st.write(f"{i}. {step}")
        else:
            st.write("No plan generated.")

    with logs_box:
        st.subheader("Logs")
        if show_debug:
            for item in result.get("logs", []):
                st.code(item)
        else:
            st.write("Enable debug logs in the sidebar to view details.")

    with report_box:
        st.subheader("Final Report")
        final_report = result.get("final_report", "").strip()
        if final_report:
            st.markdown(final_report)
        else:
            st.warning("No report generated.")

    # Export buttons
    st.divider()
    col1, col2 = st.columns(2)

    md_bytes = final_report.encode("utf-8", errors="ignore")
    col1.download_button(
        "Download Markdown",
        data=md_bytes,
        file_name="ara_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

    pdf_bytes = export_pdf_bytes(title="ARA Research Report", markdown_text=final_report)
    col2.download_button(
        "Download PDF",
        data=pdf_bytes,
        file_name="ara_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
