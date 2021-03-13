import discord

from redbot.core import commands
from redbot.core.utils.chat_formatting import box

class Access(commands.Cog):
    """
    Get member access to guild categories, text and voice channels.
    """

    def __init__(self, bot):
        self.bot = bot

    async def send_access(self, ctx, member: discord.Member, access_type: str):
        if access_type == 'text':
            build = ctx.guild.text_channels
            prefix = '#'
            access_type += ' channels'
            singular_access_type = "Text Channel"
        elif access_type == 'voice':
            build = ctx.guild.voice_channels
            prefix = '#'
            access_type += ' channels'
            singular_access_type = "Voice Channel"
        else:
            build = ctx.guild.categories
            prefix = ''
            singular_access_type = "Category"

        can = []
        cant = []
        user = await self.bot.get_or_fetch_member(guild=ctx.guild, member_id=member.id)
        for c in build:
            if access_type.startswith('v'):
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
            p1 = f"Has access ({len(can)}):\n" + "\n".join(f'+ {prefix}{x}' for x in sorted(can))
        else:
            p1 = ''
        if cant:
            p2 = f"No access ({len(cant)}):\n" + "\n".join(f'- {prefix}{x}' for x in sorted(cant))
        else:
            p2 = ''

        total = box(f"= Guild {singular_access_type.lower()} count: {len(build)}", lang='asciidoc')
        pre_processed = total + box(f'{p1}\n\n{p2}', lang='diff')
        if await ctx.embed_requested():
            embed = discord.Embed(
                title=f"{singular_access_type} Access",
                description=pre_processed,
                color=await ctx.embed_colour(),
            )
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            return await ctx.send(embed=embed)
        await ctx.send(box(f'{p1}\n\n{p2}', lang='diff'))

    @commands.group()
    @commands.bot_has_permissions(embed_links=True)
    async def access(self, ctx):
        """
        Get member access to guild categories, text and voice channels.
        """

    @access.command()
    async def text(self, ctx, member: discord.Member):
        """
        Get text channel read access for a member.
        """
        await self.send_access(ctx=ctx, member=member, access_type='text')

    @access.command()
    async def voice(self, ctx, member: discord.Member):
        """
        Get voice channel connect access for a member.
        """
        await self.send_access(ctx=ctx, member=member, access_type='voice')

    @access.command()
    async def category(self, ctx, member: discord.Member):
        """
        Get category read access for a member.
        """
        await self.send_access(ctx=ctx, member=member, access_type='categories')