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
from datetime import datetime
from redbot.core.utils.chat_formatting import humanize_timedelta, humanize_number, box

log = logging.getLogger("red.kreusada.advanceduptime")


class AdvancedUptime(commands.Cog):
    """
    Show [botname]'s uptime, with extra stats.
    """

    __author__ = "Kreusada"
    __version__ = "1.3.0"

    def __init__(self, bot):
        self.bot = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad."""
        return f"{super().format_help_for_context(ctx)}\n\nAuthor: {self.__author__}\nVersion: {self.__version__}"

    def cog_unload(self):
        global _old_uptime
        if _old_uptime:
            try:
                self.bot.remove_command("uptime")
            except Exception as error:
                log.info(error)
                self.bot.add_command(_old_uptime)

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    @commands.command()
    async def uptime(self, ctx: commands.Context):
        """Shows [botname]'s uptime."""
        delta = datetime.utcnow() - self.bot.uptime
        uptime_str = humanize_timedelta(timedelta=delta) or (
            "Less than one second"
        )  # Thankyou Red-DiscordBot
        botname = ctx.bot.user.name
        users = humanize_number(len(self.bot.users))
        servers = humanize_number(len(self.bot.guilds))
        commands_available = humanize_number(len(set(self.bot.walk_commands())))
        app_info = await self.bot.application_info()
        owner = app_info.team.name if app_info.team else app_info.owner
        if await ctx.embed_requested():
            e = discord.Embed(
                title=f":green_circle:  {botname}'s Uptime",
                color=await ctx.embed_colour(),
                timestamp=ctx.message.created_at,
            )
            e.add_field(
                name=f"{botname} has been up for...", value=uptime_str, inline=False
            )
            e.add_field(name="Instance name:", value=ctx.bot.user, inline=True)
            e.add_field(name="Instance owner:", value=owner, inline=True)
            e.add_field(name="Current guild:", value=ctx.guild, inline=True)
            e.add_field(name="Number of guilds:", value=servers, inline=True)
            e.add_field(name="Unique users:", value=users, inline=True)
            e.add_field(
                name="Commands available:", value=commands_available, inline=True
            )
            e.set_thumbnail(url=ctx.bot.user.avatar_url)
            await ctx.send(embed=e)
        else:
            title = f"[{botname} has been up for {uptime_str}.]"
            msg = (
                f"Instance name: {ctx.bot.user}\n"
                f"Instance owner: {owner}\n"
                f"Current guild: {ctx.guild}\n"
                f"Number of guilds: {servers}\n"
                f"Unique users: {users}\n"
                f"Commands available: {commands_available}"
            )
            await ctx.send(box(title, lang="yaml"))
            await ctx.send(box(msg, lang="yaml"))


def setup(bot):
    au = AdvancedUptime(bot)
    global _old_uptime
    _old_uptime = bot.get_command("uptime")
    if _old_uptime:
        bot.remove_command(_old_uptime.name)
    bot.add_cog(au)
