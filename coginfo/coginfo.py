import json
import pathlib
import contextlib

from redbot.core import commands

# Still a very big WIP

class CogInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def coginfo(self, ctx, cog: str):
        await ctx.trigger_typing()
        commands_cog = self.bot.get_cog(cog)
        try:
            cog = __import__(cog.lower())
        except ModuleNotFoundError:
            return await ctx.send(f"You do not have a cog named {cog}.")
        embed = discord.Embed()
        with open(pathlib.Path(cog.__file__).parent / 'info.json') as fp:
            try:
                author_key = json.load(fp)["author"]
                if isinstance(author_key, list):
                    if len(author_key) > 1:
                        s = 's'
                    else:
                        s = ''
                    embed.add_field(name=f"Author{s}", value=", ".join(x for x in author_key))
            except KeyError:
                if hasattr(commands_cog, '__author__'):
                    if isinstance(commands_cog.__author__, list):
                        author_key = ", ".join(x for x in commands_cog.__author__)
                        if len(commands_cog.__author__) > 1:
                            s = 's'
                        else:
                            s = ''
                    else:
                        author_key = commands_cog.__author__
                        s = ''
                    embed.add_field(name=f"Author{s}", value=author_key)
                else:
                    embed.add_field(name="Author(s)", value="Unknown")
            try:
                embed.add_field(name="Description", value=json.load(fp)["description"])
            except KeyError:
                if commands_cog.__cog_description__:
                    embed.add_field(name="Description", value=commands_cog.__cog_description__)
                else:
                    embed.add_field(name="Description", value="Not provided.")
            with contextlib.suppress(KeyError):
                embed.add_field(name="End User Data Statement", value=json.load(fp)["end_user_data_statement"])