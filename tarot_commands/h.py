from discord.ext import commands


@commands.command()
async def h(ctx):
    helps = [
        't/ping: pings the bot to check connection',
        't/add_player: adds player to the list',
        't/leaderboard: shows leaderboard',
        't/undo_leaderboard: undoes the last score update on the leaderboard file',
        't/undo_history: undoes the last score update on the history file',
        't/game [n]: interface for adding a game where the Preneur won [n] points',
        't/poignees [n]: shows the number of Atout required for a Poignée with [n] players',
        't/contrats: shows the number of points to win in order to match your contract',
    ]
    msg = 'List of commands:'
    for s in helps:
        msg = msg + '\t\n' + s
    await ctx.send(msg)
