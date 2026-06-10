from typing import Any

import httpx

from app.core.config import settings


class BitrixClient:
    def __init__(self) -> None:
        self.webhook_url = settings.bitrix_webhook_url.rstrip("/") if settings.bitrix_webhook_url else ""
        self.enabled = bool(self.webhook_url)

    def call_sync(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.enabled:
            return {"result": None, "mock": True, "method": method, "params": params or {}}
        url = f"{self.webhook_url}/{method}"
        with httpx.Client(timeout=20.0) as client:
            response = client.post(url, json=params or {})
            response.raise_for_status()
            return response.json()

    def send_bot_message(self, dialog_id: str, message: str) -> dict[str, Any]:
        params: dict[str, Any] = {"DIALOG_ID": dialog_id, "MESSAGE": message}
        if settings.bitrix_bot_id:
            params["BOT_ID"] = settings.bitrix_bot_id
        return self.call_sync("imbot.message.add", params)

    def create_task(self, title: str, description: str, responsible_id: int, deadline_iso: str | None = None) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "TITLE": title,
            "DESCRIPTION": description,
            "RESPONSIBLE_ID": responsible_id,
        }
        if deadline_iso:
            fields["DEADLINE"] = deadline_iso
        return self.call_sync("tasks.task.add", {"fields": fields})
