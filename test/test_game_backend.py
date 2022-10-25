import unittest
import uuid

from src.game_backend import Game

class MockEmbeddings:
    def __init__(self, embeds):
        self.embeddings = embeds

class MockCohereClient:
    def embed(self, words):
        return MockEmbeddings([[0] for _ in range(50)])

class TestGame(unittest.TestCase):
    def test_too_many_players(self):
        game = Game(num_players=2)
        game.add_player(uuid.uuid4())
        game.add_player(uuid.uuid4())
        with self.assertRaises(Exception):
            game.add_player(uuid.uuid4())

    def test_correct_guess(self):
        game = Game(num_players=1)
        game.cohere_client = MockCohereClient()
        player_id = uuid.uuid4()
        game.add_player(player_id)
        res = game.make_guess(game.target_word, player_id)
        self.assertTrue(res["is_correct"] and res["distance"] == 0)

    def test_incorrect_guess(self):
        game = Game(num_players=1)
        game.cohere_client = MockCohereClient()
        game.get_target_word_embedding()
        player_id = uuid.uuid4()
        game.add_player(player_id)
        res = game.make_guess(game.target_word + "asdf", player_id)
        self.assertFalse(res["is_correct"])

    def test_incorrect_player_turn(self):
        game = Game(num_players=2)
        game.cohere_client = MockCohereClient()
        game.get_target_word_embedding()
        player_id_1 = uuid.uuid4()
        game.add_player(player_id_1)
        player_id_2 = uuid.uuid4()
        game.add_player(player_id_2)
        with self.assertRaises(Exception):
            game.make_guess(game.target_word + "asdf", player_id_2)

    def test_game_over(self):
        game = Game(num_players=1)
        game.cohere_client = MockCohereClient()
        player_id = uuid.uuid4()
        game.add_player(player_id)
        game.make_guess(game.target_word, player_id)
        self.assertTrue(game.get_state(player_id)["is_game_over"])     

    def test_game_not_over(self):
        game = Game(num_players=1)
        game.cohere_client = MockCohereClient()
        game.get_target_word_embedding()
        player_id = uuid.uuid4()
        game.add_player(player_id)
        game.make_guess(game.target_word + "blah", player_id)
        self.assertFalse(game.get_state(player_id)["is_game_over"])     
