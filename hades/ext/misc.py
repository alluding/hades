from __future__ import annotations
from typing import (
    Dict,
    List,
    Any,
    Union,
    Coroutine
)

from discord import (
    User,
    Member,
    DMChannel,
    Message,
    Forbidden
)
from discord.ext.commands import group, command, Cog
from discord.errors import CaptchaRequired
import discord

from ..managers.context import HadesContext, Flags, FlagsEmojiMapping
from ..managers.embed import Embed
from ..constants import PACKS
from ..hades import Hades

from xxhash import xxh32_hexdigest
import asyncio
import random

class FastRoutine:
    """
    A simple class for fast gathering, and execution of coroutines.
    """

    func: Coroutine[Any, Any, Any]
    repetitions: int

    def __init__(self, func: Coroutine[Any, Any, Any], repetitions: int = 24) -> None:
        self.func: Coroutine[Any, Any, Any] = func
        self.repetitions: int = repetitions

    async def gather_coroutines(self) -> None:
        tasks: List[asyncio.Task[Any]] = [
            asyncio.create_task(self.func()) for _ in range(self.repetitions)
        ]
        await asyncio.gather(*tasks)

class Miscellaneous(Cog):
    def __init__(self, bot: Hades) -> None:
        self.bot: Hades = bot

        self.packing: bool = False
    
    @Cog.listener("on_message")
    async def check_insult(self: Miscellaneous, origin: Message) -> None:
        if await self.bot.cache.get(
            f"insult:{xxh32_hexdigest(str(origin.author.id))}"
        ):
            await origin.reply(
                "# " + random.choice(PACKS)
            )

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

        total: int = len(self.bot.friends)
        new: int = 0

        while new <= total:
            for friend in self.bot.friends:
                if new >= total:
                    return await ctx.do(
                        _type=Flags.APPROVE,
                        content=f"Successfully finished the mass DM to `{total}` users!",
                        embed=self.bot.embed
                    )
                    break

                try:
                    dm = getattr(friend.user, "dm_channel", None) or await friend.user.create_dm()
                    await dm.send(
                        f"{friend.user.mention}\n\n"
                        f"{message}"
                    )
                    new += 1
                except (CaptchaRequired, Forbidden):
                    self.bot.logger.error(f"Failed to send a DM to {friend.user}! (`Captcha Required / Forbidden!`)")

                await asyncio.sleep(timeout)

    @group(
        name="insult",
        description="Insult a user until stopped.",
        invoke_without_command=True
    )
    async def insult(self: Miscellaneous, ctx: HadesContext) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.do(
                _type=Flags.WARN,
                content=f"Invalid insult command passed... - `{ctx.prefix}insult begin/end`",
                embed=self.bot.embed
            )
        
    @insult.command(
        name="begin",
        description="Begin the insulting on a user.",
        usage="(user)",
        example="ryu"
    )
    async def begin(
        self: Miscellaneous, 
        ctx: HadesContext,
        *,
        user: Union[Member, User]
    ) -> Message:
        await ctx.message.delete()

        if await self.bot.cache.get(
            f"insult:{xxh32_hexdigest(str(user.id))}"
        ):
            return await ctx.do(
                _type=Flags.WARN,
                emoji="❌",
                content="This user is already being insulted!"
            )

        await self.bot.cache.sadd(
            f"insult:{xxh32_hexdigest(str(user.id))}",
            True
        )

        return await ctx.do(
            _type=Flags.APPROVE,
            emoji="✅",
            content=f"Starting auto-insulter on **{user.name}**"
        )

    @insult.command(
        name="end",
        description="Stop the auto-insulting."
    )
    async def end(
        self: Miscellaneous, 
        ctx: HadesContext, 
        user: Union[User, Member]
    ) -> None:
        if await self.bot.cache.get(
            f"insult:{xxh32_hexdigest(str(user.id))}"
        ):
            await self.bot.cache.remove(
                f"insult:{xxh32_hexdigest(str(user.id))}"
            )

            await ctx.message.add_reaction("👍")

    @group(
        name="pack",
        description="Commands related to packing."
    )
    async def pack(self: Miscellaneous, ctx: HadesContext) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.do(
                _type=Flags.WARN,
                content=f"Invalid pack command passed... - `{ctx.prefix}pack start/end`",
                embed=self.bot.embed,
            )
            
    @pack.command(
        name="start",
        description="Start sending words from a random pack one by one in the current channel."
    )
    async def start(self: Miscellaneous, ctx: HadesContext) -> None:
        await ctx.message.delete()

        channel: Union[
            discord.DMChannel,
            discord.TextChannel,
            discord.abc.MessageableChannel
        ] = ctx.channel

        if self.packing:
            return

        self.packing: bool = True

        while self.packing:
            pack = random.choice(PACKS)
            words = pack.split()

            if not self.packing:
                break

            while len(words) >= 4:
                chunk, words = words[:4], words[4:]

                await channel.send("# " + " ".join(chunk).lower())
                await asyncio.sleep(0.9)

            if words:
                await channel.send("# " + " ".join(words).lower())

            if self.packing:
                await asyncio.sleep(1)

    @pack.command(
        name="stop",
        description="Stop the packing process.",
    )
    async def stop(self: Miscellaneous, ctx: HadesContext) -> None:
        await ctx.message.delete()

        if not self.packing:
            return

        self.packing: bool = False


async def setup(bot: Hades) -> None:
    await bot.add_cog(Miscellaneous(bot))
