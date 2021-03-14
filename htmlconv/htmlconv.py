import io
import asyncio
import discord
import markdown

from redbot.core import commands
from redbot.core.utils.chat_formatting import box


class HTMLConv(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def html(self, ctx, *, text: str = None):
        if not text:
            if not ctx.message.attachments:
                return await ctx.send("You must upload a file.")
            file = ctx.message.attachments[0]
            if not file.filename.lower().endswith('.md'):
                return await ctx.send("Only supporting MD files at this time.")
            x = await file.read()
            output = markdown.markdown(x)
            if len(output) < 2000:
                await ctx.send(box(output, lang='html'))
            else:
                await ctx.send("What would you like to save your extension as?")

                def check(x):
                    return x.author == ctx.author and x.channel == ctx.channel

                try:
                    extension = await self.bot.wait_for("message", timeout=20, check=check)
                except asyncio.TimeoutError:
                    extension.content = "html"
                await ctx.send(file=discord.File(io.BytesIO(output.encode()), filename=f"converted.{extension.content}"))      
                              
        else:
            output = markdown.markdown(text)
            await ctx.send(box(output, lang='html'))
            await ctx.send(file=discord.File(io.BytesIO(output.encode()), filename="converted.json"))