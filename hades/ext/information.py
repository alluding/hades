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
from ..util import resolve_user
from ..hades import Hades

import asyncio

class Information(Cog):
    def __init__(self, bot: Hades) -> None:
        self.bot: Hades = bot
        self.resolve_time: Dict[str, float] = {}

    @command(
        name="test"
    )
    async def test(self: Information, ctx: HadesContext) -> Message:
        """
        A test command for the custom embed API.
        """
        await ctx.do(
            _type=Flags.DENY,
            content="test"
        )

    @command(
        name="resolve",
        description="Username to IP address resolver!",
        usage="(username) (platform)",
        example="anime ps/xbl"
    )
    async def resolve(
        self: Information,
        ctx: HadesContext,
        username: str,
        platform: Literal["ps", "xbl"]
    ) -> Message:
        await ctx.message.delete()

        if ctx.author.id in self.resolve_time and self.resolve_time[ctx.author.id] > asyncio.get_event_loop().time():
            return await ctx.do(
                _type=Flags.WARN,
                content=f"Rate limited for `{round(self.resolve_time[ctx.author.id] - asyncio.get_event_loop().time())}` seconds.",
                embed=self.bot.embed,
                delete_after=12
            )

        data = resolve_user(username, platform)

        if isinstance(data, str) and "Rate limited" in data:
            self.resolve_time[ctx.author.id] = asyncio.get_event_loop().time() + 1800
            
            return await ctx.do(
                _type=Flags.WARN,
                content=data,
                embed=self.bot.embed,
                delete_after=12
            )
            
        if "User wasn't found" in data:
            return await ctx.do(
                _type=Flags.ERROR,
                content=data,
                embed=self.bot.embed,
                delete_after=12
            )
            
        return await ctx.send(
            content="\n".join([f"**{key}** » `{value}`" for key, value in data.items()]),
            delete_after=12
        )


async def setup(bot: Hades) -> None:
    await bot.add_cog(Information(bot))
