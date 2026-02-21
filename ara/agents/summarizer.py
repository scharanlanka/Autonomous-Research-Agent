from ara.azure_llm import AzureChatLLM

SYSTEM = """You are SummarizerAgent.
Given the user query, memory context (prior notes), and gathered sources (snippets + extracted text),
produce a structured research draft in Markdown with citations.

Rules:
- Use inline citation markers like [1], [2] etc. whenever you state factual claims.
- Do not invent sources. Only cite from the provided sources list.
- Focus on relevance and synthesis.
- Include a "References" section mapping [n] -> URL + title.
"""

def run_summarizer(query: str, memory_context: list[str], sources: list[dict]) -> str:
    llm = AzureChatLLM()

    # Build compact source pack
    src_lines = []
    for i, s in enumerate(sources, 1):
        title = s.get("title", "")[:160]
        url = s.get("url", "")
        snippet = (s.get("snippet") or "")[:500]
        content = (s.get("content") or "")[:1200]
        src_lines.append(
            f"[{i}] {title}\nURL: {url}\nSnippet: {snippet}\nExtract: {content}\n"
        )
    memory_text = "\n".join(memory_context[:6])

    user_payload = f"""QUERY:
{query}

MEMORY CONTEXT (prior relevant notes):
{memory_text}

SOURCES:
{chr(10).join(src_lines)}
"""

    return llm.chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_payload},
        ],
        temperature=0.2,
        max_tokens=1600,
    )