"""
MIT License

Copyright (c) 2021 kreusada

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
import logging

from redbot.core import commands
from redbot.core.utils.chat_formatting import box

log = logging.getLogger("red.kreusada.access")


class Access(commands.Cog):
    """
    Get member access to guild categories, text and voice channels.
    """

    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        global access
        if access:
            try:
                self.bot.remove_command("access")
            except Exception as e:
                log.info(e)
                self.bot.add_command("access")

    async def send_access(self, ctx, member: discord.Member, access_type: str):
        if access_type == "text":
            build = ctx.guild.text_channels
            prefix = "#"
            access_type += " channels"
            singular_access_type = "Text Channel"
        elif access_type == "voice":
            build = ctx.guild.voice_channels
            prefix = "#"
            access_type += " channels"
            singular_access_type = "Voice Channel"
        else:
            build = ctx.guild.categories
            prefix = ""
            singular_access_type = "Category"

        can = []
        cant = []
        user = await self.bot.get_or_fetch_member(guild=ctx.guild, member_id=member.id)
        for c in build:
            if access_type.startswith("v"):
                if c.permissions_for(user).connect:
                    can.append(c.name)
                else:
                    cant.append(c.name)
            else:
                if c.permissions_for(user).view_channel:
                    can.append(c.name)
                else:
                    cant.append(c.name)

        if can:
            p1 = f"Has access ({len(can)}):\n" + "\n".join(
                f"+ {prefix}{x}" for x in sorted(can)
            )
        else:
            p1 = ""
        if cant:
            p2 = f"No access ({len(cant)}):\n" + "\n".join(
                f"- {prefix}{x}" for x in sorted(cant)
            )
        else:
            p2 = ""

        total = box(
            f"= Guild {singular_access_type.lower()} count: {len(build)}",
            lang="asciidoc",
        )
        pre_processed = total + box(f"{p1}\n\n{p2}", lang="diff")
        if await ctx.embed_requested():
            embed = discord.Embed(
                title=f"{singular_access_type} Access",
                description=pre_processed,
                color=await ctx.embed_colour(),
            )
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            return await ctx.send(embed=embed)
        await ctx.send(box(f"{p1}\n\n{p2}", lang="diff"))

    async def compare_access(self, ctx, member1: discord.Member, member2: discord.Member, access_type: str):
        if access_type == "text":
            build = ctx.guild.text_channels
            prefix = "#"
            access_type += " channels"
            singular_access_type = "Text Channel"
        elif access_type == "voice":
            build = ctx.guild.voice_channels
            prefix = "#"
            access_type += " channels"
            singular_access_type = "Voice Channel"
        else:
            build = ctx.guild.categories
            prefix = ""
            singular_access_type = "Category"
        can_member1 = []
        can_member2 = []
        cant_member1 = []
        cant_member2 = []
        user1 = await self.bot.get_or_fetch_member(guild=ctx.guild, member_id=member1.id)
        for c in build:
            if access_type.startswith("v"):
                if c.permissions_for(user1).connect:
                    can_member1.append(c.name)
                else:
                    cant_member1.append(c.name)
            else:
                if c.permissions_for(user1).view_channel:
                    can_member1.append(c.name)
                else:
                    cant_member1.append(c.name)
        user2 = await self.bot.get_or_fetch_member(guild=ctx.guild, member_id=member2.id)
        for c in build:
            if access_type.startswith("v"):
                if c.permissions_for(user2).connect:
                    can_member2.append(c.name)
                else:
                    cant_member2.append(c.name)
            else:
                if c.permissions_for(user2).view_channel:
                    can_member2.append(c.name)
                else:
                    cant_member2.append(c.name)
        total = box(
            f"= Guild {singular_access_type.lower()} count: {len(build)}",
            lang="asciidoc",
        )
        if can_member1:
            p1 = f"Has access ({len(can_member1)}):\n" + "+ " + ", ".join(
                f"{prefix}{x}" for x in sorted(can_member1)
            )
        else:
            p1 = ""
        if cant_member1:
            p2 = f"No access ({len(cant_member1)}):\n" + "- " + ", ".join(
                f"{prefix}{x}" for x in sorted(cant_member1)
            )
        else:
            p2 = ""
        if can_member2:
            p3 = f"Has access ({len(can_member2)}):\n" + "+ " + ", ".join(
                f"{prefix}{x}" for x in sorted(can_member2)
            )
        else:
            p3 = ""
        if cant_member2:
            p4 = f"No access ({len(cant_member2)}):\n" + "- " + ", ".join(
                f"{prefix}{x}" for x in sorted(cant_member2)
            )
        else:
            p4 = ""
        pre_processed = total + box(f"{p1}\n\n{p2}", lang="diff") + box(f"{p3}\n\n{p4}", lang="diff")
        if await ctx.embed_requested():
            embed = discord.Embed(
                title=f"{singular_access_type} Access",
                description=pre_processed,
                color=await ctx.embed_colour(),
            )
            return await ctx.send(embed=embed)
        await ctx.send(total + box(f"{p1}\n\n{p2}", lang="diff") + box(f"{p3}\n\n{p4}", lang="diff"))

    @commands.group()
    @commands.bot_has_permissions(embed_links=True)
    async def access(self, ctx):
        """
        Get member access to guild categories, text and voice channels.
        """

    @access.group()
    async def text(self, ctx):
        """
        Get text channel read access for a member, or compare viewership.
        """

    @access.group()
    async def voice(self, ctx):
        """
        Get text channel read access for a member, or compare viewership.
        """

    @access.group()
    async def category(self, ctx):
        """
        Get text channel read access for a member, or compare viewership.
        """

    @text.command(name="user")
    async def text_user(self, ctx, member: discord.Member):
        """
        Get text channel read access for a member.
        """
        await self.send_access(ctx=ctx, member=member, access_type="text")

    @voice.command(name="user")
    async def voice_user(self, ctx, member: discord.Member):
        """
        Get voice channel connect access for a member.
        """
        await self.send_access(ctx=ctx, member=member, access_type="voice")

    @category.command(name="user")
    async def category_user(self, ctx, member: discord.Member):
        """
        Get category read access for a member.
        """
        await self.send_access(ctx=ctx, member=member, access_type="categories")

    @text.command(name="compare")
    async def text_compare(self, ctx, member: discord.Member, member2: discord.Member):
        """
        Compare text channel access with another user.
        """
        await self.compare_access(ctx=ctx, member1=member2, member2=member2, access_type="text")

    @voice.command(name="compare")
    async def voice_compare(self, ctx, member1: discord.Member, member2: discord.Member):
        """
        Compare voice channel connect access with another user.
        """
        await self.compare_access(ctx=ctx, member1=member2, member2=member2, access_type="voice")

    @category.command(name="compare")
    async def category_compare(self, ctx, member1: discord.Member, member2: discord.Member):
        """
        Compare category access with another user.
        """
        await self.compare_access(ctx=ctx, member1=member2, member2=member2, access_type="categories")

def setup(bot):
    cog = Access(bot)
    global access
    access = bot.get_command("access")
    if access:
        bot.remove_command("access")
    bot.add_cog(cog)