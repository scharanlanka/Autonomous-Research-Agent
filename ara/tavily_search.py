from tavily import TavilyClient
from ara.config import TAVILY_API_KEY, TAVILY_MAX_RESULTS

client = TavilyClient(api_key=TAVILY_API_KEY)


def tavily_search(query: str, max_results: int | None = None) -> list[dict]:
    """
    Tavily search tool for Autonomous Research Agent
    Returns clean structured results optimized for LLM use
    """

    max_results = max_results or TAVILY_MAX_RESULTS

    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
            include_raw_content=False,
        )

        results = []

        for item in response.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
            })

        return results

    except Exception as e:
        print(f"Tavily search error: {e}")
        return []