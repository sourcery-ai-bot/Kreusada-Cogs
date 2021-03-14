import string
import discord
import collections

from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import bold

def shorten(value):
    if len(value) > 45:
        value = value[:45] + '...'
    return value

### Absolutely not working or ready yet, a very long WIP
### This code is not for public use as I make necessary changes over time.

class GlobalC(commands.Cog):
    """
    Create global commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 34284792384723498273, force_registration=True)
        self.config.register_global(commands={})

    async def remove_command(self, ctx, command: str):
        coms = await self.config.commands()
        if command in coms.keys():
            coms.pop(command)
            return True
        return False

    @commands.group()
    async def globalc(self, ctx):
        """
        Base command for global commands.
        """

    @globalc.command(usage="<command name> <response>", aliases=["create"])
    async def add(self, ctx, n: str, *, r: str):
        coms = await self.config.commands()
        if n in coms.keys():
            return await ctx.send(f"A command named {n} already exists as a global command.")
        elif n in self.bot.all_commands:
            return await ctx.send(f"A command named {n} already exists on {ctx.me.name}.")
        elif set(n).difference(string.printable):
            return await ctx.send("Your command cannot contain special characters.")
        elif not n.islower():
            return await ctx.send("Your command must be lower case.")
        elif len(n) > 10:
            return await ctx.send("The command name must be under 10 characters.")
        else:
            coms[n] = r
            await self.config.coms.set(coms)
            await ctx.send("Global command successfully added.")

    @globalc.command(name="list")
    async def _list(self, ctx):
        coms = await self.config.commands()
        embed = discord.Embed(
            title="Global Commands",
            description="\n".join(f'{bold(k)} {shorten(v)}' for k, v in sorted(coms.items())),
            color=await ctx.embed_colour(),
        )
        await ctx.send(embed=embed)

    @globalc.command(usage="<command name>", aliases=["del"])
    async def delete(self, ctx, n: str):
        conf = await self.remove_command(ctx, n)
        if not conf:
            return await ctx.send(f"No global command found matching `{n}`.")
        await ctx.tick("Global command successfully deleted.")

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        prefix_cache = await self.bot.command_prefix(self.bot, message)
        coms = await self.config.coms()

        for x in prefix_cache:
            for k, v in coms.items():
                if message.content.startswith(f'{x}{k}'):
                    return await message.channel.send(v)