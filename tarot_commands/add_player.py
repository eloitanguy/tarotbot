from discord.ext import commands
import json


@commands.command()
async def add_player(ctx, player_name):
    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    if player_name in PLAYERS:
        await ctx.send('{} is already listed!'.format(player_name))

    else:
        PLAYERS[player_name] = 0

        with open('players.json', 'w') as f:
            json.dump(PLAYERS, f, indent=4)

        await ctx.send('Successfully added {}.'.format(player_name))
