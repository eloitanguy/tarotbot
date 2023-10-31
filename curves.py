import matplotlib.pyplot as plt
import numpy as np
import json
from matplotlib import colormaps
from discord.ext import commands
import discord


def render_curves():
    with open('history.json', 'r') as f:
        HISTORY = json.load(f)

    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    n_players = len(PLAYERS)
    n_games = len(HISTORY)
    sorted_players = dict(sorted(PLAYERS.items(), key=lambda item: item[1])[::-1])
    player_to_idx = {p: i for (i, p) in enumerate(sorted_players.keys())}

    scores = np.zeros((n_games + 1, n_players))  # placeholder first scores at 0
    dates = []

    for t, hist in enumerate(HISTORY):
        dates.append(hist['time'])
        delta = np.zeros(n_players)
        delta[[player_to_idx[p] for p in hist['scores'].keys()]] = list(hist['scores'].values())
        scores[t + 1] = scores[t] + delta

    cm = colormaps['gist_ncar'].resampled(3 * n_players)
    plt.figure(figsize=(21, 12))
    for p, i in player_to_idx.items():
        plt.plot(scores[:, i], label=p, color=cm(1 - (i + 1)/(n_players + 1)))

    plt.legend(loc='center left')
    plt.title('Le jeu tourne')
    plt.xlabel('temps')
    plt.ylabel('score')
    plt.savefig("curves.png", format="png", bbox_inches="tight")


@commands.command()
async def curves(ctx):
    """
    Renders and shows the entire play history as curves
    """
    render_curves()

    with open('curves.png', 'rb') as f:
        picture = discord.File(f)

    await ctx.send(file=picture)
