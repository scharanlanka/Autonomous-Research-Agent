from ara.azure_llm import AzureChatLLM

SYSTEM = """You are SummarizerAgent.
Given the user query, memory context (prior notes), and gathered sources (snippets + extracted text),
produce a structured research draft in Markdown with citations.

Rules:
- Use inline citation markers like [1], [2] etc. whenever you state factual claims.
- Do not invent sources. Only cite from the provided sources list.
- Focus on relevance and synthesis.
- Be specific, not vague: include concrete facts, dates, metrics, and limitations where available.
- If evidence is weak or missing, say so explicitly.
- Include a "References" section mapping [n] -> URL + title.

Required Markdown structure:
# Research Report: <topic>
## Executive Summary
## Scope and Assumptions
## Key Findings
### Finding 1
### Finding 2
## Risks / Limitations
## Recommendations / Next Steps
## References
"""


def _format_sources(sources: list[dict], snippet_chars: int, content_chars: int, limit: int) -> str:
    lines: list[str] = []
    for i, s in enumerate(sources[:limit], 1):
        title = (s.get("title") or "")[:160]
        url = s.get("url", "")
        snippet = (s.get("snippet") or "")[:snippet_chars]
        content = (s.get("content") or "")[:content_chars]
        lines.append(
            f"[{i}] {title}\nURL: {url}\nSnippet: {snippet}\nExtract: {content}\n"
        )
    return "\n".join(lines)


def _fallback_report(query: str, sources: list[dict]) -> str:
    refs = []
    for i, s in enumerate(sources[:8], 1):
        title = (s.get("title") or "Untitled Source").strip()
        url = (s.get("url") or "").strip()
        refs.append(f"[{i}] {title} - {url}")
    refs_block = "\n".join(refs) if refs else "No sources available."
    return f"""# Research Report: {query}

## Executive Summary
The summarizer returned an empty response in this run. This fallback keeps the report aligned to the requested topic and preserves collected references.

## Scope and Assumptions
- Requested topic: {query}
- No synthesized findings are included because the summarizer output was empty.
- Use the references below for manual verification and rerun.

## Key Findings
### Finding 1
No validated finding available because the summarizer step returned no content.

### Finding 2
No validated finding available because the summarizer step returned no content.

## Risks / Limitations
- Empty LLM output in summarization can cause downstream agents to hallucinate unrelated topics.
- This fallback intentionally avoids inventing claims.

## Recommendations / Next Steps
1. Retry with fewer sources or shorter excerpts.
2. Add response metadata logging (finish reason/content filtering) for the Azure call.
3. Consider reducing prompt size or splitting summarization into chunks.

## References
{refs_block}
"""


def run_summarizer(query: str, memory_context: list[str], sources: list[dict]) -> str:
    llm = AzureChatLLM()
    memory_text = "\n".join(memory_context[:6])

    # First pass: richer context, but capped to avoid oversized prompts.
    user_payload = f"""QUERY:
{query}

MEMORY CONTEXT (prior relevant notes):
{memory_text}

SOURCES:
{_format_sources(sources, snippet_chars=350, content_chars=700, limit=10)}
"""

    draft = llm.chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_payload},
        ],
        temperature=0.2,
        max_tokens=2200,
        continue_on_length=True,
        max_continuations=2,
    )
    if (draft or "").strip():
        return draft

    # Retry with a much smaller payload if the first call returns empty.
    retry_payload = f"""QUERY:
{query}

Return a complete Markdown report using ONLY the sources below. If evidence is limited, say so explicitly.

SOURCES:
{_format_sources(sources, snippet_chars=180, content_chars=240, limit=6)}
"""
    retry = llm.chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": retry_payload},
        ],
        temperature=0.2,
        max_tokens=2000,
        continue_on_length=True,
        max_continuations=2,
    )
    if (retry or "").strip():
        return retry

    return _fallback_report(query, sources)
