from ara.azure_llm import AzureChatLLM

SYSTEM = """You are PlannerAgent for an Autonomous Research Agent.
Create a concise step-by-step plan (5-8 steps max) to research the user's query.
Output ONLY a numbered list, one step per line.
"""

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
    # Parse numbered lines
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    plan = []
    for ln in lines:
        # remove leading numbering if present
        plan.append(ln.lstrip("0123456789. ").strip())
    # keep unique & non-empty
    plan = [p for p in plan if p]
    return plan[:8]