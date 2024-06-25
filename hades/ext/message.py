from __future__ import annotations
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, HttpUrl

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
import discord

from ..managers.context import HadesContext, Flags
from ..managers.embed import Embed
from ..hades import Hades

from xxhash import xxh32_hexdigest
import datetime
import asyncio

class Messages(Cog):
    def __init__(self, bot: Hades) -> None:
        self.bot: Hades = bot

    @Cog.listener("on_message_delete")
    async def deletes(self: Messages, message: Message) -> None:
        if not message.author.bot and message.author != self.bot.user:
            try:
                await self.bot.cache.sadd(
                    f"snipe:{xxh32_hexdigest(str(message.channel.id))}",
                    self.bot.dump(message),
                )
            except Exception as e:
                self.bot.logger.error(e)

    @Cog.listener("on_message_edit")
    async def edits(
        self: Messages,
        before: Message,
        after: Message
    ) -> None:
        if not after.author.bot and after.author != self.bot.user:
            try:
                await self.bot.cache.sadd(
                    f"editsnipe:{xxh32_hexdigest(str(after.channel.id))}",
                    [self.bot.dump(before), self.bot.dump(after)],
                )
            except Exception as e:
                self.bot.logger.error(e)

    @Cog.listener("on_message")
    async def check_reply(self: Messages, origin: Message) -> None:
        if origin.author.bot:
            return

        reply = await self.bot.cache.get(f"auto_reply:{xxh32_hexdigest(str(self.bot.user.id))}")

        if reply and (ref := origin.reference) and (resolved := ref.resolved) and isinstance(resolved, Message):
            if resolved.author == self.bot.user and origin.author != self.bot.user:
                await origin.reply(reply[0])
        
        if reply and self.bot.user.mentioned_in(origin) and origin.reference is None:
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
        name="editsnipe",
        aliases=["es"],
        description="Snipe any deleted message/s.",
        usage="(index)",
        example="1"
    )
    async def editsnipe(
        self: Messages,
        ctx: HadesContext,
        index: int = 1
    ) -> Message:
        await ctx.message.delete()

        snipes = await self.bot.cache.get(f"editsnipe:{xxh32_hexdigest(str(ctx.channel.id))}")
        
        if not snipes or index <= 0 or index > len(snipes):
            return await ctx.do(
                _type=Flags.WARN,
                emoji="❌",
                content="There are no edited messages to snipe."
            )
        
        before, after = snipes[0][0], snipes[0][1]
        
        return await ctx.send(
            content=(
                f"Sniped edited content from **{before['author']['name']}** - {discord.utils.format_dt(after['timestamp'])}:\n\n"
                f"```\nBefore -> {before['content']}\nAfter -> {after['content']}```\n\n"
                f"{index}/{len(snipes)} messages sniped.\n"
            ).strip(),
            delete_after=5
        )

    @command(
        name="snipe",
        aliases=["s"],
        description="Snipe any deleted message/s.",
        usage="(index)",
        example="1"
    )
    async def snipe(
        self: Messages,
        ctx: HadesContext,
        index: int = 1
    ) -> Message:
        await ctx.message.delete()

        snipes = await self.bot.cache.get(f"snipe:{xxh32_hexdigest(str(ctx.channel.id))}")
        
        if not snipes or index <= 0 or index > len(snipes):
            return await ctx.do(
                _type=Flags.WARN,
                emoji="❌",
                content="There are no deleted messages to snipe."
            )
        
        message = snipes[index - 1]
        
        return await ctx.send(
            content=(
                f"Sniped content from **{message['author']['name']}** - {discord.utils.format_dt(message['timestamp'])}:\n\n"
                f"```\n{message['content']}```\n\n"
                f"{index}/{len(snipes)} messages sniped.\n"
            ).strip(),
            delete_after=5
        )   
    
    @command(
        name="clearsnipes",
        aliases=["cs"],
        description="Clear the snipes of edited & deleted messages."
    )
    async def clearsnipes(self: Messages, ctx: HadesContext) -> Message:
        for query in [
            f"snipe:{xxh32_hexdigest(str(ctx.channel.id))}",
            f"editsnipe:{xxh32_hexdigest(str(ctx.channel.id))}"
        ]:
            await self.bot.cache.remove(query)

        return await ctx.message.add_reaction("👍")

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

        if not message and check != "off":
            return await ctx.do(
                _type=Flags.WARN,
                emoji="❌",
                content="Hey! You need a `message` as well!"
            )

        await self.bot.cache.sadd(
            f"auto_reply:{xxh32_hexdigest(str(ctx.author.id))}",
            message
        )

        if check == "off":
            await self.bot.cache.remove(f"auto_reply:{xxh32_hexdigest(str(ctx.author.id))}")

        return await ctx.do(
            _type=Flags.APPROVE,
            emoji="✅",
            content=f"Auto-reply has been turned **{check}** with `{message}` as the message." if check == "off" else f"Auto-reply has been turned **{check}**.",
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
