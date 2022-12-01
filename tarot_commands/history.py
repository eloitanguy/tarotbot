from discord.ext import commands
import json
from datetime import datetime


def update_history(scores):
    with open('history.json', 'r') as f:
        HISTORY = json.load(f)

    next_entry = {
        'time': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        'scores': scores
    }

    HISTORY.append(next_entry)

    with open('history.json', 'w') as f:
        json.dump(HISTORY, f, indent=4)


@commands.command()
async def undo_history(ctx, s='no'):
    """
    Retire la dernière partie de l'historique (IRREVERSIBLE).
    """
    if s != 'IAMSURE':
        await ctx.send('Are you sure though?')
        return

    with open('history.json', 'r') as f:
        HISTORY = json.load(f)

    HISTORY = HISTORY[:-1]

    with open('history.json', 'w') as f:
        json.dump(HISTORY, f, indent=4)

    await ctx.send('Undo successful!')
