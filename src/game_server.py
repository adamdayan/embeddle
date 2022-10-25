import logging
from flask import Flask, request
from flask.logging import default_handler
from src.game_backend import GameManager

root_logger = logging.getLogger()
root_logger.addHandler(default_handler)
root_logger.setLevel(logging.INFO)

app = Flask(__name__)
game_manager = GameManager()

@app.route("/create_game", methods=["POST"])
def create_game():
    return game_manager.create_game(request.json)

@app.route("/join_game", methods=["POST"])
def join_game():
    return game_manager.join_game(request.json) 

@app.route("/get_state", methods=["POST"])
def get_state():
    return game_manager.get_state(request.json)

@app.route("/make_guess", methods=["POST"])
def make_guess():
    return game_manager.make_guess(request.json)