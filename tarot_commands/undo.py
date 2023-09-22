import os
from discord.ext import commands
import json


@commands.command()
async def undo(ctx, s='no'):
    """
    Retire la dernière partie du leaderboard et de l'historique (IRREVERSIBLE).
    """
    if s != 'IAMSURE':
        await ctx.send('Are you sure though?')
        return

    if not os.path.isfile('players.json'):
        await ctx.send('No backup to load!')
        return

    with open('players_backup.json', 'r') as f:
        PLAYERS = json.load(f)

    with open('players.json', 'w') as f:
        json.dump(PLAYERS, f, indent=4)

    with open('history.json', 'r') as f:
        HISTORY = json.load(f)

    HISTORY = HISTORY[:-1]

    with open('history.json', 'w') as f:
        json.dump(HISTORY, f, indent=4)

    await ctx.send('Undo successful!')
