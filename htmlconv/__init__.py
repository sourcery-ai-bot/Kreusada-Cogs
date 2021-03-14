from .htmlconv import HTMLConv

def setup(bot):
    bot.add_cog(HTMLConv(bot))