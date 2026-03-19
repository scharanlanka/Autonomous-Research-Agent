import time
import json
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.ara.agents.reporter import export_pdf_bytes
from backend.ara.graph import build_graph
from backend.ara.logger import InMemoryLogger
from backend.ara.schemas import ResearchState

SOURCE_EVENT_STAGGER_SECONDS = 0.15


class ResearchRunRequest(BaseModel):
    query: str = Field(..., min_length=1)


class PdfExportRequest(BaseModel):
    markdown_text: str
    title: str = "ARA Research Report"


app = FastAPI(title="Autonomous Research Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/research/run")
def run_research(request: ResearchRunRequest) -> dict[str, Any]:
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    logger = InMemoryLogger()
    graph = build_graph(logger)
    initial_state = _build_initial_state(query)

    try:
        result = graph.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Research run failed: {exc}") from exc

    return result


def _build_initial_state(query: str) -> dict[str, Any]:
    return ResearchState(
        query=query,
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


def _sse(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


@app.get("/api/research/stream")
def stream_research(query: str) -> StreamingResponse:
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    logger = InMemoryLogger()
    graph = build_graph(logger)
    initial_state = _build_initial_state(clean_query)

    node_labels = {
        "planner_node": "Planning",
        "memory_retrieve_node": "Retrieving Memory",
        "research_node": "Researching Sources",
        "summarize_node": "Generating Draft",
        "critic_node": "Revising Report",
        "memory_store_node": "Storing Memory",
    }

    def event_generator():
        latest_state = dict(initial_state)
        yield _sse(
            "status",
            {
                "phase": "starting",
                "message": "Research run started.",
                "query": clean_query,
            },
        )

        try:
            for update in graph.stream(initial_state, stream_mode="updates"):
                for node_name, node_update in update.items():
                    if isinstance(node_update, dict):
                        latest_state.update(node_update)

                        if "plan" in node_update and isinstance(node_update["plan"], list):
                            plan = node_update["plan"]
                            for idx, step in enumerate(plan, start=1):
                                yield _sse(
                                    "plan",
                                    {
                                        "index": idx,
                                        "text": str(step),
                                        "total": len(plan),
                                    },
                                )

                        if "sources" in node_update and isinstance(node_update["sources"], list):
                            sources = node_update["sources"]
                            for idx, source in enumerate(sources, start=1):
                                if not isinstance(source, dict):
                                    continue
                                yield _sse(
                                    "source",
                                    {
                                        "index": idx,
                                        "total": len(sources),
                                        "title": source.get("title", ""),
                                        "url": source.get("url", ""),
                                        "snippet": source.get("snippet", ""),
                                        "type": source.get("type", "web"),
                                    },
                                )
                                time.sleep(SOURCE_EVENT_STAGGER_SECONDS)

                        if "logs" in node_update and isinstance(node_update["logs"], list):
                            logs = node_update["logs"]
                            if logs:
                                yield _sse("log", {"text": logs[-1]})

                    logs = latest_state.get("logs", [])
                    last_log = logs[-1] if logs else ""

                    yield _sse(
                        "progress",
                        {
                            "node": node_name,
                            "label": node_labels.get(node_name, node_name),
                            "status": "completed",
                            "plan_count": len(latest_state.get("plan", [])),
                            "source_count": len(latest_state.get("sources", [])),
                            "last_log": last_log,
                        },
                    )

            yield _sse("result", latest_state)
            yield _sse("done", {"ok": True})
        except Exception as exc:
            yield _sse("error", {"message": f"Research run failed: {exc}"})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/research/pdf")
def export_pdf(request: PdfExportRequest) -> Response:
    pdf_bytes = export_pdf_bytes(title=request.title, markdown_text=request.markdown_text)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="ara_report.pdf"'},
    )
