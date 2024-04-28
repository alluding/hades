from __future__ import annotations
from typing import (
    List,
    Dict,
    Any,
    overload,
    Union,
    TypedDict,
    TYPE_CHECKING,
    Tuple,
    Optional
)

from discord.ext.commands import Bot
from discord import (
    TextChannel,
    Message,
    Guild,
    User
)
from discord.ext import commands

from datetime import datetime
from tls_client import Session
from pathlib import Path

import logging
import json

from .managers.context import HadesContext

if TYPE_CHECKING:
    class Config(TypedDict):
        token: str
        settings: Dict[str, list[str]]


class Hades(Bot):
    """
    An advanced Discord self-bot made in Python, relying on discord.py-self.
    """
    config: Config = json.load(open("config.json", "r"))

    def __init__(self, options: Any = None) -> Bot:
        super().__init__(
            command_prefix=self.get_prefix,
            description="Hades Discord Self-Bot",
            strip_after_prefix=True,
            self_bot=True,
            help_command=None,
            # **options
        )

        self.config_logger()

        self.start_time: datetime = datetime.utcnow()
        self.session: Session
        self.ready: bool = False

        self.run()

    @overload
    def dump(self: Hades, message: Message) -> Dict[str, Union[Dict[str, Union[int, str, bool]], List[str], float, int]]:
        ...

    def dump(self: Hades, message: Message) -> Dict[str, Union[str, float, int, List[Dict[str, Union[str, int]]]]]:
        guild: Guild = message.guild
        channel: TextChannel = message.channel
        author: User = message.author

        attachments: List[str] = [
            attachment.url for attachment in (message.attachments + [
                embed.thumbnail or embed.image
                for embed in message.embeds if embed.type == "image"
            ])
        ]
        stickers: List[str] = [sticker.url for sticker in message.stickers]
        embeds: List[Dict[str, Union[str, int]]] = [
            embed.to_dict()
            for embed in message.embeds[:8]
            if embed.type not in ("image", "video")
        ]

        return {
            "guild": {
                "id": guild.id,
                "name": guild.name,
                "chunked": guild.chunked,
                "member_count": guild.member_count,
            },
            "channel": {
                "id": channel.id,
                "name": channel.name,
                "position": channel.position,
                "category_id": channel.category_id
            },
            "author": {
                "name": author.name,
                "id": author.id,
                "discriminator": author.discriminator,
                "bot": author.bot,
                "nick": author.nick,
                "avatar": author.avatar.url if author.avatar else None,
            },
            "attachments": attachments,
            "stickers": stickers,
            "embeds": embeds,
            "content": message.content,
            "timestamp": message.created_at.timestamp(),
            "id": message.id
        }

    @property
    def extensions(self: Hades) -> List[str]:
        exts = [ext.parts for ext in Path('./hades/ext').glob('**/[!__]*.py')]
        return [self._remove_suffix('.'.join(parts)) for parts in exts]

    def _remove_suffix(self: Hades, text: str) -> str:
        return text.removesuffix('.py')

    def config_logger(self: Hades) -> logging.Logger:
        logger: logging.Logger = logging.getLogger("discord")
        logger.setLevel(logging.INFO)
        self.logger: logging.Logger = logger
        return self.logger

    def fetch_uptime(self: Hades) -> Tuple[int, int, int, int]:
        delta_seconds = round((datetime.utcnow() - self.start_time).total_seconds())
        days, remaining = divmod(delta_seconds, 86400)
        hours, remaining = divmod(remaining, 3600)
        minutes, seconds = divmod(remaining, 60)
        return days, hours, minutes, seconds

    def run(self: Hades) -> Hades:
        super().run(
            token=self.config["token"],
            reconnect=True
        )

    async def on_ready(self: Hades) -> None:
        self.logger.info(f"Hades | Logged in as {self.user}")

        await self.load_extensions()

        if not self.ready:
            self.ready = True

        self.session = Session(
            client_identifier="chrome_119",
            random_tls_extension_order=True
        )

    async def load_ext(
        self: Hades,
        name: str,
        *,
        package: Optional[str] = None,
        cache: bool = False
    ) -> None:
        if cache:
            ...

        return await super().load_extension(name, package=package)

    async def load_extensions(self: Hades) -> None:
        for ext in self.extensions:
            try:
                await self.load_ext(ext)
                self.logger.info(f"Successfully loaded {ext}.")
            except Exception as e:
                self.logger.error(f"Failed to load {ext}. | {e}")

    async def get_context(
        self: Hades,
        origin: Message,
        *,
        cls: Optional = None
    ) -> HadesContext:
        return await super().get_context(
            origin,
            cls=cls or HadesContext
        )

    async def get_prefix(self: Hades, message: Message) -> Any:
        guild: Guild = message.guild
        user: User = message.author

        prefixes = list(self.config["settings"]["prefixes"])

        return commands.when_mentioned_or(*prefixes)(self, message)