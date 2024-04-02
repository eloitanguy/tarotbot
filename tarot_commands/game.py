import discord
from discord.ext import commands
import json
from tarot_commands.rules import CONTRAT_PAR_BOUT, PRIMES
from table2ascii import table2ascii as t2a
from tarot_commands.leaderboard import update_leaderboard
from tarot_commands.history import update_history
from unidecode import unidecode
from collections import OrderedDict


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

    @discord.ui.button(label='Calcul', style=discord.ButtonStyle.blurple)
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
             - primes_defense['Simple Poignée'] - primes_defense['Double Poignée'] - primes_defense['Triple Poignée']

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


def str_idx_to_split_idx(s, str_idx, split=' '):
    """
    Gives the index in s.split(split) corresponding to the index str_idx in the string
    Parameters
    ----------
    s : str
        input string
    str_idx : int
        index within s
    split : str, optional
        split argument for s.split(split), default to ' '

    Returns
    -------
    i : int
    """
    if s[str_idx] == split:
        raise ValueError(f'Input string index {str_idx} corresponds to a split <{split}> in input string {s}')
    if str_idx > len(s):
        raise ValueError(f'index {str_idx} >= {len(s)} length of input string')
    s_list = s.split(split)
    split_start_idx_in_str = 0
    for e_idx, e in enumerate(s_list):
        if split_start_idx_in_str <= str_idx < split_start_idx_in_str + len(e):  # str_idx is in e
            return e_idx
        split_start_idx_in_str += len(e) + 1


def find_split_idx_of_subsequence(s, sub, split=' '):
    """
    Finds the index within s.split(split) of the last element of sub.split(split)
    For example if s = 'i am now a tuna', the output for split=' ' and sub='now a' is 3.

    Parameters
    ----------
    s : str
        input string
    sub : str
        substring to locate within s
    split : str, optional
        split argument for s.split(split), default to ' '

    Returns
    -------
    i : int
    """
    str_idx = s.find(sub)  # let it raise ValueError if not found
    if str_idx == -1:
        raise ValueError(f'sub {sub} is not a substring of {s}')
    return str_idx_to_split_idx(s, str_idx + len(sub) - 1, split)


def clean_msg(msg):
    return msg.replace('.', '').replace(',', '').replace(':', '').replace(';', '').replace("'", '').replace('"', '')


def autoparse(msg):
    global GLOBAL_ENCHERE, GLOBAL_GAME_PLAYERS, GLOBAL_BOUTS, GLOBAL_PRIMES_ATTAQUE, GLOBAL_PRIMES_DEFENSE, \
        GLOBAL_POINTS_ATTAQUE, GLOBAL_DESCENDANTE_PLAYERS, GLOBAL_MISERES, GLOBAL_DESCENDANTE_POINTS

    enchere_name = None
    msg = clean_msg(msg)
    msg_list = msg.split(' ')
    msg_lower_list = msg.lower().split(' ')
    msg_decode_lower = unidecode(msg).lower()
    msg_decode_lower_list = msg_decode_lower.split(' ')

    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    preneur = msg_list[0]
    if preneur not in PLAYERS:
        if unidecode(preneur).lower() in ['desc', 'descendante']:
            return autoparse_desc(msg)
        raise ParseError(f'Confused, first word should be a player (Preneur), and {preneur} is not')
    GLOBAL_GAME_PLAYERS['Preneur'] = [preneur]

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

    # find bid location
    enchere_idx = None
    try:
        enchere_idx = find_split_idx_of_subsequence(msg.lower(), enchere_name)
    except ValueError:
        raise ParseError(f'Confused, could not find parsed bid {enchere_name}')

    vs_idx = None
    try:
        vs_idx = find_split_idx_of_subsequence(msg.lower(), 'vs')
    except ValueError:
        raise ParseError('Could not find required keyword <vs>')

    avec_idx = None
    try:
        avec_idx = msg_lower_list.index('avec')
    except ValueError:
        try:
            avec_idx = msg_lower_list.index('with')
        except ValueError:  # parsed 1 vs rest, check that only 1 name before vs
            for e in msg_list[:vs_idx]:
                if e in PLAYERS and e != preneur:
                    raise ParseError(
                        f'Parsed a 1 vs rest situation, but found an extra name '
                        f'{e} other than the preneur {preneur} before vs')

    # find partenaire name
    if avec_idx is not None:
        avec_count = 0
        for e in msg_list[avec_idx:vs_idx]:
            if e in PLAYERS:
                avec_count += 1
                GLOBAL_GAME_PLAYERS['Partenaire'].append(e)
            if avec_count > 1:
                raise ParseError(f'Found more than one partenaire.')

    # determine segments for attack primes, defense primes and miseres
    # misere
    misere_idx = None
    try:
        misere_idx = msg_decode_lower_list.index('misere')
    except ValueError:
        try:
            misere_idx = msg_lower_list.index('miseres')
        except ValueError:
            pass  # no misère

    # primes
    prime_a_idx, prime_d_idx = None, None
    if 'prime' in msg.lower():
        exists_prime_a = 'prime att' in msg_decode_lower or 'primes att' in msg_decode_lower
        if exists_prime_a:  # find primes attaque something
            try:
                prime_a_idx = find_split_idx_of_subsequence(msg_decode_lower, 'prime att')
            except ValueError:
                try:
                    prime_a_idx = find_split_idx_of_subsequence(msg_decode_lower, 'primes att')
                except ValueError:
                    raise ParseError(f'expected to find prime att(ack) but didnt')
        exists_prime_d = 'prime def' in msg_decode_lower or 'primes def' in msg_decode_lower
        if exists_prime_d:  # find prime(s) défense something
            try:
                prime_d_idx = find_split_idx_of_subsequence(msg_decode_lower, 'prime def')
            except ValueError:
                try:
                    prime_d_idx = find_split_idx_of_subsequence(msg_decode_lower, 'primes def')
                except ValueError:
                    raise ParseError(f'expected to find prime def(ense) but didnt')
        if not (exists_prime_a or exists_prime_d):  # only prime, assume for attack
            try:
                prime_a_idx = find_split_idx_of_subsequence(msg_decode_lower, 'prime')
            except ValueError:
                raise ParseError('Expected to find <prime> but didnt')

    segments_idx = sorted([(k, v) for (k, v) in
                          [('vs', vs_idx), ('prime_a', prime_a_idx), ('prime_d', prime_d_idx), ('misere', misere_idx)]
                          if v is not None], key=lambda c: c[1])

    # handle segment by segment
    for seg_idx, (seg_name, seg_position) in enumerate(segments_idx):
        next_seg_position = None if seg_idx == len(segments_idx) - 1 else segments_idx[seg_idx + 1][1]
        segment_msg_list = msg_list[seg_position:next_seg_position]
        segment_msg = ' '.join(segment_msg_list)
        if seg_name == 'vs':
            def_players_count = 0
            for e in segment_msg_list:
                if e in PLAYERS:
                    GLOBAL_GAME_PLAYERS['Défenseurs'].append(e)
                    def_players_count += 1
            if def_players_count <= 1 or def_players_count >= 5:
                raise ParseError(f'Parsed 1 or less defenders or 5 or more defenders in {segment_msg_list}')
            if GLOBAL_GAME_PLAYERS['Partenaire'] and def_players_count != 3:
                raise ParseError(f'Parsed {def_players_count}!=3 defenders in {segment_msg_list}, '
                                 f'but found a partenaire')
        elif seg_name == 'prime_a':
            for prime_name in PRIMES.keys():
                if unidecode(prime_name.lower()) in unidecode(segment_msg.lower()):
                    GLOBAL_PRIMES_ATTAQUE.append(prime_name)

        elif seg_name == 'prime_d':
            for prime_name in PRIMES.keys():
                if unidecode(prime_name.lower()) in unidecode(segment_msg.lower()):
                    GLOBAL_PRIMES_DEFENSE.append(prime_name)

        elif seg_name == 'misere':
            for e in segment_msg_list:
                if e in PLAYERS:
                    GLOBAL_MISERES.append(e)

    # find number of bouts: assume it's the only number between 0 and 3 separated by spaces
    for bouts in [0, 1, 2, 3]:
        found_bouts = 0
        if str(bouts) in msg_list:
            GLOBAL_BOUTS = bouts
            found_bouts += 1
        if found_bouts > 1:
            raise ParseError(f'Found more than one number interpreted as bouts')

    # find score: assume it's the only number over 4 separated by spaces in the msg
    for e in msg_list:
        found_scores = 0
        if e.isnumeric() and int(e) >= 4:
            GLOBAL_POINTS_ATTAQUE = int(e)
            found_scores += 1
        if found_scores > 1:
            raise ParseError(f'Found more than one number interpreted as score')

    reparse = (f"Preneur:    {GLOBAL_GAME_PLAYERS['Preneur']},\n"
               f"Partenaire: {GLOBAL_GAME_PLAYERS['Partenaire']},\n"
               f"Score:      {GLOBAL_POINTS_ATTAQUE},\n"
               f"Bouts:      {GLOBAL_BOUTS},\n"
               f"Enchère:    {enchere_name} ({GLOBAL_ENCHERE}),\n"
               f"Défense:    {GLOBAL_GAME_PLAYERS['Défenseurs']},\n"
               f"Primes Att: {GLOBAL_PRIMES_ATTAQUE},\n"
               f"Primes Déf: {GLOBAL_PRIMES_DEFENSE},\n"
               f"Misères:    {GLOBAL_MISERES}")

    return reparse


def autoparse_desc(msg):
    """
    Parses a message starting with 'descendante', then a names and scores. Updates the global params for descendante.
    Omitting punctuation, assumes 'descendante <name1> <score1> <name2> <score2> ...'
    """
    msg = clean_msg(msg)
    msg_list = msg.split(' ')

    with open('players.json', 'r') as f:
        PLAYERS = json.load(f)

    player_idx = 1
    for e_idx, e in enumerate(msg_list):
        if e in PLAYERS:
            if e_idx == len(msg_list) - 1 or not msg_list[e_idx + 1].isnumeric():
                raise ParseError(f'Could not find a score for {e}')
            GLOBAL_DESCENDANTE_PLAYERS[f'#{player_idx}'] = e
            GLOBAL_DESCENDANTE_POINTS.append(int(msg_list[e_idx + 1]))
            player_idx += 1

    reparse = f"Descendante:\n"
    for player_score, player in list(zip(GLOBAL_DESCENDANTE_POINTS, GLOBAL_DESCENDANTE_PLAYERS.values())):
        reparse = reparse + f"{player}: {player_score},\n"

    return reparse[:-2]  # removes last ,\n


@commands.command()
async def auto(ctx, *, value):
    """
    Tente d'interpréter le message et d'affecter les scores en conséquence. Cliquer sur le bouton valide et affecte.

    Elements de syntaxe imposés: (Attaque) 'vs' (Défense)

    Partenaire: mot-clef 'avec' ou 'with'

    Primes: 'prime attaque' ou 'prime défense' si nécessaire, et juste 'prime' est un raccourci pour Attaque

    Descendante: commencer par 'Descendante' ou desc puis mettre nom, score, nom, score etc

    """
    reset_cache()
    global GLOBAL_DESCENDANTE_POINTS
    try:
        reparse = autoparse(value)  # affects global values for the game information
    except ParseError as e:
        reset_cache()
        await ctx.send(e.args[0])
        return
    msg = '**Is this parse correct?:**\n' + reparse
    if reparse[:13] == 'Descendante:\n':  # parsed a descendante
        await ctx.send(f"Somme des points = {sum(GLOBAL_DESCENDANTE_POINTS)}." + msg,
                       view=DescendanteCalculButton())
    else:  # parsed a normal game
        await ctx.send(msg, view=GameCalculButton())
