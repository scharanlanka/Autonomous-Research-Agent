import time
from ara.tavily_search import tavily_search
from ara.tools.arxiv_tool import arxiv_search
from ara.tools.web_fetch import fetch_clean_text

def run_research(query: str) -> tuple[list[dict], list[dict]]:
    """
    Returns:
      web_sources: [{title,url,snippet,content,accessed_at}]
      arxiv_sources: [{title,url,snippet,published,authors,accessed_at}]
    """
    web = tavily_search(query)
    web_sources = []
    for item in web:
        url = item.get("url", "")
        content = ""
        try:
            if url:
                content = fetch_clean_text(url)
        except Exception:
            content = ""
        web_sources.append({
            "title": item.get("title", ""),
            "url": url,
            "snippet": item.get("snippet", ""),
            "content": content,
            "accessed_at": time.time(),
        })

    papers = arxiv_search(query)
    arxiv_sources = []
    for p in papers:
        p["accessed_at"] = time.time()
        arxiv_sources.append(p)

    return web_sources, arxiv_sources
