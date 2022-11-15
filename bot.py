import discord
from discord.ext import commands
import json
from tarot_commands.ping import ping
from tarot_commands.add_player import add_player
from tarot_commands.leaderboard import leaderboard, undo_leaderboard
from tarot_commands.game import game
from tarot_commands.rules import poignees, contrats
from tarot_commands.history import undo_history
from tarot_commands.h import h
import os

with open('config.json', 'r') as f:
    config = json.load(f)

if not os.path.isfile('players.json'):
    with open('players.json', 'w') as f:
        json.dump({}, f, indent=4)
    print('No players.json file, writing a blank one.')

if not os.path.isfile('history.json'):
    with open('history.json', 'w') as f:
        json.dump([], f, indent=4)
    print('No history.json file, writing a blank one.')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='t/')

bot.add_command(ping)
bot.add_command(add_player)
bot.add_command(leaderboard)
bot.add_command(undo_leaderboard)
bot.add_command(undo_history)
bot.add_command(game)
bot.add_command(poignees)
bot.add_command(contrats)
bot.add_command(h)
bot.run(config['token'])
