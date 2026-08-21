import logging
import os
from typing import Any
from google import genai

logger = logging.getLogger("uvicorn")


def _get_api_keys() -> list[str]:
    keys = []
    k1 = os.getenv("GEMINI_API_KEY", "").strip()
    k2 = os.getenv("GEMINI_API_KEY_SECONDARY", "").strip()
    if k1:
        keys.append(k1)
    if k2 and k2 != k1:
        keys.append(k2)
    return keys


class ModelsProxy:
    """
    Transparent proxy for genai.Client.models supporting automatic 0ms key rotation.
    If Key #1 encounters a 429 quota error, it automatically fails over to Key #2.
    """

    def __init__(self, clients: list[genai.Client]):
        self.clients = clients

    def embed_content(self, *args, **kwargs) -> Any:
        last_err = None
        for idx, client in enumerate(self.clients):
            try:
                return client.models.embed_content(*args, **kwargs)
            except Exception as err:
                err_str = str(err)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str) and idx < len(self.clients) - 1:
                    logger.warning(
                        f"[GEMINI KEY ROTATION] Key #{idx+1} hit quota limit. Automatically failing over to Key #{idx+2} in 0ms..."
                    )
                    last_err = err
                    continue
                raise err
        if last_err:
            raise last_err

    def generate_content(self, *args, **kwargs) -> Any:
        last_err = None
        for idx, client in enumerate(self.clients):
            try:
                return client.models.generate_content(*args, **kwargs)
            except Exception as err:
                err_str = str(err)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str) and idx < len(self.clients) - 1:
                    logger.warning(
                        f"[GEMINI KEY ROTATION] Key #{idx+1} hit quota limit. Automatically failing over to Key #{idx+2} in 0ms..."
                    )
                    last_err = err
                    continue
                raise err
        if last_err:
            raise last_err

    def generate_content_stream(self, *args, **kwargs) -> Any:
        last_err = None
        for idx, client in enumerate(self.clients):
            try:
                return client.models.generate_content_stream(*args, **kwargs)
            except Exception as err:
                err_str = str(err)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str) and idx < len(self.clients) - 1:
                    logger.warning(
                        f"[GEMINI KEY ROTATION] Key #{idx+1} hit quota limit. Automatically failing over to Key #{idx+2} in 0ms..."
                    )
                    last_err = err
                    continue
                raise err
        if last_err:
            raise last_err


class RotatingGeminiClient:
    def __init__(self):
        keys = _get_api_keys()
        self.clients = [genai.Client(api_key=k) for k in keys] if keys else [genai.Client(api_key="")]
        self.models = ModelsProxy(self.clients)


client = RotatingGeminiClient()