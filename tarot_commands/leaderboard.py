from discord.ext import commands
import json
from table2ascii import table2ascii as t2a
import os


@commands.command()
async def leaderboard(ctx):
    """
    Montre le leaderboard.
    """
    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    sorted_players = dict(sorted(PLAYERS.items(), key=lambda item: item[1])[::-1])
    body = []
    for i, (k, v) in enumerate(sorted_players.items()):
        body.append([i+1, k, int(v)])
    output = t2a(
        header=["Rank", "Name", "Points"],
        body=body,
        first_col_heading=True
    )

    await ctx.send(f"```\n{output}\n```")


def update_leaderboard(scores):
    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    with open('players_backup.json', 'w') as f:
        json.dump(PLAYERS, f, indent=4)

    for k, v in scores.items():
        PLAYERS[k] += v

    with open('players.json', 'w') as f:
        json.dump(PLAYERS, f, indent=4)


@commands.command()
async def undo_leaderboard(ctx):
    """
    Retire la dernière partie du leaderboard (IRREVERSIBLE).
    """
    if not os.path.isfile('players.json'):
        await ctx.send('No backup to load!')
        return

    with open('players_backup.json', 'r') as f:
        PLAYERS = json.load(f)

    with open('players.json', 'w') as f:
        json.dump(PLAYERS, f, indent=4)

    await ctx.send('Undo successful!')
