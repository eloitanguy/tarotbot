from discord.ext import commands  # type: ignore
import json


@commands.command()
async def add_player(ctx, player_name):
    """
    Rajoute le joueur [player_name] au leaderboard.
    """
    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    if player_name in PLAYERS:
        await ctx.send('{} is already listed!'.format(player_name))

    else:
        PLAYERS[player_name] = 0

        with open('players.json', 'w') as f:
            json.dump(PLAYERS, f, indent=4)

        await ctx.send('Successfully added {}.'.format(player_name))


@commands.command()
async def add_players(ctx, *, msg):
    """
    Rajoute les joueurs donnés (séparés par espaces) au leaderboard.
    """
    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)
    names_already_listed = []
    names_added = []

    for player_name in msg.split(' '):

        if player_name in PLAYERS:
            names_already_listed.append(player_name)

        else:
            PLAYERS[player_name] = 0
            names_added.append(player_name)

    with open('players.json', 'w') as f:
        json.dump(PLAYERS, f, indent=4)

    if names_already_listed:
        await ctx.send(f'Players {names_already_listed} are already listed!')
    await ctx.send(f'Successfully added {names_added}.')
