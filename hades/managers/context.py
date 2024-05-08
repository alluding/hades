from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING

from discord.ext import commands
from discord import Message, Color, Embed
from discord.utils import cached_property

from enum import Enum, auto
from .embed import rgb_to_hex, get_embed, hidden

if TYPE_CHECKING:
    from ..hades import Hades
    
class Flags(Enum):
    APPROVE = "APPROVE"
    NEUTRAL = "NEUTRAL"
    WARN = "WARN"
    DENY = "DENY"


FlagsColorMapping: Dict[str, Color] = {
    "APPROVE": Color.green(),
    # "NEUTRAL": Color.og_blurple(),
    "NEUTRAL": Color(800080),
    "WARN": Color.yellow(),
    "DENY": Color.red()
}

FlagsEmojiMapping: Dict[str, Any] = {
    "APPROVE": "✅",
    "NEUTRAL": "",
    "WARN": "⚠",
    "DENY": "❌"
}


class HadesContext(commands.Context["Hades"]):
    bot: Hades

    @cached_property
    def replied(self: Context) -> Optional[Message]:
        reference = getattr(self.message, "reference", None)
        return (
            reference.resolved
            if reference and isinstance(reference.resolved, Message)
            else None
        )
        
    async def send(self, *args, **kwargs) -> Message:
        if kwargs.get("embed"):
            ...

        previous_message = kwargs.pop("previous_message", None)
        return await (previous_message.edit if previous_message else super().send)(*args, **kwargs)

    async def do(
        self,
        _type: Flags = Flags.NEUTRAL,
        content: str = "",
        emoji: str = "",
        embed: bool = False,
        **kwargs
    ) -> Message:
        if not emoji:
            emoji = FlagsEmojiMapping.get(_type.value, "❓")

        color = FlagsColorMapping.get(_type.value, 0xffffff)
        embed_description = f"{emoji} » {content}"

        embed: Embed = Embed(
            title="Hades Self-Bot",
            color=color,
            description=embed_description
        )
        url: str = await get_embed(embed)

        if embed:
            content = hidden(url)

        if not embed:
            content = embed_description

        return await self.send(
            content=content,
            delete_after=kwargs.get("delete_after", 5),
            **kwargs
        )

    async def send_help(self, embed: bool = False) -> Message:
        await self.message.delete()

        example = self.command.__original_kwargs__.get("example", "")
        embed: Embed = Embed(
            url="https://github.com/alluding/hades",
            title=(f"Group Command: {self.command.qualified_name}" if isinstance(self.command, commands.Group) else f"Command: {self.command.qualified_name}"),
            description=(
                f"{self.command.description or 'N/A'}\n\n"
                f"{self.prefix}{self.command.qualified_name} {self.command.usage or ''}\n"
                f"{self.prefix}{self.command.qualified_name} {example}\n\n"
                "Optional = [] | Required = ()"
            ),
            color=FlagsColorMapping.get("NEUTRAL", 000000)
        )
        url: str = await get_embed(embed)

        if embed:
            content = hidden(url)

        if not embed:
            content = f"""```go\nHades\n\n""" + (
                f"Group Command: {self.command.qualified_name}" if isinstance(self.command, commands.Group) else f"Command: {self.command.qualified_name}\n\n"
                f"{self.command.description or 'N/A'}\n\n"
                f"{self.prefix}{self.command.qualified_name} {self.command.usage or ''}\n"
                f"{self.prefix}{self.command.qualified_name} {example}\n\n"
                "Optional = [] | Required = ()\n"
            ) + "```"

        return await self.send(content=content)
