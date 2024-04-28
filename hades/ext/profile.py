"""
I got terminated on an alt while using profile-related commands in rapid succession. 
Be careful when using these commands quickly; make sure to keep some delay between them.
"""

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


class Profile(Cog):
    def __init__(self: Hades, bot: Hades) -> None:
        self.bot: Hades = bot

    @command(
        name="bio",
        description="Change your profile's bio!",
        example="My new bio.",
        usage="(bio)"
    )
    async def bio(self: Profile, ctx: HadesContext, *, bio: str) -> Message:
        await ctx.message.delete()
        await self.bot.user.edit(bio=bio)

        return await ctx.do(
            _type=Flags.NEUTRAL,
            emoji="📖",
            content=f"Bio successfully changed to: {bio}"
        )


async def setup(bot: Hades) -> None:
    await bot.add_cog(Profile(bot))
