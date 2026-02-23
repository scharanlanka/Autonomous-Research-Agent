import json
import re

from ara.azure_llm import AzureChatLLM

SYSTEM = """You are PlannerAgent for an Autonomous Research Agent.
Create a concise step-by-step plan (5-8 steps max) to research the user's query.
Return ONLY a numbered list, one step per line.
Each step must be concrete and action-oriented.
"""

_NUM_PREFIX_RE = re.compile(r"^\s*\d+[\.\)]\s*")
_BULLET_PREFIX_RE = re.compile(r"^\s*[-*+]\s*")


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2 and lines[-1].strip() == "```":
            return "\n".join(lines[1:-1]).strip()
    return text


def _coerce_plan(raw: str) -> list[str]:
    text = _strip_code_fences(raw)

    # Try JSON first if model ignored the format instruction.
    try:
        obj = json.loads(text)
        if isinstance(obj, list):
            items = obj
        elif isinstance(obj, dict):
            items = obj.get("plan") or obj.get("steps") or []
        else:
            items = []
        if items:
            parsed = [str(x).strip() for x in items if str(x).strip()]
            if parsed:
                return parsed
    except Exception:
        pass

    plan: list[str] = []
    for ln in text.splitlines():
        line = ln.strip()
        if not line:
            continue
        line = _NUM_PREFIX_RE.sub("", line)
        line = _BULLET_PREFIX_RE.sub("", line)
        line = line.strip()
        if not line:
            continue
        # Drop obvious non-plan wrappers.
        if line.lower() in {"plan", "research plan", "steps"}:
            continue
        plan.append(line)
    return plan


def _fallback_plan(query: str) -> list[str]:
    topic = query.strip().rstrip(".") or "the research topic"
    return [
        f"Clarify the scope, timeframe, and decision criteria for {topic}.",
        "Break the question into subtopics and define what evidence is needed for each.",
        "Collect recent high-quality sources (official docs, research papers, reputable publications).",
        "Extract key facts, metrics, and claims with citations; note source dates and limitations.",
        "Compare sources for agreement, disagreement, and gaps in evidence.",
        "Synthesize findings into a structured report with recommendations and a references section.",
    ]


def run_planner(query: str) -> list[str]:
    llm = AzureChatLLM()
    content = llm.chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": query},
        ],
        temperature=0.2,
        max_tokens=400,
    )
    plan = _coerce_plan(content)

    # Keep unique/non-empty while preserving order.
    seen = set()
    deduped: list[str] = []
    for step in plan:
        norm = re.sub(r"\s+", " ", step).strip()
        if not norm:
            continue
        key = norm.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(norm)

    if len(deduped) < 3:
        deduped = _fallback_plan(query)

    return deduped[:8]
