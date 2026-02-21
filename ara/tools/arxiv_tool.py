import arxiv
import time
from ara.config import ARXIV_MAX_RESULTS

def arxiv_search(query: str, max_results: int | None = None) -> list[dict]:
    max_results = max_results or ARXIV_MAX_RESULTS

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    # arXiv intermittently returns 503. Retry with backoff and fail-soft.
    retries = 3
    backoff_seconds = 1.5
    page_size = min(max_results, 25)

    for attempt in range(retries):
        try:
            results = []
            client = arxiv.Client(page_size=page_size, delay_seconds=3.0, num_retries=2)
            for r in client.results(search):
                results.append({
                    "title": r.title,
                    "url": r.entry_id,
                    "snippet": (r.summary or "")[:600],
                    "published": str(r.published) if r.published else "",
                    "authors": [a.name for a in (r.authors or [])],
                })
            return results
        except Exception as e:
            message = str(e).lower()
            is_retryable = "503" in message or "http" in message or "temporar" in message
            if is_retryable and attempt < retries - 1:
                time.sleep(backoff_seconds * (2 ** attempt))
                continue
            print(f"arXiv search error: {e}")
            return []

    return []
