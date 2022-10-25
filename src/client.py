import requests
import uuid
from time import sleep
from tabulate import tabulate

class GameClient:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.auth_token = None
        self.guesses = []
        self.last_state = None

    def create_game_request(self, num_players):
        resp = requests.post(
            url=f"{self.base_url}/create_game",
            json={"num_players": num_players}
        )
        if resp.status_code != 200:
            return False
        self.game_id = resp.json()["game_id"]
        self.auth_token = resp.json()["auth_token"]
        return True
    
    def join_game_request(self):
        resp = requests.post(
            url=f"{self.base_url}/join_game",
            json={"game_id": self.game_id.hex}
        )
        if resp.status_code != 200:
            return False
        self.auth_token = resp.json()["auth_token"]
        return True

    def make_guess_request(self, guess):
        resp = requests.post(
            url=f"{self.base_url}/make_guess",
            json={"guess": guess, "auth_token": self.auth_token}
        )
        if resp.status_code != 200:
            return False
        self.is_winner = resp.json()["is_correct"]
        self.guesses.append({
            "guess": guess,
            "distance": resp.json()["distance"]
        })
        return True

    def get_state_request(self):
        resp = requests.post(
            url=f"{self.base_url}/get_state",
            json={"auth_token": self.auth_token}
        )
        if resp.status_code != 200:
            return False
        self.last_state = resp.json()
        return True

    def create_game(self):
        is_created = False
        while not is_created:
            print("How many players will join this game?")
            num_players = int(input())
            is_created = self.create_game_request(num_players)
            if not is_created:
                print("Failed to create game, try again")
            else:
                print(f"Created game with id {self.game_id}.")
                if num_players > 1:
                    print("Waiting for other players to join")
        self.play_game()

    
    def join_game(self):
        is_joined = False
        while not is_joined:
            print("Enter the game id of the game you wish to join")
            self.game_id = uuid.UUID(input())
            is_joined = self.join_game_request()
            if not is_joined:
                print("Failed to join game, try again")
            else:
                print(f"Successfully joined game {self.game_id}")
        self.play_game()

        
    def play_game(self):
        self.get_state_request()
        while not self.last_state["is_game_over"]:
            if self.last_state["is_turn"]:
                print("Enter your guess")
                guess = input()
                self.make_guess_request(guess)
                self.display_guesses()
            else:
                sleep(0.5)
            self.get_state_request()
        if self.is_winner:
            print("Congratulations, you guessed the word!")
        else:
            print("Commiserations, you lost")

    def display_guesses(self):
        sorted_guesses = sorted(self.guesses, key=lambda guess : guess["distance"])
        print(tabulate(sorted_guesses, headers="keys"))



if __name__=="__main__":
    gc = GameClient()
    gc.create_game() 