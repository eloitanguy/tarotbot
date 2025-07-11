# Discord Tarot Bot

Helps you keep track of Tarot score!
Seek help with `t/help`.

### Setup

This bot relies on the discord.py API:

	pip install -r requirements.txt

### Using screens

A "screen" is a remotely running terminal. Common uses of this bot is on a
server, which one accesses from their machine via ssh, running the bot within a
remote terminal. To ensure that the process continues remotely after having
closed the terminal on the personal machine, the easiest method is with screens
(within a "remote terminal", i.e. a terminal that is ssh'ed into the remote
machine). 

Remind: an ssh connection can be started with something like

	ssh machine@place.com

then entering your credentials. From the remote terminal, create a screen called
SCREEN-NAME with:

	screen -S SCREEN-NAME

You are now within the screen: run anything you want to stay running, for
instance this bot with:

	./run_bot.sh

To exit the screen without stopping the process, detach with CTRL+A,D (CTRL+A
then press D).

To join a screen that is running, use:

	screen -r SCREEN-NAME

### Starting a new season

A discord command `t/new_season IAMSURE` starts a new season automatically!

To start a new Tarot season, you can also simply copy the files `history.json`,
`players.json` and `players_backup.json` to some other location for safekeeping,
then re-start the bot (CTRL+C the script and run it again).