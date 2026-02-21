import requests
from ara.config import AZURE_EMBEDDING_ENDPOINT, AZURE_EMBEDDING_API_KEY, AZURE_EMBEDDING_DEPLOYMENT_NAME

class AzureEmbeddings:
    def __init__(self, endpoint: str = AZURE_EMBEDDING_ENDPOINT, api_key: str = AZURE_EMBEDDING_API_KEY):
        self.endpoint = endpoint
        self.api_key = api_key

    def embed(self, texts: list[str]) -> list[list[float]]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key

        payload = {
            "model": AZURE_EMBEDDING_DEPLOYMENT_NAME,
            "input": texts,
        }

        resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]