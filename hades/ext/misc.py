from __future__ import annotations
from typing import Dict, List

from discord import (
    User,
    Member,
    DMChannel,
    Message,
    Forbidden
)
from discord.ext.commands import group, command, Cog
from discord.errors import CaptchaRequired

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


async def setup(bot: Hades) -> None:
    await bot.add_cog(Miscellaneous(bot))
