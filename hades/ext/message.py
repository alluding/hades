from __future__ import annotations
from typing import Dict, List, Literal, Optional

from discord import (
    User,
    Member,
    TextChannel,
    Message,
    Emoji,
    PartialEmoji
)
from discord.ext.commands import group, command, Cog

from ..managers.context import HadesContext, Flags
from ..managers.embed import Embed
from ..hades import Hades

import asyncio


class Messages(Cog):
    def __init__(self, bot: Hades) -> None:
        self.bot: Hades = bot
        self.react: Dict[int, str] = {}

    @Cog.listener("on_message")
    async def check_react(self: Messages, origin: Message) -> None:
        if origin.author.bot:
            return

        if origin.author.id in self.react:
            reaction = self.react[origin.author.id]
            await origin.add_reaction(reaction)

    @command(
        name="autoreact",
        description="Toggle auto-reaction for someone.",
        usage="(user) [reaction/emoji]",
        example="dancers. :skull:"
    )
    async def autoreact(
        self: Messages,
        ctx: HadesContext,
        user: User,
        reaction: Optional[str | Emoji | PartialEmoji] = None
    ) -> Message:
        await ctx.message.delete()

        check: str = "off" if user.id in self.react else "on"
        self.react[user.id]: str | None = reaction if check == "on" else None

        if check == "off":
            del self.react[user.id]

        return await ctx.do(
            _type=Flags.APPROVE,
            emoji="✅",
            content=f"Auto-react for {user.name} has been turned {check}.",
            embed=self.bot.embed
        )

    @command(
        name="test"
    )
    async def test(self: Messages, ctx: HadesContext) -> Message:
        """
        A test command for the custom embed API.
        """
        await ctx.do(
            _type=Flags.DENY,
            content="test",
            embed=self.bot.embed
        )


async def setup(bot: Hades) -> None:
    await bot.add_cog(Messages(bot))
