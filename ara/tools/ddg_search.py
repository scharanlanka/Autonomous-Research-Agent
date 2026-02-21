from duckduckgo_search import DDGS
from ara.config import DDG_MAX_RESULTS

def ddg_search(query: str, max_results: int | None = None) -> list[dict]:
    max_results = max_results or DDG_MAX_RESULTS
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            # r keys usually: title, href, body
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            })
    return results