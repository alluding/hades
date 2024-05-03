from __future__ import annotations
from typing import Dict, List, Literal

from discord import (
    User,
    Member,
    TextChannel,
    Message
)
from discord.ext.commands import group, command, Cog

from ..managers.context import HadesContext, Flags
from ..managers.embed import Embed
from ..hades import Hades

import asyncio

class Information(Cog):
    def __init__(self, bot: Hades) -> None:
        self.bot: Hades = bot

    @command(
        name="test"
    )
    async def test(self: Information, ctx: HadesContext) -> Message:
        """
        A test command for the custom embed API.
        """
        await ctx.do(
            _type=Flags.DENY,
            content="test",
            embed=self.bot.embed
        )

async def setup(bot: Hades) -> None:
    await bot.add_cog(Information(bot))
