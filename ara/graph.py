from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from ara.logger import InMemoryLogger
from ara.memory import MemoryStore, make_id
from ara.schemas import ToolResult, SourceItem

from ara.agents.planner import run_planner
from ara.agents.researcher import run_research
from ara.agents.summarizer import run_summarizer
from ara.agents.critic import run_critic
from ara.agents.reporter import extract_revised

class GraphState(TypedDict, total=False):
    query: str
    status: str
    created_at: float
    plan: List[str]
    tool_results: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    memory_context: List[str]
    draft_report: str
    final_report: str
    logs: List[str]

def build_graph(logger: InMemoryLogger):
    mem = MemoryStore()

    def node_plan(state: GraphState) -> GraphState:
        q = state["query"]
        logger.log("PlannerAgent: generating plan")
        plan = run_planner(q)
        logger.log(f"PlannerAgent: plan steps={len(plan)}")
        state["plan"] = plan
        state["logs"] = logger.dump()
        return state

    def node_memory_retrieve(state: GraphState) -> GraphState:
        q = state["query"]
        logger.log("Memory: retrieving similar past research")
        ctx = mem.search(q, k=5)
        state["memory_context"] = ctx
        logger.log(f"Memory: retrieved items={len(ctx)}")
        state["logs"] = logger.dump()
        return state

    def node_research(state: GraphState) -> GraphState:
        q = state["query"]
        logger.log("ResearchAgent: running Tavily + arXiv search + fetching pages")
        web_sources, arxiv_sources = run_research(q)

        # Build unified sources list for report generator
        sources = []
        for s in web_sources:
            sources.append({
                "title": s["title"],
                "url": s["url"],
                "snippet": s.get("snippet", ""),
                "content": s.get("content", ""),
                "accessed_at": s.get("accessed_at"),
                "type": "web",
            })
        for p in arxiv_sources:
            sources.append({
                "title": p["title"],
                "url": p["url"],
                "snippet": p.get("snippet", ""),
                "content": "",  # we can add PDF/abstract parsing later
                "accessed_at": p.get("accessed_at"),
                "type": "arxiv",
                "published": p.get("published", ""),
                "authors": p.get("authors", []),
            })

        state["sources"] = sources

        state["tool_results"] = [
            ToolResult(tool="tavily_search", query=q, results=web_sources).model_dump(),
            ToolResult(tool="arxiv_search", query=q, results=arxiv_sources).model_dump(),
        ]

        logger.log(f"ResearchAgent: sources collected={len(sources)}")
        state["logs"] = logger.dump()
        return state

    def node_summarize(state: GraphState) -> GraphState:
        logger.log("SummarizerAgent: drafting report with citations")
        draft = run_summarizer(
            query=state["query"],
            memory_context=state.get("memory_context", []),
            sources=state.get("sources", []),
        )
        state["draft_report"] = draft
        logger.log("SummarizerAgent: draft complete")
        state["logs"] = logger.dump()
        return state

    def node_critic(state: GraphState) -> GraphState:
        logger.log("CriticAgent: reviewing + improving report")
        crit = run_critic(state.get("draft_report", ""))
        revised = extract_revised(crit)
        state["final_report"] = revised
        logger.log("CriticAgent: revision complete")
        state["logs"] = logger.dump()
        return state

    def node_memory_store(state: GraphState) -> GraphState:
        logger.log("Memory: storing research notes")
        q = state["query"]
        report = state.get("final_report", "")
        sources = state.get("sources", [])

        # Store a compact “note” so future runs can recall it
        note = f"Query: {q}\n\nReport (excerpt):\n{report[:2500]}"
        metas = [{
            "source": "ara_report",
            "timestamp": state.get("created_at", ""),
            "num_sources": len(sources),
        }]
        ids = [make_id("report")]

        try:
            mem.add([note], metas, ids)
            logger.log("Memory: stored successfully")
        except Exception as e:
            logger.log(f"Memory: store failed: {e}")

        state["status"] = "done"
        state["logs"] = logger.dump()
        return state

    g = StateGraph(GraphState)
    g.add_node("planner_node", node_plan)
    g.add_node("memory_retrieve_node", node_memory_retrieve)
    g.add_node("research_node", node_research)
    g.add_node("summarize_node", node_summarize)
    g.add_node("critic_node", node_critic)
    g.add_node("memory_store_node", node_memory_store)

    g.set_entry_point("planner_node")
    g.add_edge("planner_node", "memory_retrieve_node")
    g.add_edge("memory_retrieve_node", "research_node")
    g.add_edge("research_node", "summarize_node")
    g.add_edge("summarize_node", "critic_node")
    g.add_edge("critic_node", "memory_store_node")
    g.add_edge("memory_store_node", END)

    return g.compile()
