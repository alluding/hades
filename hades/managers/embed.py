from __future__ import annotations
from typing import (
    Optional,
    TypeVar,
    Generic,
    Dict,
    Union,
    Any
)
import requests

from ..api.start import EmbedPayload

T = TypeVar('T')


class Embed:
    def __init__(self, title: str, description: str, **kwargs: Any):
        self.base_embed = EmbedPayload(title=title, description=description)
        self.create(**kwargs)

    def create(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self.base_embed, key, value)

    def render(self) -> Dict[str, Any]:
        return {key: getattr(self.base_embed, key) for key in vars(self.base_embed) if getattr(self.base_embed, key) is not None}

    def send_to_server(self) -> Dict[str, Any]:
        server_url = "https://127.0.0.1/create"
        base_url = "https://127.0.0.1/"

        try:
            response = requests.post(server_url, json=self.render())
            if response.status_code == 200:
                return {
                    "url": base_url + response.json().get('id'),
                    "message": "success"
                }
            else:
                return {"error": f"Server returned status code {response.status_code} | {response.text}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request error: {e}"}

    def __str__(self) -> str:
        return f"Embed with title: {self.base_embed.title}"

    def to_dict(self) -> Dict[str, Any]:
        return {key: getattr(self.base_embed, key) for key in vars(self.base_embed) if getattr(self.base_embed, key) is not None}

    def __repr__(self) -> str:
        return f"Embed(title='{self.base_embed.title}', description='{self.base_embed.description}')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Embed:
        title = data.get("title", "")
        description = data.get("description", "")
        embed = cls(title, description)
        embed.create(**data)
        return embed


def hidden(value: str) -> str:
    return (
        "||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||"
        f" _ _ _ _ _ _ {value}"
    )
