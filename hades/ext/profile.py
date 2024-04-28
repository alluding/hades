"""
I got terminated on an alt while using profile-related commands in rapid succession. 
Be careful when using these commands quickly; make sure to keep some delay between them.
"""

from __future__ import annotations
from typing import Dict, List, Any

from discord import (
    User,
    Member,
    DMChannel,
    Message,
    HypeSquadHouse
)
from discord.ext.commands import group, command, Cog

from ..managers.context import HadesContext, Flags
from ..managers.embed import Embed
from ..hades import Hades

import asyncio

HYPESQUAD: Dict[str, Any] = {
    "balance": HypeSquadHouse.balance,
    "bravery": HypeSquadHouse.bravery,
    "brilliance": HypeSquadHouse.brilliance
}

class Profile(Cog):
    def __init__(self: Hades, bot: Hades) -> None:
        self.bot: Hades = bot

    @command(
        name="hypesquad",
        description="Change your profile's hypesquad team!",
        example="brilliance",
        usage="(team)"
    )
    async def hypesquad(
        self: Profile, 
        ctx: HadesContext, 
        *, 
        team: str
    ) -> Message:
        await ctx.message.delete()
        await self.bot.user.edit(house=HYPESQUAD[team])

        return await ctx.do(
            _type=Flags.NEUTRAL,
            emoji="🏆",
            content=f"Hypesquad team successfully changed to: {team}"
        )
        
    @command(
        name="bio",
        description="Change your profile's bio!",
        example="My new bio.",
        usage="(bio)"
    )
    async def bio(
        self: Profile, 
        ctx: HadesContext, 
        *, 
        bio: str
    ) -> Message:
        await ctx.message.delete()
        await self.bot.user.edit(bio=bio)

        return await ctx.do(
            _type=Flags.NEUTRAL,
            emoji="📖",
            content=f"Bio successfully changed to: {bio}"
        )


async def setup(bot: Hades) -> None:
    await bot.add_cog(Profile(bot))
