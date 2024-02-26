import curves
import json
import argparse
import os
from tarot_commands import leaderboard 


def fuse_history_and_players(folder_list):
	history, players = [], {}
	
	for folder in folder_list:

		# concatenante histories, assuming they are given chronologically
		with open(os.path.join(folder, 'history.json'), 'r') as f:
			history.extend(json.load(f))

		# final score of each player is the sum of their season scores
		with open(os.path.join(folder, 'players.json'), 'r') as f:
			players_dict = json.load(f)
			for (player, score) in players_dict.items():
				if player in players:
					players[player] += score
				else:
					players[player] = score

	with open('players.json', 'w') as f:
		json.dump(players, f, indent=4)
	with open('history.json', 'w') as f:
		json.dump(history, f, indent=4)


all_folders = os.listdir()
season_folders = sorted([s for s in all_folders if 'saison' in s])
fuse_history_and_players(season_folders)
curves.render_curves()
print(leaderboard.leaderboard_text())
print('\n\n\n\n')
print(leaderboard.leaderboard2_text())
