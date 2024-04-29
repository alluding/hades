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
    HypeSquadHouse,
    Gift
)
from discord.ext.commands import group, command, Cog

from ..managers.context import HadesContext, Flags
from ..managers.embed import Embed
from ..hades import Hades

import asyncio
import re

HYPESQUAD: Dict[str, Any] = {
    "balance": HypeSquadHouse.balance,
    "bravery": HypeSquadHouse.bravery,
    "brilliance": HypeSquadHouse.brilliance
}
NITRO_REGEX = re.compile(r"(discord.com/gifts/|discordapp.com/gifts/|discord.gift/)([a-zA-Z0-9]+)")
PRIVNOTE_REGEX = re.compile(r"https://privnote\.com/[a-zA-Z0-9]+#[a-zA-Z0-9]+")

class Profile(Cog):
    def __init__(self: Hades, bot: Hades) -> None:
        self.bot: Hades = bot

        self.used_notes: List[str] = []
        self.used_codes: List[str] = []

    def can_nitro(self: Profile, message: Message) -> bool:
        sniper = self.bot.config["settings"].get("nitro_sniper", False)
        return (
            sniper
            and (match := NITRO_REGEX.search(message.content))
            and match.group(2) not in self.used_codes
        )

    def can_privnote(self: Profile, message: Message) -> bool:
        sniper = self.bot.config["settings"].get("privnote_sniper", False)
        return (
            sniper
            and (match := PRIVNOTE_REGEX.search(message.content))
            and match.group(0) not in self.used_notes
        )

    @Cog.listener("on_message")
    async def snipe_privnote(self: Profile, message: Message) -> None:
        if self.can_privnote(message):
            ...
            # I will finish this later.

    @Cog.listener("on_message")
    async def snipe_nitro(self: Profile, message: Message) -> None:
        if self.can_nitro(message):
            if match := NITRO_REGEX.search(message.content):
                code = match.group(2)
                gift: Gift = await self.bot.fetch_gift(code)
                try:
                    await gift.redeem()
                    self.bot.logger.info(f"Successfully sniped nitro code! | {code}")
                    self.used_codes.append(code)
                except Exception as e:
                    self.bot.logger.error(f"Failed to snipe nitro code! | {code}")
                    self.used_codes.append(code)
                
    @command(
        name="nitrosniper",
        description="Toggle the Nitro sniper on or off.",
        usage="(on/off)",
        example="on"
    )
    async def nitrosniper(
        self: Profile,
        ctx: HadesContext,
        option: str
    ) -> Message:
        option = option.lower()
        
        if option not in ["on", "off"]:
            return await ctx.do(
                _type=Flags.ERROR,
                emoji="❌",
                content="Invalid option! Please use `on` or `off`."
            )

        sniper = option == "on"
        self.bot.config["settings"]["nitro_sniper"] = sniper
        
        return await ctx.do(
            _type=Flags.NEUTRAL,
            emoji="✅",
            content=f"Nitro sniper has been turned {'on' if sniper else 'off'}."
        )

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
