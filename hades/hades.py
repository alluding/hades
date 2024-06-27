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
    Optional,
    ClassVar,
)
from typing_extensions import override

from discord.ext import commands
from discord import (
    TextChannel,
    Message,
    Guild,
    User,
    DMChannel,
)
from curl_cffi.requests import Session
from datetime import datetime
from pathlib import Path

import logging
import json

from .managers.context import HadesContext, Flags
from .managers.cache import ExpiringDict
from .managers.embed import Embed

if TYPE_CHECKING:
    class Config(TypedDict):
        token: str
        settings: Dict[str, Union[bool, List[str]]]
        snipers: Dict[str, bool]

__all__: Tuple[str, ...] = ("Hades",)

class Hades(commands.Bot):
    """
    An advanced Discord self-bot made in Python, relying on discord.py-self.
    """

    config: ClassVar[Config] = json.load(open("config.json", "r"))
    ready: ClassVar[bool] = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            *args,
            **kwargs,
            command_prefix=self.get_prefix,
            description="Hades Discord Self-Bot",
            strip_after_prefix=True,
            self_bot=True,
            proxy=self.config["settings"]["proxy"],
        )

        self.config_logger()

        self.start_time: datetime = datetime.utcnow()
        self.embed: bool = False  # self.config["settings"]["embed"]

        self.cache: ExpiringDict = ExpiringDict()
        self.session: Session

        self.run()

    @overload
    def dump(self, message: Message) -> Dict[str, Union[Dict[str, Union[int, str, bool]], List[str], float, int]]:
        ...

    def dump(self, message: Message) -> Dict[str, Union[str, float, int, List[Dict[str, Union[str, int]]]]]:
        guild: Optional[Guild] = message.guild
        channel: Union[TextChannel, DMChannel] = message.channel
        author: User = message.author

        attachments: List[str] = [attachment.url for attachment in message.attachments] + [
            embed.thumbnail.url if embed.thumbnail else embed.image.url for embed in message.embeds if embed.type == "image"
        ]
        stickers: List[str] = [sticker.url for sticker in message.stickers]
        embeds: List[Dict[str, Union[str, int]]] = [
            embed.to_dict() for embed in message.embeds[:8] if embed.type not in ("image", "video")
        ]

        channel_info = {
            "id": channel.id,
            **(
                {
                    "name": channel.name,
                    "position": channel.position,
                    "category_id": channel.category_id,
                }
                if isinstance(channel, TextChannel)
                else {"type": "DM"}
            ),
        }

        return {
            "guild": {
                "id": guild.id,
                "name": guild.name,
                "chunked": guild.chunked,
                "member_count": guild.member_count,
            }
            if guild
            else None,
            "channel": channel_info,
            "author": {
                "name": author.name,
                "id": author.id,
                "discriminator": author.discriminator,
                "bot": author.bot,
                "nick": getattr(author, "nick", None),
                "avatar": author.avatar.url if author.avatar else None,
            },
            "attachments": attachments,
            "stickers": stickers,
            "embeds": embeds,
            "content": message.content,
            "timestamp": datetime.utcfromtimestamp(message.created_at.timestamp()),
            "id": message.id,
        }

    @override
    async def get_context(self, origin: Message, *, cls: Optional[type[HadesContext]] = None) -> HadesContext:
        return await super().get_context(origin, cls=cls or HadesContext)

    @property
    def extensions(self) -> List[str]:
        return [
            str(ext.with_suffix("")).replace("\\", ".").replace("/", ".")
            for ext in Path("./hades/ext").glob("**/[!__]*.py")
        ]

    def config_logger(self) -> logging.Logger:
        logger = logging.getLogger("discord")
        logger.setLevel(logging.INFO)
        self.logger: logging.Logger = logger
        return self.logger

    def fetch_uptime(self) -> Tuple[int, int, int, int]:
        delta_seconds = round((datetime.utcnow() - self.start_time).total_seconds())
        days, hours, minutes, seconds = (
            divmod(delta_seconds, 86400)[0],
            *divmod(divmod(delta_seconds, 86400)[1], 3600),
            *divmod(divmod(divmod(delta_seconds, 86400)[1], 3600)[1], 60),
        )
        return days, hours, minutes, seconds

    def run(self) -> None:
        super().run(token=self.config["token"], reconnect=True)

    async def on_ready(self) -> None:
        self.logger.info(f"Hades | Logged in as {self.user}")

        await self.load_extensions()

        if not self.ready:
            self.ready = True

        self.session = Session(impersonate="chrome119", headers={})

    async def load_ext(self, name: str, *, package: Optional[str] = None, cache: bool = False) -> None:
        if cache:
            ...

        return await super().load_extension(name, package=package)

    async def load_extensions(self) -> None:
        for ext in self.extensions:
            try:
                await self.load_ext(ext)
                self.logger.info(f"Successfully loaded {ext}.")
            except Exception as e:
                self.logger.error(f"Failed to load {ext}. | {e}")

    async def get_prefix(self, message: Message) -> Any:
        prefixes = list(self.config["settings"]["prefixes"])
        return commands.when_mentioned_or(*prefixes)(self, message)

    async def on_command_error(self, ctx: HadesContext, error: Exception) -> Optional[Message]:
        if isinstance(
            error, (
                commands.CommandNotFound, 
                commands.NotOwner, 
                commands.CheckFailure, 
                commands.DisabledCommand, 
                commands.UserInputError
            )
        ):
            return
    
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.do(
                _type=Flags.WARN, 
                content=f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", 
                emoji="⏳", 
                delete_after=5, 
                embed=self.embed
            )

        if isinstance(error, commands.MemberNotFound):
            return await ctx.do(
                _type=Flags.WARN, 
                content="I was unable to find that member, or the ID is invalid.", 
                embed=self.embed
            )
        
        if isinstance(error, commands.UserNotFound):
            return await ctx.do(
                _type=Flags.WARN, 
                content="I was unable to find that user, or the ID is invalid.", 
                embed=self.embed
            )

        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help(embed=self.embed)
