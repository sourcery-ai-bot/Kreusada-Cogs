import re
import contextlib

import discord

from redbot.core import commands, Config
from redbot.core.commands import Context
from redbot.core.utils import AsyncIter
from redbot.core.utils.chat_formatting import box, bold

conf = {
    "toggle": True,
    "action": [0,0],
    "prevent": [],
    "log_channel": None,
}

pre_formatted_member_info = (
    "{}: {}\n"
    "{}: {}\n"
    "{}: {}\n"
    "{}: {}\n"
    "{}: {}\n"
)

class ServerShield(commands.Cog):
    """
    Run automatic actions when a user joins the guild.
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(
            self, 432948230492432, force_registration=True
        )
        self.config.register_guild(**conf)
        self.error = "ServerShield failed for user ({}). {}"

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        toggle = await self.config.guild(guild).toggle()
        action = await self.config.guild(guild).action()
        prevent = await self.config.guild(guild).prevent()
        log_channel_config = await self.config.guild(guild).log_channel()
        log_channel = self.bot.get_channel(log_channel_config)

        sg = {
            guild
            async for guild in AsyncIter(self.bot.guilds, steps=100)
            if user in guild.members
        }

        if re.match(".*\\W+.*", member.name):
            cancerous = "True"
        else:
            cancerous = "False"

        if not toggle:
            return

        if not action[0]:
            return

        if member.id in prevent:
            return

        try:

            if action[0] == 1:
                if action[1]:
                    with contextlib.suppress(discord.Forbidden):
                        await ctx.send(action[1])
                return await guild.kick(member, reason="User was kicked via ServerShield.")

            if action[0] == 2:
                if action[1]:
                    with contextlib.suppress(discord.Forbidden):
                        await ctx.send(action[1])
                return await guild.ban(member, reason="User was banned via ServerShield.")

            if action[0] == 3:

                if action[1]:
                    with contextlib.suppress(discord.Forbidden):
                        await ctx.send(action[1])

                if not log_channel_config:
                    return

                if not log_channel:
                    return await self.config.guild(ctx.guild).log_channel.clear()

                embed = discord.Embed(
                    title="A new user has joined!",
                    description = pre_formatted_member_info.format(
                        bold("User"),
                        self.bot.get_user(member),
                        bold("ID"),
                        member.id,
                        bold("Account Age"),
                        member.created_at.strftime("%d %b %Y %H:%M"),
                        bold("Joined this server"),
                        "Just now",
                        bold("Shared Guilds"),
                        f"Shared guilds: {sg}",
                        bold("Cancerous nickname"),
                        cancerous,
                        ),
                    color = await ctx.embed_colour()
                )

                if cancerous:
                    embed.set_footer(text="This users name has been flagged as potentially cancerous.")

                return await log_channel.send(embed=embed)

        except Exception as e:
            return log.info(self.error.format(member.id, e))

    @staticmethod
    def boxin(text):
        return '[{}]'.format(text)

    async def help_send(self, ctx, text):
        await ctx.send(text)
        return await ctx.send_help()

    @staticmethod
    def map_action_type(c):
        if c == 0:
            return 'None'
        elif c == 1:
            return 'Kick'
        elif c == 2:
            return 'Ban'
        elif c == 3:
            return 'Log'

    async def map_action_type_to_confirm(self, ctx, action_number):
        if action_number == 0:
            return await ctx.send("No actions will be taken on users who join.")
        elif action_number == 3:
            return await ctx.send("Users who join will now have their information logged to a channel.")
        elif action_number == 1:
            _type = 'kick'
        elif action_number == 2:
            _type = 'ban'
        return await ctx.send(f"Action type set to {_type}.")

    @commands.group()
    async def shield(self, ctx):
        """Commands with ServerShield."""

    @shield.command()
    async def toggle(self, ctx):
        """
        Toggle ServerShield.
        """
        toggled = await self.config.guild(ctx.guild).toggle()
        if toggled:
            _set = False
        else:
            _set = True
        await self.config.guild(ctx.guild).toggle.set(_set)
        if _set:
            verb = "enabled"
        else:
            verb = "disabled"
        await ctx.send(f"The server shield has been {verb}.")

    @shield.command()
    async def action(self, ctx, action_number):
        """
        Set the action number for users who join.

        `0`: No Action
        `1`: Kick
        `2`: Ban
        `3`: Log

        **Kick**
        Kicks the user from the guild and sends them an optional message,
        when they join the guild. This user will be able to join back.

        **Ban**
        Bans the user from the guild and sends them an optional message,
        when they join the guild. This user will not be able to join back
        unless unbanned.

        **Log**
        Logs the user's information in a dedicated channel when they join.
        No action will be taken on them.
        """
        if not isinstance(action_number, int):
            await self.help_send("Please provide a number from 0-3.")

        if not action_number in [*range(0,4)]:
            await self.help_send("Please provide a number from 0-3.")

        await self.config.guild(ctx.guild).action.set(action_number)
        await self.map_action_type_to_confirm(ctx, action_number)

    @shield.command()
    async def actionmessage(self, ctx, content: str = None):
        """
        Adds a subordinate message send feature to the main action.

        Your configured message will be sent to the user if they are affected
        by this cog's actions. If they cannot be DMed, it will fall silent.

        You can include `{user}` in your content, which will say the user's name.
        """
        action = await self.config.guild(ctx.guild).action()
        if not content:
            return await ctx.send("No content was provided, subordinate messages have been turned off.")
        action[1] = content
        await self.config.guild(ctx.guild).action.set(action)
        await ctx.send("Action message set.")

    @shield.group()
    async def immune(self, ctx):
        """
        Configure users to be immune to servershield.
        """

    @immune.command(usage="<user or users...>")
    async def add(self, ctx, *, u: discord.User):
        """
        Add certain users to have immunity.
        """
        prevent = await self.config.guild(ctx.guild).prevent()
        prevent.append([u.id for u in u])
        await self.config.guild(ctx.guild).prevent.set(prevent)
        if len(u) == 1:
            verb = "This"
            plural = "s"
        else:
            verb = "These"
            plural = "s"
        await ctx.send(
            f"{verb} user{s} have been prevented from servershield."
        )

    @immune.command(usage="<user>")
    async def remove(self, ctx, u: discord.User):
        """
        Remove a certain user from immunity.
        """
        prevent = await self.config.guild(ctx.guild).prevent()
        if u.id in prevent:
            prevent.remove(u.id)
            await self.config.guild(ctx.guild).prevent.set(prevent)
            return await ctx.send("This user has been removed successfully.")
        await ctx.send("This user was not in the blacklist.")

    @immune.command(name="list")
    async def _list(self, ctx):
        """
        Get the list of immune users.
        """
        prevent = await self.config.guild(ctx.guild).prevent()
        if not prevent:
            return await ctx.send("There are no immune users.")
        for u in prevent:
            get = self.bot.get_user(u)
            if not get:
                get = "Unknown"
            await ctx.send(box("\n".join(f'+ {u} {self.boxin(get)}'), lang='diff'))

    @immune.command()
    async def clear(self, ctx):
        """
        Clear the list of immune users.
        """
        await self.config.guild(ctx.guild).prevent.clear()
        await ctx.send("Immune list cleared.")