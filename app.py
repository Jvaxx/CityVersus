import time

from duelGame import DuelGame
import asyncio
import secrets
import json
from websockets.asyncio.server import serve, broadcast

JOIN = {}


async def send_init(connected, player: int, join_key: str):
    """
    Send initialisation message to the player. Used for the waiting screen.
    :param join_key: secret key of the lobby
    :param connected: set of websockets targeted
    :param player: integer between 1 and 2
    :return: null
    """
    event = {
        "type": "init",
        "join": join_key,
        "player": player,
    }
    broadcast(connected, json.dumps(event))


async def send_ready(connected, player: int):
    """
    Send the ready state to the players
    :param connected:
    :param player:
    :return:
    """
    event = {
        "type": "ready",
        "player": player,
    }
    broadcast(connected, json.dumps(event))


async def send_round_end(connected, correct_answer, last_damages):
    event = {"type": "round_end",
             "correct_id": correct_answer[1],
             "correct_name": correct_answer[0],
             "last_damages": last_damages,
             }
    broadcast(connected, json.dumps(event))


async def send_game_end(connected, winner, players_life):
    event = {
        "type": "game_end",
        "winner": winner,
        "players_life": players_life,
    }
    broadcast(connected, json.dumps(event))


async def send_answer(connected, countdown: float):
    """
    sends the answer to all players
    """
    event = {
        "type": "answer",
        "countdown": countdown,
    }
    broadcast(connected, json.dumps(event))


async def set_ready(websocket, game, player):
    game.players_ready[player-1] = True
    return game.players_ready == [True, True]


async def init_round(connected, game):
    question = game.get_question
    propositions = game.get_propositions
    event = {
        "type": "round_start",
        "question": question,
        "propositions": propositions,
        "players_life": game.players_life,
        "round_number": game.round_number,
    }
    broadcast(connected, json.dumps(event))

async def reset_game(connected, game):
    game.reset_game()
    event = {
        "type": "reset_game",
    }
    broadcast(connected, json.dumps(event))


async def player_handler(connected, websocket, player, data_received, game):
    """
    Handles the players
    :param connected:
    :param websocket:
    :param player:
    :param data_received:
    :return:
    """

    print(f'Joueur {player}: ', data_received)
    if data_received["type"] == "ready":
        both_ready = await set_ready(websocket, game, player)
        await send_ready(connected, player)
        if both_ready:
            await init_round(connected, game)
    if data_received["type"] == "answer":
        answer = game.get_answer
        result = game.play_round(player, int(data_received["geoname_id"]), round(time.time() * 1000))
        print("Result: ", result)
        if type(result) is float or type(result) is int:
            # Premier a répondre, timer déclanché
            await send_answer(connected, result)

        else:
            await send_round_end(connected, answer, game.last_damages)
            await asyncio.sleep(2)
            if not game.game_finished:
                print("Nouveau round")
                await init_round(connected, game)
            else:
                print("Fin de la partie")
                await send_game_end(connected, game.get_winner, game.players_life)
    if data_received["type"] == "replay":
        await reset_game(connected, game)


async def start(websocket):
    game = DuelGame()
    connected = {websocket}
    join_key = str(secrets.randbits(12))
    JOIN[join_key] = game, connected

    try:
        # Envoie la connexion du joueur au lobby.
        await send_init(connected, 1, join_key)

        print("Le premier joueur a rejoin la room: ", id(game))
        async for message in websocket:
            # print("Le joueur 1 a envoyé: ", message)
            data = json.loads(message)
            await player_handler(connected, websocket, 1, data, game)

    finally:
        del JOIN[join_key]


async def join(websocket, join_key):
    try:
        game, connected = JOIN[join_key]
        connected.add(websocket)
    except KeyError:
        pass
        return

    try:
        # Envoie la connexion au lobby.
        await send_init(connected, 2, join_key)

        print("Le deuxième joueur a rejoint la room: ", id(game))
        async for message in websocket:
            # print("Le deuxième joueur a envoyé: ", message)
            data = json.loads(message)
            await player_handler(connected, websocket, 2, data, game)

    finally:
        connected.remove(websocket)


async def handler(websocket):
    message = await websocket.recv()
    print(message)
    event = json.loads(message)
    assert event["type"] == "init"
    if "join" in event:
        await join(websocket, event["join"])
    else:
        await start(websocket)


async def main():
    async with serve(handler, "", 8001) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
