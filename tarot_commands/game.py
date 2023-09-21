import discord
from discord.ext import commands
import json
from tarot_commands.rules import CONTRAT_PAR_BOUT, PRIMES
from table2ascii import table2ascii as t2a
from tarot_commands.leaderboard import update_leaderboard
from tarot_commands.history import update_history


class ParseError(Exception):
    pass


GLOBAL_ENCHERE = None
GLOBAL_GAME_PLAYERS = {'Preneur': [], 'Partenaire': [], 'Défenseurs': []}
GLOBAL_BOUTS = None
GLOBAL_PRIMES_ATTAQUE = []
GLOBAL_PRIMES_DEFENSE = []
GLOBAL_POINTS_ATTAQUE = None
GLOBAL_DESCENDANTE_PLAYERS = {'#1': None, '#2': None, '#3': None, '#4': None, '#5': None}
GLOBAL_DESCENDANTE_POINTS = []
GLOBAL_MISERES = []


def reset_cache():
    global GLOBAL_ENCHERE, GLOBAL_GAME_PLAYERS, GLOBAL_BOUTS, GLOBAL_PRIMES_ATTAQUE, GLOBAL_PRIMES_DEFENSE, \
        GLOBAL_POINTS_ATTAQUE, GLOBAL_DESCENDANTE_PLAYERS, GLOBAL_MISERES, GLOBAL_DESCENDANTE_POINTS
    GLOBAL_ENCHERE = None
    GLOBAL_GAME_PLAYERS = {'Preneur': [], 'Partenaire': [], 'Défenseurs': []}
    GLOBAL_BOUTS = None
    GLOBAL_PRIMES_ATTAQUE = []
    GLOBAL_PRIMES_DEFENSE = []
    GLOBAL_POINTS_ATTAQUE = None
    GLOBAL_DESCENDANTE_PLAYERS = {'#1': None, '#2': None, '#3': None, '#4': None, '#5': None}
    GLOBAL_DESCENDANTE_POINTS = []
    GLOBAL_MISERES = []


class SelectEnchere(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Petite", emoji="🤏"),
            discord.SelectOption(label="Garde", emoji="✋"),
            discord.SelectOption(label="GardeSans", emoji="✊"),
            discord.SelectOption(label="GardeContre", emoji="💪"),
        ]
        super().__init__(placeholder="👋 Enchère:", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global GLOBAL_ENCHERE
        if self.values[0] == "Petite":
            GLOBAL_ENCHERE = 1
            await interaction.response.send_message(content=f"Choix: {self.values[0]}!", ephemeral=True)
        elif self.values[0] == "Garde":
            GLOBAL_ENCHERE = 2
            await interaction.response.send_message(content=f"Choix: {self.values[0]}!", ephemeral=True)
        elif self.values[0] == "GardeSans":
            GLOBAL_ENCHERE = 4
            await interaction.response.send_message(content=f"Choix: {self.values[0]}!", ephemeral=True)
        elif self.values[0] == "GardeContre":
            GLOBAL_ENCHERE = 6
            await interaction.response.send_message(content=f"Choix: {self.values[0]}!", ephemeral=True)


class SelectBouts(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="0"),
            discord.SelectOption(label="1"),
            discord.SelectOption(label="2"),
            discord.SelectOption(label="3")
        ]
        super().__init__(placeholder="🧶 Bouts:", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global GLOBAL_BOUTS
        GLOBAL_BOUTS = int(self.values[0])
        await interaction.response.send_message(content=f"Choix: {self.values[0]}!", ephemeral=True)


class SelectPlayers(discord.ui.Select):
    def __init__(self, role, emote):
        with open('players.json', 'r') as f:
            PLAYERS = json.load(f)

        options = [
            discord.SelectOption(label=player_name) for player_name in PLAYERS.keys()
        ]

        self.role = role
        if self.role == 'Misère':
            max_values = 5
        elif self.role == 'Défenseurs':
            max_values = 4
        else:  # Descendante #1->#5, Preneur, Partenaire, Misères
            max_values = 1

        if self.role == 'Preneur':
            min_values = 1
        elif self.role in ['Partenaire']:
            min_values = 0
        elif self.role == 'Défenseurs':
            min_values = 2
        elif self.role in ['#1', '#2', '#3', '#4', '#5']:  # Descendante: we give the right amount of SelectMenus
            min_values = 1  # so all should be answered.
        else:
            min_values = 0  # should never happen

        super().__init__(placeholder="{} {}:".format(emote, self.role),
                         max_values=max_values, min_values=min_values, options=options)

    async def callback(self, interaction: discord.Interaction):
        global GLOBAL_DESCENDANTE_PLAYERS, GLOBAL_GAME_PLAYERS, GLOBAL_MISERES
        if self.values:
            if '#' in self.role:  # Descendante
                GLOBAL_DESCENDANTE_PLAYERS[self.role] = self.values[0]
                await interaction.response.send_message(content=f"Choix: {str(self.values[0])}!", ephemeral=True)
            elif self.role != 'Misères':
                GLOBAL_GAME_PLAYERS[self.role] = self.values
                await interaction.response.send_message(content=f"Choix: {str(self.values)}!", ephemeral=True)
            else:  # Misère
                GLOBAL_MISERES = self.values
                await interaction.response.send_message(content=f"Choix: {str(self.values)}!", ephemeral=True)


class SelectPrimes(discord.ui.Select):
    def __init__(self, attaque=True):
        self.attaque = attaque
        self.defense = not attaque
        emote = '⚔' if self.attaque else '🛡️'
        options = [
            discord.SelectOption(label="Simple Poignée", emoji="✊"),
            discord.SelectOption(label="Double Poignée", emoji="✊"),
            discord.SelectOption(label="Triple Poignée", emoji="✊"),
            discord.SelectOption(label="Petit au bout", emoji="☝️"),
            discord.SelectOption(label="Chelem annoncé", emoji="🤑"),
            discord.SelectOption(label="Chelem non annoncé", emoji="🤭"),
            discord.SelectOption(label="Chelem chuté", emoji="😭")
        ]
        if self.defense:
            del options[-1]
            del options[-2]
        super().__init__(placeholder="{} Primes {}:".format(emote, 'Attaque' if self.attaque else 'Défense'),
                         max_values=3, min_values=0, options=options)

    async def callback(self, interaction: discord.Interaction):
        global GLOBAL_PRIMES_ATTAQUE, GLOBAL_PRIMES_DEFENSE
        if self.attaque:
            GLOBAL_PRIMES_ATTAQUE = self.values
            await interaction.response.send_message(content=f"Choix: {str(self.values)}!", ephemeral=True)
        else:
            GLOBAL_PRIMES_DEFENSE = self.values
            await interaction.response.send_message(content=f"Choix: {str(self.values)}!", ephemeral=True)


class SelectViewGame(discord.ui.View):
    def __init__(self, *, timeout=300):
        super().__init__(timeout=timeout)
        self.add_item(SelectPlayers('Preneur', '⚔️'))
        self.add_item(SelectPlayers('Partenaire', '🗡️️'))
        self.add_item(SelectPlayers('Défenseurs', '🛡️'))
        self.add_item(SelectEnchere())
        self.add_item(SelectBouts())


class SelectViewDescendante(discord.ui.View):
    def __init__(self, *, timeout=300):
        super().__init__(timeout=timeout)
        global GLOBAL_DESCENDANTE_POINTS
        n_players = len(GLOBAL_DESCENDANTE_POINTS)
        for i in range(n_players):
            self.add_item(SelectPlayers('#{}'.format(i + 1), '☂️️'))


class SelectViewPrimes(discord.ui.View):
    def __init__(self, *, timeout=300):
        super().__init__(timeout=timeout)
        self.add_item(SelectPrimes(attaque=True))
        self.add_item(SelectPrimes(attaque=False))
        self.add_item(SelectPlayers('Misères', '😇️'))


class GameCalculButton(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Calcul", style=discord.ButtonStyle.blurple)
    async def calcul(self, interaction: discord.Interaction, button: discord.ui.Button):
        global GLOBAL_ENCHERE, GLOBAL_GAME_PLAYERS, GLOBAL_BOUTS, GLOBAL_PRIMES_ATTAQUE, GLOBAL_PRIMES_DEFENSE, \
            GLOBAL_MISERES

        if not GLOBAL_GAME_PLAYERS['Preneur']:
            await interaction.response.send_message('Preneur?')
            return

        if len(GLOBAL_GAME_PLAYERS['Défenseurs']) < 2:
            await interaction.response.send_message('Pas assez de défenseurs.')
            return

        if GLOBAL_GAME_PLAYERS['Preneur'][0] in GLOBAL_GAME_PLAYERS['Défenseurs']:
            await interaction.response.send_message('Le Preneur défend aussi?')
            return

        if GLOBAL_GAME_PLAYERS['Partenaire'] and \
                GLOBAL_GAME_PLAYERS['Partenaire'][0] in GLOBAL_GAME_PLAYERS['Défenseurs']:
            await interaction.response.send_message('Le Partenaire défend aussi?.')
            return

        if GLOBAL_GAME_PLAYERS['Partenaire'] and GLOBAL_GAME_PLAYERS['Partenaire'][0] in GLOBAL_GAME_PLAYERS['Preneur']:
            await interaction.response.send_message('Le Partenaire est Preneur?.')
            return

        n_players = len(GLOBAL_GAME_PLAYERS['Preneur'] + GLOBAL_GAME_PLAYERS['Partenaire'] +
                        GLOBAL_GAME_PLAYERS['Défenseurs'])

        if n_players not in [3, 4, 5]:
            await interaction.response.send_message('Le Tarot ne se joue pas à {}.'.format(n_players))
            return

        if GLOBAL_GAME_PLAYERS['Partenaire'] and n_players != 5:
            await interaction.response.send_message('Pas de partenaire à moins de 5.')
            return

        n_chelem_tot = 0
        for x in [GLOBAL_PRIMES_ATTAQUE, GLOBAL_PRIMES_DEFENSE]:
            if x:
                n_poignees = 0
                n_chelem = 0
                for p in x:
                    if 'Poignée' in p:
                        n_poignees += 1
                    if 'Chelem' in p:
                        n_chelem += 1
                if n_poignees > 1:
                    await interaction.response.send_message("Plus d'un type de Poignée.")
                    return
                if n_chelem > 1:
                    await interaction.response.send_message("Plus d'un type de Chelem.")
                    return
                if n_chelem == 1:
                    n_chelem_tot += 1

        if n_chelem_tot > 1:
            await interaction.response.send_message("Un chelem par équipe.")
            return

        if GLOBAL_PRIMES_ATTAQUE and GLOBAL_PRIMES_DEFENSE:
            if "Petit au bout" in GLOBAL_PRIMES_ATTAQUE and "Petit au bout" in GLOBAL_PRIMES_DEFENSE:
                await interaction.response.send_message('Un seul Petit.')
                return

        if GLOBAL_BOUTS is None:
            await interaction.response.send_message('Pas de réponse pour les bouts.')
            return

        if not GLOBAL_ENCHERE:
            await interaction.response.send_message('Pas de réponse pour les enchères.')
            return

        for player in GLOBAL_MISERES:
            if not (player in GLOBAL_GAME_PLAYERS['Preneur'] or player in GLOBAL_GAME_PLAYERS['Partenaire']
                    or player in GLOBAL_GAME_PLAYERS['Défenseurs']):
                await interaction.response.send_message(
                    'Le joueur {} est listé dans les misères mais ne joue pas.'.format(player))
                return

        scores = calcul_scores()
        update_leaderboard(scores)
        update_history(scores)
        button.disabled = True  # After updating the score!
        reset_cache()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"```\n{get_score_table_string(scores)}\n```")


class DescendanteCalculButton(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(SelectPlayers('Misères', '😇️'))

    @discord.ui.button(label="Calcul", style=discord.ButtonStyle.blurple)
    async def calcul(self, interaction: discord.Interaction, button: discord.ui.Button):
        global GLOBAL_DESCENDANTE_PLAYERS, GLOBAL_MISERES, GLOBAL_DESCENDANTE_POINTS

        n_players = sum([bool(v) for v in GLOBAL_DESCENDANTE_PLAYERS.values()])

        if n_players != len(GLOBAL_DESCENDANTE_POINTS):
            await interaction.response.send_message('Merci de remplir toutes les entrées.')
            return

        test_unique_dict = {player: 0 for player in GLOBAL_DESCENDANTE_PLAYERS.values() if player}
        if len(test_unique_dict) != n_players:
            await interaction.response.send_message('Liste de joueurs non injective.')
            return

        for player in GLOBAL_MISERES:
            if player not in [p for p in GLOBAL_DESCENDANTE_PLAYERS if p]:
                await interaction.response.send_message(
                    'Le joueur {} est listé dans les misères mais ne joue pas.'.format(player))
                return

        scores = calcul_score_descendante(GLOBAL_DESCENDANTE_PLAYERS, GLOBAL_DESCENDANTE_POINTS)
        scores = affecte_miseres(scores)
        update_leaderboard(scores)
        update_history(scores)
        button.disabled = True  # After updating the score!
        reset_cache()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"```\n{get_score_table_string(scores)}\n```")


@commands.command()
async def game(ctx, value=-999):
    """
    Entre une nouvelle partie avec [value] points faits par l'attaque: lance des menus à remplir pour les détails.

    Attention, le nombre de points à rentrer doit être ENTIER!! Sinon la commande renverra une erreur.

    Par exemple, si l'attaque ne fait que deux plis avec que des cartes valant 0.5 points, l'attaque a marqué 5 points
    donc il faut rentrer "t/game 5".
    """
    reset_cache()
    v = int(value)

    if v == -999:
        await ctx.send('Retente avec une valeur! par exemple t/game 10')
        return

    if v < 0 or v > 91:
        await ctx.send("{} n'est pas un nombre de points valide".format(v))
        return

    global GLOBAL_POINTS_ATTAQUE
    GLOBAL_POINTS_ATTAQUE = v
    await ctx.send("Alors? 👀", view=SelectViewGame())
    await ctx.send("Des primes?", view=SelectViewPrimes())
    await ctx.send("", view=GameCalculButton())


def calcul_scores():
    global GLOBAL_ENCHERE, GLOBAL_GAME_PLAYERS, GLOBAL_BOUTS, GLOBAL_PRIMES_ATTAQUE, GLOBAL_PRIMES_DEFENSE, \
        GLOBAL_POINTS_ATTAQUE

    # we consider all values to be legal (checked in the "calcul" button)
    delta = GLOBAL_POINTS_ATTAQUE - CONTRAT_PAR_BOUT[GLOBAL_BOUTS]
    s = delta / abs(delta) if delta != 0 else 1
    primes_attaque = {k: (v if k in GLOBAL_PRIMES_ATTAQUE else 0) for (k, v) in PRIMES.items()}
    primes_defense = {k: (v if k in GLOBAL_PRIMES_DEFENSE else 0) for (k, v) in PRIMES.items()}
    score = GLOBAL_ENCHERE * (abs(delta) + 25 + s * (primes_attaque['Petit au bout'] - primes_defense['Petit au bout']))
    score += primes_attaque['Simple Poignée'] + primes_attaque['Double Poignée'] + primes_attaque['Triple Poignée'] \
             + primes_defense['Simple Poignée'] + primes_defense['Double Poignée'] + primes_defense['Triple Poignée']

    score += primes_attaque["Chelem annoncé"] + primes_attaque["Chelem non annoncé"] + primes_attaque["Chelem chuté"]

    score_attaquant = s * score * len(GLOBAL_GAME_PLAYERS['Défenseurs'])
    score_attaquant -= len(GLOBAL_GAME_PLAYERS['Défenseurs']) * primes_defense["Chelem non annoncé"]
    score_defense = -s * score + primes_defense["Chelem non annoncé"]
    scores = {}

    if GLOBAL_GAME_PLAYERS['Partenaire']:
        scores[GLOBAL_GAME_PLAYERS['Partenaire'][0]] = score_attaquant // 3
        scores[GLOBAL_GAME_PLAYERS['Preneur'][0]] = (2 * score_attaquant) // 3
    else:
        scores[GLOBAL_GAME_PLAYERS['Preneur'][0]] = score_attaquant

    for def_name in GLOBAL_GAME_PLAYERS['Défenseurs']:
        scores[def_name] = score_defense

    scores = affecte_miseres(scores)

    return scores


def calcul_score_descendante(descendante_players, descendante_points):
    players = [p for p in descendante_players.values() if p]
    n_players = len(players)
    scores = {p: 0 for p in players}
    for idx, player in enumerate(players):
        player_points = descendante_points[idx]
        scores[player] -= n_players * player_points  # will receive +player_points in the next loop
        for player2 in players:  # this includes the current player!
            scores[player2] += player_points
    return scores


@commands.command()
async def descendante(ctx, *points):
    """
    Entre une nouvelle partie en descendante.

    Il faut donner les scores des joueurs, puis une interface demandera les noms des joueurs, et affectera les scores.

    Par exemple "t/descendante 20 20 51" fera remplir les noms de 3 joueurs dont les points respectifs
    sont 20, 20 et 51.
    """
    reset_cache()
    global GLOBAL_DESCENDANTE_POINTS
    points = [int(point) for point in points]
    GLOBAL_DESCENDANTE_POINTS = points
    n_players = len(points)

    if n_players not in [3, 4, 5]:
        await ctx.send('Le Tarot ne se joue pas à {}.'.format(n_players))
        return

    for point in points:
        if point < 0 or point > 91:
            await ctx.send('Points invalides: {}.'.format(point))
            return

    await ctx.send("Somme des points = {}.\nJoueurs respectifs:".format(sum(points)), view=SelectViewDescendante())
    await ctx.send("", view=DescendanteCalculButton())


def get_score_table_string(scores):
    body = []
    for (k, v) in scores.items():
        body.append([k, '{}{}'.format('+' if v >= 0 else '', int(v))])

    output = t2a(
        header=["Nom", "Score"],
        body=body,
        first_col_heading=True
    )
    return output


def affecte_miseres(scores):
    global GLOBAL_GAME_PLAYERS, GLOBAL_MISERES
    all_players = GLOBAL_GAME_PLAYERS['Preneur'] + GLOBAL_GAME_PLAYERS['Partenaire'] + GLOBAL_GAME_PLAYERS['Défenseurs']
    n_players = len(all_players)

    for misere_player in GLOBAL_MISERES:
        # misere_player will lose 10 in the following loop, so all other players give misere_player 10
        scores[misere_player] += n_players * 10
        for player in all_players:
            scores[player] -= 10
    return scores


def autoparse(msg):
    global GLOBAL_ENCHERE, GLOBAL_GAME_PLAYERS, GLOBAL_BOUTS, GLOBAL_PRIMES_ATTAQUE, GLOBAL_PRIMES_DEFENSE, \
        GLOBAL_POINTS_ATTAQUE, GLOBAL_DESCENDANTE_PLAYERS, GLOBAL_MISERES, GLOBAL_DESCENDANTE_POINTS

    enchere_name = None
    enchere_idx = None
    msg_list = msg.split(' ')
    msg_lower_list = msg.split(' ')

    if 'petite' in msg.lower():
        GLOBAL_ENCHERE = 1
        if 'garde' in msg.lower():
            raise ParseError('Confused, found petite and garde in the message')
        enchere_name = 'petite'
    elif 'garde' in msg.lower():
        if 'garde sans' in msg.lower():
            GLOBAL_ENCHERE = 4
            if 'garde contre' in msg.lower():
                raise ParseError('Confused, found garde sans and garde contre in the message')
            enchere_name = 'garde sans'
        elif 'garde contre' in msg.lower():
            GLOBAL_ENCHERE = 6
            enchere_name = 'garde contre'
        else:
            GLOBAL_ENCHERE = 2  # garde
            enchere_name = 'garde'
    else:
        raise ParseError('Confused, found no bid info')

    try:
        enchere_idx = msg_lower_list.find(enchere_name)  # TODO: handle two-word bids
    except ValueError:
        raise ParseError(f'Confused, could not find parsed bid {enchere_name}')

    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    preneur = msg_list[0]
    if preneur not in PLAYERS:
        raise ParseError(f'Confused, first word should be a player (Preneur), and {preneur} is not')
    GLOBAL_GAME_PLAYERS['Preneur'] = [preneur]

    scores = None
    return scores


@commands.command()
async def auto(ctx, value):
    return
