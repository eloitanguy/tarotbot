from discord.ext import commands
from table2ascii import table2ascii as t2a

POIGNEES = {
    3: {'Simple: 13 Atouts': 20, 'Double: 15 Atouts': 30, 'Triple: 18 Atouts': 40},
    4: {'Simple: 10 Atouts': 20, 'Double: 13 Atouts': 30, 'Triple: 15 Atouts': 40},
    5: {'Simple: 8 Atouts': 20, 'Double: 10 Atouts': 30, 'Triple: 13 Atouts': 40},
}
CONTRAT_PAR_BOUT = [56, 51, 41, 36]
PRIMES = {
    "Simple Poignée": 20,
    "Double Poignée": 30,
    "Triple Poignée": 40,
    "Petit au bout": 10,
    "Chelem annoncé": 400,
    "Chelem non annoncé": 200,
    "Chelem chuté": -200
}


@commands.command()
async def poignees(ctx, n_players=5):
    """
    Donne le nombre d'atouts pour les différentes poignées selon le nombre de joueurs "n_players".
    """
    if n_players not in [3, 4, 5]:
        await ctx.send('Le Tarot ne se joue pas à {}.'.format(n_players))
        return

    body = []
    for (k, v) in POIGNEES[n_players].items():
        body.append([k, v])

    output = t2a(
        header=["Poignée", "Prime"],
        body=body,
        first_col_heading=True
    )

    await ctx.send(f"```\n{output}\n```")


@commands.command()
async def contrats(ctx):
    body = []
    for i, v in enumerate(CONTRAT_PAR_BOUT):
        body.append([i, v])

    output = t2a(
        header=["Bouts", "Points"],
        body=body,
        first_col_heading=True
    )

    await ctx.send(f"```\n{output}\n```")


