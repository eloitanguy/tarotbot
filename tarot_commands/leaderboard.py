from discord.ext import commands
import json
from table2ascii import table2ascii as t2a


def leaderboard_text():
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
    return f"```\n{output}\n```"


def leaderboard2_text():
    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    with open('history.json', 'r') as f:
        HISTORY = json.load(f)

    player_ratios = {p: 0 for p in PLAYERS.keys()}
    player_WL = {p: {'W': 0, 'L': 0} for p in PLAYERS.keys()}

    for player, v in PLAYERS.items():
        for hist in HISTORY:
            if player in hist['scores']:
                if hist['scores'][player] >= 0:  # won the game
                    player_WL[player]['W'] += 1
                else:  # lost the game
                    player_WL[player]['L'] += 1

        player_ratios[player] = int(v / (player_WL[player]['W'] + player_WL[player]['L'])) \
            if player_WL[player]['W'] + player_WL[player]['L'] > 0 else 0

    sorted_players_ratios = dict(sorted(player_ratios.items(), key=lambda item: item[1])[::-1])
    body = []
    for i, (player, ratio) in enumerate(sorted_players_ratios.items()):
        body.append([i+1, player, ratio,
                     str(int(player_WL[player]['W'])) + '/' + str(int(player_WL[player]['L']))])
    output = t2a(
        header=["Rank", "Name", "Points/Games", "W/L"],
        body=body,
        first_col_heading=True
    )
    return f"```\n{output}\n```"


@commands.command()
async def leaderboard(ctx):
    """
    Montre le leaderboard.
    """
    text = leaderboard_text()
    await ctx.send(text)


@commands.command()
async def leaderboard2(ctx):
    """
    Montre le leaderboard à ratios.
    """
    text = leaderboard2_text()
    await ctx.send(text)


def update_leaderboard(scores):
    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    with open('players_backup.json', 'w') as f:
        json.dump(PLAYERS, f, indent=4)

    for k, v in scores.items():
        PLAYERS[k] += v

    with open('players.json', 'w') as f:
        json.dump(PLAYERS, f, indent=4)
