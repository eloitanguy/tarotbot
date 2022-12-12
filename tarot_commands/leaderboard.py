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

    with open('history.json', 'r') as f:
        HISTORY = json.load(f)

    sorted_players = dict(sorted(PLAYERS.items(), key=lambda item: item[1])[::-1])
    number_games_played = {p: 0 for p in sorted_players.keys()}

    for player in sorted_players.keys():
        for hist in HISTORY:
            if player in hist['scores']:
                number_games_played[player] += 1

    body = []
    for i, (k, v) in enumerate(sorted_players.items()):
        body.append([i+1, k, int(v), int(number_games_played[k]), int(v / number_games_played[k])])
    output = t2a(
        header=["Rank", "Name", "Points", "Games", "Ratio"],
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
async def undo_leaderboard(ctx, s='no'):
    """
    Retire la dernière partie du leaderboard (IRREVERSIBLE).
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

    await ctx.send('Undo successful!')
