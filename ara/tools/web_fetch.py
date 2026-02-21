import re
import requests
from bs4 import BeautifulSoup
from ara.config import FETCH_MAX_CHARS

def fetch_clean_text(url: str, max_chars: int | None = None) -> str:
    max_chars = max_chars or FETCH_MAX_CHARS
    headers = {"User-Agent": "ARA/1.0 (research agent)"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    # remove noisy tags
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:max_chars]