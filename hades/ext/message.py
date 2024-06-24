from __future__ import annotations
from typing import Dict, List, Literal, Optional

from discord import (
    User,
    Member,
    TextChannel,
    Message,
    Emoji,
    PartialEmoji,
    errors
)
from discord.ext.commands import group, command, Cog

from ..managers.context import HadesContext, Flags
from ..managers.embed import Embed
from ..hades import Hades

from xxhash import xxh32_hexdigest
import asyncio


class Messages(Cog):
    def __init__(self, bot: Hades) -> None:
        self.bot: Hades = bot

    @Cog.listener("on_message")
    async def check_reply(self: Messages, origin: Message) -> None:
        if origin.author.bot:
            return

        reply = await self.bot.cache.get(f"auto_reply:{xxh32_hexdigest(str(self.bot.user.id))}")

        if reply and (ref := origin.reference) and (resolved := ref.resolved) and isinstance(resolved, Message):
            if resolved.author == self.bot.user:
                await origin.reply(reply[0])

    @Cog.listener("on_message")
    async def check_react(self: Messages, origin: Message) -> None:
        if origin.author.bot:
            return

        hashed = xxh32_hexdigest(str(origin.author.id))
        user, _self = await asyncio.gather(
            self.bot.cache.get(f"user_reaction:{hashed}"),
            self.bot.cache.get(f"self_reaction:{hashed}")
        )

        if _self:
            await origin.add_reaction(_self[0])

        if user:
            try:
                await origin.add_reaction(user[0])
            except errors.Forbidden as e:
                if "Reaction blocked" in str(e):
                    print(
                        f"[AUTO-REACT] {origin.author.name} has blocked you - you cannot react! Full error: {str(e)}"
                    )
                else:
                    print(
                        f"[AUTO-REACT] Forbidden error when reacting to {origin.author.name}'s message: {str(e)}"
                    )

    @command(
        name="autoreply",
        description="Toggle auto-reply for someone.",
        usage="(message)",
        example="I'm busy right now."
    )
    async def autoreply(
        self: Messages,
        ctx: HadesContext,
        *,
        message: Optional[str] = None
    ) -> Message:
        await ctx.message.delete()

        check: str = "off" if await self.bot.cache.get(f"auto_reply:{xxh32_hexdigest(str(ctx.author.id))}") else "on"

        await self.bot.cache.sadd(
            f"auto_reply:{xxh32_hexdigest(str(ctx.author.id))}",
            message
        )

        if check == "off":
            await self.bot.cache.remove(f"auto_reply:{xxh32_hexdigest(str(ctx.author.id))}")

        return await ctx.do(
            _type=Flags.APPROVE,
            emoji="✅",
            content=f"Auto-reply has been turned **{check}** with `{message}` as the message." if check else f"Auto-reply has been turned **{check}**.",
            embed=self.bot.embed
        )

    @command(
        name="selfreact",
        description="Toggle self-reaction for yourself.",
        user="(emoji)",
        example=":skull:"
    )
    async def selfreact(
        self: Messages,
        ctx: HadesContext,
        reaction: Optional[str | Emoji | PartialEmoji] = None
    ) -> Message:
        await ctx.message.delete()

        check: str = "off" if await self.bot.cache.get(f"self_reaction:{xxh32_hexdigest(str(ctx.author.id))}") else "on"

        await self.bot.cache.sadd(
            f"self_reaction:{xxh32_hexdigest(str(ctx.author.id))}",
            reaction
        )

        if check == "off":
            await self.bot.cache.remove(f"self_reaction:{xxh32_hexdigest(str(ctx.author.id))}")

        return await ctx.do(
            _type=Flags.APPROVE,
            emoji="✅",
            content=f"Auto-react has been turned **{check}**.",
            embed=self.bot.embed
        )

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

        check: str = "off" if await self.bot.cache.get(f"user_reaction:{xxh32_hexdigest(str(user.id))}") else "on"

        await self.bot.cache.sadd(
            f"user_reaction:{xxh32_hexdigest(str(user.id))}",
            reaction
        )

        if check == "off":
            await self.bot.cache.remove(f"user_reaction:{xxh32_hexdigest(str(user.id))}")

        return await ctx.do(
            _type=Flags.APPROVE,
            emoji="✅",
            content=f"Auto-react for `{user.name}` has been turned **{check}**.",
            embed=self.bot.embed
        )

    @command(
        name="selfpurge",
        description="Delete all messages sent by the bot in the current channel.",
        usage="[amount]",
        example="500"
    )
    async def selfpurge(
        self: Messages,
        ctx: HadesContext,
        amount: Optional[int] = 100
    ) -> Message:
        await ctx.message.delete()

        def is_self(message: Message) -> bool:
            return message.author == self.bot.user

        deleted: int = 0
        tasks: list = []

        async for message in ctx.channel.history(limit=amount):
            if is_self(message):
                tasks.append(message.delete())
                deleted += 1

        await asyncio.gather(*tasks)

        return await ctx.do(
            _type=Flags.APPROVE,
            emoji="✅",
            content=f"Deleted **{deleted}** messages.",
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
