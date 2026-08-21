import logging
import os
from typing import Any
from google import genai

logger = logging.getLogger("uvicorn")


def _get_api_keys() -> list[str]:
    keys = []
    k1 = os.getenv("GEMINI_API_KEY", "").strip()
    k2 = (
        os.getenv("GEMINI_API_KEY_SECONDARY", "")
        or os.getenv("GEMINI_SECONDARY_API_KEY", "")
        or os.getenv("GEMINI_API_KEY_2", "")
        or os.getenv("SECOND_GEMINI_API_KEY", "")
    ).strip()

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

    def __get_active_clients(self) -> list[genai.Client]:
        keys = _get_api_keys()
        if not keys:
            return [genai.Client(api_key="")]
        return [genai.Client(api_key=k) for k in keys]

    def embed_content(self, *args, **kwargs) -> Any:
        clients = self.__get_active_clients()
        last_err = None
        for idx, client in enumerate(clients):
            try:
                return client.models.embed_content(*args, **kwargs)
            except Exception as err:
                err_str = str(err)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str) and idx < len(clients) - 1:
                    logger.warning(
                        f"[GEMINI KEY ROTATION] API Key #{idx+1} hit quota limit. Automatically failing over to Key #{idx+2} in 0ms..."
                    )
                    last_err = err
                    continue
                if idx == len(clients) - 1 and len(clients) > 1:
                    logger.error(f"[GEMINI KEY ROTATION EXHAUSTED] All {len(clients)} API keys exhausted quota: {err_str[:150]}")
                raise err
        if last_err:
            raise last_err

    def generate_content(self, *args, **kwargs) -> Any:
        clients = self.__get_active_clients()
        last_err = None
        for idx, client in enumerate(clients):
            try:
                return client.models.generate_content(*args, **kwargs)
            except Exception as err:
                err_str = str(err)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str) and idx < len(clients) - 1:
                    logger.warning(
                        f"[GEMINI KEY ROTATION] API Key #{idx+1} hit quota limit. Automatically failing over to Key #{idx+2} in 0ms..."
                    )
                    last_err = err
                    continue
                raise err
        if last_err:
            raise last_err

    def generate_content_stream(self, *args, **kwargs) -> Any:
        clients = self.__get_active_clients()
        last_err = None
        for idx, client in enumerate(clients):
            try:
                return client.models.generate_content_stream(*args, **kwargs)
            except Exception as err:
                err_str = str(err)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str) and idx < len(clients) - 1:
                    logger.warning(
                        f"[GEMINI KEY ROTATION] API Key #{idx+1} hit quota limit. Automatically failing over to Key #{idx+2} in 0ms..."
                    )
                    last_err = err
                    continue
                raise err
        if last_err:
            raise last_err


class RotatingGeminiClient:
    def __init__(self):
        self.models = ModelsProxy()


client = RotatingGeminiClient()