from __future__ import annotations
from typing import Dict, Any

from discord.ext import commands
from discord import Message, Color
from discord.utils import cached_property

from enum import Enum, auto
from .embed import Embed, hidden


class Flags(Enum):
    APPROVE = "APPROVE"
    NEUTRAL = "NEUTRAL"
    WARN = "WARN"
    DENY = "DENY"


FlagsColorMapping: Dict[str, Color] = {
    "APPROVE": Color.green(),
    "NEUTRAL": Color.og_blurple(),
    "WARN": Color.yellow(),
    "DENY": Color.red()
}

FlagsEmojiMapping: Dict[str, Any] = {
    "APPROVE": "✅",
    "NEUTRAL": "",
    "WARN": "⚠",
    "DENY": "❌"
}


class HadesContext(commands.Context):
    flags: Dict[str, Any] = {}

    @cached_property
    def replied_message(self) -> Message:
        return self.message.reference.resolved if (reference := self.message.reference) and isinstance(reference.resolved, Message) else None

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

        if embed:
            content = Embed(
                title="Hades Self-Bot",
                color=str(color),
                description=embed_description,
                redirect="https://github.com/alluding/hades"
            ).send_to_server()["url"]

        if not embed:
            # old_content: str = f"### [Hades](https://github.com/alluding/hades)\n{embed_description}"
            content = embed_description

        return await self.send(
            content=content,
            delete_after=kwargs.get("delete_after", 5),
            **kwargs
        )

    async def send_help(self, embed: bool = False) -> Message:
        await self.message.delete()

        example = self.command.__original_kwargs__.get("example", "")

        if embed:
            content = hidden(
                Embed(
                    redirect="https://github.com/alluding/hades",
                    title=(f"Group Command: {self.command.qualified_name}" if isinstance(self.command, commands.Group) else f"Command: {self.command.qualified_name}"),
                    description=(
                        f"{self.command.description or 'N/A'}\n\n"
                        f"{self.prefix}{self.command.qualified_name} {self.command.usage or ''}\n"
                        f"{self.prefix}{self.command.qualified_name} {example}\n\n"
                        "Optional = [] | Required = ()"
                    )
                ).send_to_server()["url"]
            )
        
        if not embed:
            content = f"""```go\nHades\n\n""" + (
                f"Group Command: {self.command.qualified_name}" if isinstance(self.command, commands.Group) else f"Command: {self.command.qualified_name}\n\n"
                f"{self.command.description or 'N/A'}\n\n"
                f"{self.prefix}{self.command.qualified_name} {self.command.usage or ''}\n"
                f"{self.prefix}{self.command.qualified_name} {example}\n\n"
                "Optional = [] | Required = ()\n"
            ) + "```"

        return await self.send(content=content)
