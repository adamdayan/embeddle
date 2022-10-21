import json
import uuid
import logging
from cmath import sqrt
from random import randint
from secrets import token_hex
from threading import Lock
import cohere
import jwt
from flask import Flask, make_response
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError 

def read_words():
    with open("words.txt", "r") as f:
        words = f.readlines()
    return words

WORDS = open("words.txt", "r").readlines()
COHERE_API_KEY = json.load(open("../creds.json"))["cohere"]

def compute_euclidean_distance(vec1, vec2):
    if len(vec1) != len(vec2):
        raise Exception("Vector lengths do not match")
    cur_sum = 0
    for p1, p2 in zip(vec1, vec2):
        cur_sum += (p1 - p2)**2
    return sqrt(cur_sum)

class Game:
    def __init__(self, num_players):
        num_players = num_players
        id = uuid.uuid4()
        players = set()
        turn_order = []
        game_lock = Lock()
        cur_turn = 0
        cohere_client = cohere.Client(COHERE_API_KEY)
        target_word = WORDS[randint(0, len(WORDS)-1)]
        target_embedding = self.get_embedding(target_word)
        is_game_over = False
        winner = None

    def add_player(self, player_id):
        if len(self.players) > self.num_players:
            raise Exception("Game already full")
        self.players.add(player_id)
        self.turn_order.append(player_id)

    def get_state(self, player_id):
        state = {
            "winner": self.winner,
            "is_turn": len(self.players) == self.num_players and player_id == self.turn_order[self.cur_turn % self.num_players]
        }
    
    def get_embedding(self, word):
        return self.cohere_client.embed(word).embeddings[0]

    def make_guess(self, guess):
        cur_turn+= 1
        if guess == self.target_word:
            winner = cur_turn % self.num_players
            return {
                "is_correct": True,
                "distance": 0
            }
        guess_embedding = self.get_embedding(guess)
        return {
            "is_correct": False,
            "distance": compute_euclidean_distance(guess_embedding, self.target_embedding)
        }


class GameManager:
    def __init__(self):
        ongoing_games = {}
        key = token_hex(128)

    def encode_auth_token(self, game_id, player_id):
        return jwt.encode({"game_id": game_id, "player_id": player_id}, self.key, algorithm="HS256")

    def decode_auth_token(self, auth_token):
        payload = jwt.decode(auth_token, self.key, algorithms="HS256")
        return payload["game_id"], payload["player_id"]
    
    def create_game(self, body):
        try:
            body = json.loads(body)
            num_players = body["num_players"]
        except Exception:
            logging.exception("Bad create_game request")
            raise BadRequest()

        try:
            new_game = Game(num_players)
            with new_game.game_lock:
                self.ongoing_games[new_game.uuid] = new_game
                player_id = uuid.uuid4()
                new_game.add_player(player_id)
        except Exception:
           logging.exception("Failed to create_game")
           raise InternalServerError()

        
        return make_response(
            {"auth_token": self.encode_auth_token(new_game.id, player_id)}, 200
        )

    def join_game(self, body):
        try:
            body = json.loads(body)
            game_id = body["game_id"]
            game = self.ongoing_games[game_id]
        except Exception:
            logging.exception("Bad join_game request")
            raise BadRequest()

        try:
            player_id = uuid.uuid4()
            with game.game_lock:
                game.add_player(player_id)
        except Exception:
            logging.exception("Failed to join_game")
            raise InternalServerError()
        
        return make_response(
            {"auth_token": self.encode_auth_token(game.id, player_id)}, 200
        )

    def get_state(self, body):
        try:
            body = json.loads(body)
            game_id, player_id = self.decode_auth_token(body["auth_token"])
            game = self.ongoing_games[game_id]
        except Exception:
            logging.exception("Bad is_turn request")
            raise BadRequest()

        try:
            with game.game_lock:
                state = game.get_state()
        except Exception: 
            logging.exception("Failed to check get_state")
            raise InternalServerError()

        return make_response(state, 200)

    def make_guess(self, body):
        try:
            body = json.loads(body)
            game_id, player_id = self.decode_auth_token(body["auth_token"])
            guess = body["guess"]
            game = self.ongoing_games[game_id]
        except Exception:
            logging.exception("Bad make_guess request")
            raise BadRequest()

        try:
            with game.game_lock:
                result = game.make_guess(guess)
        except Exception:
            logging.exception("Failed to make_guess")
            raise InternalServerError()
        return make_response(result, 200)