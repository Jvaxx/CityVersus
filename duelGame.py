import json
import random
import time

ROUND_MULTIPLICATOR = 2
TIME_MULTIPLICATOR = 0.03
WRONG_ANSWER_MULTIPLICATOR = 200


class DuelGame:
    """
    Main class handling the game in itself.
    Rules of the game:
    -in the Geoguessr style
    -2 players, a certain quantity of life (5000) and each round:
        -a country name as question and four cities with one being the capital of the country
        -the first player to answer starts a countdown for the other player (5s)
        -at the end of the timer or when both player answered, the life is recalculated
    -the game finishes when one of the players reaches 0 life.
    """

    def __init__(self, gamemode: str = "capital"):
        self.max_life: int = 5000
        self.players_life: list[int] = [5000, 5000]
        self.gamemode = gamemode
        self.countdown: float = 10
        self.active_capital = {}
        self.active_propositions = []
        self.has_played = [False, False]
        self.time_of_answer = [0, 0]
        self.good_answer = [False, False]
        self.round_number = 0
        self.players_ready = [False, False]
        self.last_damages = [0, 0]

        self.capital_list = []
        self.cities_list = []

        self._load_capitals()
        self._load_cities()
        self._initialize_round()

    def _load_capitals(self, path: str = "./capitales.json"):
        with open(path, "r", encoding="utf-8") as file:
            self.capital_list = json.load(file)

    def _load_cities(self, path: str = "./cities.json"):
        with open(path, "r", encoding="utf-8") as file:
            self.cities_list = json.load(file)

    @property
    def game_finished(self):
        return 0 in self.players_life

    @property
    def get_winner(self):
        if self.players_life[0] > self.players_life[1]:
            return 1
        return 2

    @property
    def get_life(self):
        return self.players_life

    @property
    def get_last_damages(self):
        return self.last_damages

    @property
    def get_question(self):
        return self.active_capital["country_name"]

    @property
    def get_propositions(self):
        return self.active_propositions

    @property
    def get_answer(self):
        return self.active_capital["capital_name"], self.active_capital["capital_id"]

    def _initialize_round(self):
        self.has_played = [False, False]
        self.good_answer = [False, False]
        self.round_number += 1
        self.time_of_answer = [0, 0]
        self.active_capital = random.choice(self.capital_list)

        self.active_propositions = []
        propositions = random.choices(self.cities_list, k=3)
        for proposition in propositions:
            self.active_propositions.append([proposition["city_name"], proposition["city_id"]])
        self.active_propositions.append([self.active_capital["capital_name"], self.active_capital["capital_id"]])
        random.shuffle(self.active_propositions)

    def play_round(self, player: int, choice_id: int, time: int):
        """
        Saves the answer of a player. Player must be 1 or 2. Raises ValueError if the player has already played.
        Returns the countdown (float, in seconds) if the player is the first to play. Returns players lives otherwise.

        :param player: int between 1 and 2
        :param choice_id: int geoname id
        :param time: int time in milliseconds since epoch
        :return: float countdown in seconds if this is the first move. tuple of players lives otherwise.
        """

        if not self.has_played[player - 1]:
            # Le joueur n'a pas encore joué

            # Date de la reponse
            self.time_of_answer[player - 1] = time

            # Enregistrement de la réponse
            self.good_answer[player - 1] = choice_id == self.active_capital["capital_id"]
            self.has_played[player - 1] = True

            if self.has_played == [True, True]:
                # L'autre joueur a déjà joué
                return self._end_round()
            else:
                # Le joueur est le premier a jouer
                return self.countdown

        else:
            # Le joueur a déjà joué
            raise ValueError

    def _end_round(self):
        time_diff = (self.time_of_answer[1] - self.time_of_answer[0])
        player1_first = time_diff >= 0


        # player 1 damage
        damage1 = player1_first * (not self.good_answer[0]) * self.good_answer[1] * ROUND_MULTIPLICATOR * self.round_number * WRONG_ANSWER_MULTIPLICATOR
        damage1 += (not player1_first) * ((self.good_answer == [True, True]) * ROUND_MULTIPLICATOR * self.round_number * TIME_MULTIPLICATOR * abs(time_diff)
                                        + (self.good_answer == [False, True]) * ROUND_MULTIPLICATOR * self.round_number * (TIME_MULTIPLICATOR*abs(time_diff) + WRONG_ANSWER_MULTIPLICATOR))

        # player 2 damage
        damage2 = (not player1_first) * (not self.good_answer[1]) * self.good_answer[0] * ROUND_MULTIPLICATOR * self.round_number * WRONG_ANSWER_MULTIPLICATOR
        damage2 += player1_first * ((self.good_answer == [True, True]) * ROUND_MULTIPLICATOR * self.round_number * TIME_MULTIPLICATOR * abs(time_diff)
                                         + (self.good_answer == [True, False]) * ROUND_MULTIPLICATOR * self.round_number * (TIME_MULTIPLICATOR*abs(time_diff) + WRONG_ANSWER_MULTIPLICATOR))

        damage1, damage2 = round(damage1), round(damage2)
        self.players_life[0] -= damage1
        self.players_life[1] -= damage2
        print("damage 1: ", damage1)
        print("damage 2: ", damage2)
        self.last_damages = [damage1, damage2]

        # Avoid negative values and round lives
        for i in range(2):
            self.players_life[i] = round(self.players_life[i])
            if self.players_life[i] < 0:
                self.players_life[i] = 0

        self._initialize_round()
        return self.get_life

    def reset_game(self):
        self.players_life = [5000, 5000]
        self.countdown = 10
        self.active_capital = {}
        self.active_propositions = []
        self.has_played = [False, False]
        self.time_of_answer = [0, 0]
        self.good_answer = [False, False]
        self.round_number = 0
        self.players_ready = [False, False]
        self.last_damages = [0, 0]
        self._initialize_round()



# game = DuelGame()
# while not game.game_finished:
#     question = game.get_question
#     propositions = game.get_propositions
#
#     print("Capitale de", question, "?")
#     for proposition in propositions:
#         print(proposition)
#
#     for i in range(2):
#         resp = int(input("id: "))
#         resp = propositions[-1][1]
#         res = game.play_round(i+1, resp, round(time.time() * 1000))
#         if type(res) is float:
#             print("Premier a répondre, timer start.")
#         if type(res) is list:
#             print("Les deux ont répondu. Vies: ", res)
# print("partie terminée.")
