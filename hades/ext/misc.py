from __future__ import annotations
from typing import Dict, List

from discord import (
    User,
    Member,
    DMChannel,
    Message
)
from discord.ext.commands import group, command, Cog

from ..managers.context import HadesContext, Flags
from ..managers.embed import Embed
from ..hades import Hades

import asyncio


class Miscellaneous(Cog):
    def __init__(self, bot: Hades) -> None:
        self.bot: Hades = bot

    @command(
        name="massdm",
        description="Send a message to all your friends!",
        example="hi! 5",
        usage="(message) [timeout]"
    )
    async def massdm(
        self: Miscellaneous,
        ctx: HadesContext,
        message: str,
        *,
        timeout: int = 3
    ) -> Message:
        await ctx.message.delete()

        for friend in self.bot.friends:
            direct = await friend.user.create_dm()
            await direct.send(
                f"{friend.user.mention}\n\n"
                f"{message}"
            )
            await asyncio.sleep(timeout)


async def setup(bot: Hades) -> None:
    await bot.add_cog(Miscellaneous(bot))
