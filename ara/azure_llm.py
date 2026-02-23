import requests
from ara.config import AZURE_LLM_ENDPOINT, AZURE_LLM_API_KEY, AZURE_LLM_DEPLOYMENT_NAME

class AzureChatLLM:
    last_call_meta = {}

    def __init__(self, endpoint: str = AZURE_LLM_ENDPOINT, api_key: str = AZURE_LLM_API_KEY):
        self.endpoint = endpoint
        self.api_key = api_key
        self.last_response_meta = {}

    def _extract_text(self, content) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(item.get("text", ""))
                    elif "text" in item:
                        parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
            return "".join(parts)
        return "" if content is None else str(content)

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 1200,
        continue_on_length: bool = False,
        max_continuations: int = 2,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["api-key"] = self.api_key

        base_messages = list(messages)
        working_messages = list(base_messages)
        chunks: list[str] = []
        finish_reasons: list[str] = []
        usage_records: list[dict] = []

        for continuation_idx in range(max_continuations + 1):
            payload = {
                # Keep deployment name in payload for your tracking/debugging even if endpoint already routes it.
                "model": AZURE_LLM_DEPLOYMENT_NAME,
                "messages": working_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()

            try:
                choice = data["choices"][0]
                finish_reason = choice.get("finish_reason", "")
                message = choice.get("message", {})
                piece = self._extract_text(message.get("content", ""))
            except Exception:
                self.last_response_meta = {"raw": data}
                AzureChatLLM.last_call_meta = self.last_response_meta
                return str(data)

            chunks.append(piece or "")
            finish_reasons.append(str(finish_reason or ""))
            if isinstance(data.get("usage"), dict):
                usage_records.append(data["usage"])

            if not (continue_on_length and str(finish_reason).lower() == "length"):
                break

            if continuation_idx >= max_continuations:
                break

            assembled = "".join(chunks)
            working_messages = base_messages + [
                {"role": "assistant", "content": assembled},
                {
                    "role": "user",
                    "content": (
                        "Continue exactly from where you stopped. "
                        "Do not repeat previous text. Return only the continuation."
                    ),
                },
            ]

        self.last_response_meta = {
            "finish_reasons": finish_reasons,
            "continued": any(fr.lower() == "length" for fr in finish_reasons[:-1]) if finish_reasons else False,
            "segments": len(chunks),
            "usage": usage_records,
        }
        AzureChatLLM.last_call_meta = self.last_response_meta
        return "".join(chunks)
