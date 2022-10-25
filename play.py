import argparse
from ast import arg
from src.client import GameClient

play_parser = argparse.ArgumentParser()
play_parser.add_argument(
    "--create", action="store_true", required=False
)

args = play_parser.parse_args()
is_create = args.create
gc = GameClient()
if is_create:
    gc.create_game()
else:
    gc.join_game()

