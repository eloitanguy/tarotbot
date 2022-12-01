from discord.ext import commands


@commands.command()
async def ping(ctx):
    """
    pong!
    """
    await ctx.send('pong!')
