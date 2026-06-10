import httpx

from app.config import Settings


class OllamaUnavailableError(Exception):
    pass


class OllamaTimeoutError(Exception):
    pass


class OllamaResponseError(Exception):
    pass


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model
        self._timeout = settings.llm_timeout_seconds

    @property
    def model(self) -> str:
        return self._model

    async def is_available(self) -> bool:
        return await self.ollama_reachable() and await self.model_installed()

    async def ollama_reachable(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._base_url}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def model_installed(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._base_url}/api/tags")
                if response.status_code != 200:
                    return False
                models = response.json().get("models", [])
                installed = {m.get("name", "").split(":")[0] for m in models}
                model_base = self._model.split(":")[0]
                return any(
                    m.get("name") == self._model or m.get("name", "").startswith(f"{model_base}:")
                    for m in models
                ) or model_base in installed
        except httpx.HTTPError:
            return False

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise OllamaTimeoutError(
                f"Превышено время ожидания ответа от Ollama ({self._timeout} сек.)"
            ) from exc
        except httpx.ConnectError as exc:
            raise OllamaUnavailableError(
                "Ollama недоступна. Убедитесь, что контейнер ollama запущен и модель загружена."
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaUnavailableError(f"Ошибка при обращении к Ollama: {exc}") from exc

        if response.status_code == 404 and "not found" in response.text.lower():
            raise OllamaResponseError(
                f"Модель '{self._model}' не найдена. "
                f"Загрузите её: docker exec -it ollama ollama pull {self._model}"
            )
        if response.status_code != 200:
            raise OllamaResponseError(
                f"Ollama вернула ошибку {response.status_code}: {response.text}"
            )

        data = response.json()
        message = data.get("message", {})
        content = message.get("content", "").strip()
        if not content:
            raise OllamaResponseError("Ollama вернула пустой ответ")
        return content
