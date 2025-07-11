from discord.ext import commands  # type: ignore
import os
from datetime import datetime
import shutil
import json


@commands.command()
async def new_season(ctx, s='no'):
    """
    Commence une nouvelle saison (IRREVERSIBLE SANS ACCÈS AU SERVEUR)
    """
    now = datetime.today().strftime('%Y-%m-%d')
    folder = now + '/'
    if s != 'IAMSURE':
        await ctx.send('Are you sure though?')
        return

    if os.path.isdir(folder):
        ctx.send('Folder already exists, aborted!')
        return

    os.makedirs(folder)
    shutil.move('players.json', folder + 'players.json')
    shutil.move('history.json', folder + 'history.json')
    shutil.move('players_backup.json', folder + 'players_backup.json')

    if not os.path.isfile('players.json'):
        with open('players.json', 'w') as f:
            json.dump({}, f, indent=4)
        print('No players.json file, writing a blank one.')

    if not os.path.isfile('history.json'):
        with open('history.json', 'w') as f:
            json.dump([], f, indent=4)
        print('No history.json file, writing a blank one.')

    await ctx.send('New season started!')
