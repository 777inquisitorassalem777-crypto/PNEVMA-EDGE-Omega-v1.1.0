
"""OpenAI-compatible LLM client; supports remote endpoints and local Ollama-compatible APIs."""
from __future__ import annotations
import json
import os
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

class LLMError(RuntimeError):
    pass

class OpenAICompatibleClient:
    def __init__(self, base_url=None, model=None, api_key=None, timeout=45):
        self.base_url = (base_url or os.getenv("SYMBIO_LLM_BASE_URL", "http://localhost:11434/v1")).rstrip("/")
        self.model = model or os.getenv("SYMBIO_LLM_MODEL", "llama3.2")
        self.api_key = api_key if api_key is not None else os.getenv("SYMBIO_LLM_API_KEY", "")
        self.timeout = timeout

    def chat(self, messages, temperature=0.2, max_tokens=700):
        body = json.dumps({"model": self.model, "messages": messages,
                           "temperature": temperature, "max_tokens": max_tokens}).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = Request(f"{self.base_url}/chat/completions", data=body, headers=headers, method="POST")
        try:
            with urlopen(req, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"]
        except (HTTPError, URLError, TimeoutError, KeyError, IndexError, ValueError) as exc:
            raise LLMError(f"LLM request failed ({type(exc).__name__}); check endpoint/model configuration.") from exc

    @classmethod
    def from_env(cls):
        return cls()
