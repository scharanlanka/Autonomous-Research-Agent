import requests
from ara.config import AZURE_LLM_ENDPOINT, AZURE_LLM_API_KEY, AZURE_LLM_DEPLOYMENT_NAME

class AzureChatLLM:
    def __init__(self, endpoint: str = AZURE_LLM_ENDPOINT, api_key: str = AZURE_LLM_API_KEY):
        self.endpoint = endpoint
        self.api_key = api_key

    def chat(self, messages: list[dict], temperature: float = 0.2, max_tokens: int = 1200) -> str:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["api-key"] = self.api_key

        payload = {
            # Keep deployment name in payload for your tracking/debugging even if endpoint already routes it.
            "model": AZURE_LLM_DEPLOYMENT_NAME,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()

        # Compatible parsing (choices/message/content)
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            return str(data)