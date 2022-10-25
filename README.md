# embeddle

A multi-player, CLI version of [Semantle](https://semantle.com/) created to explore the CohereAI API. Players compete to guess a randomly selected word, using the euclidean distance between the embeddings of their guesses and the embedding of the selected word as clues. The backend currently uses the flask development server which is only appropriate for using on localhost, if you for some reason actually wanted to use this on the internet you should replace it with a proper WSGI server and probably NGINX to handle TLS. 

## How to play
Before starting the backend, you must save your CohereAI API key in a `creds.json` file at the root of the repo. The file should follow this format: 
```
{
	"cohere": "<COHERE API KEY HERE>"
}
```

In a terminal from the root of this repo, run `flask --app src.game_server run` to start the backend.  

To create a game, run `python3 play.py --create`. This will return the game id that other players will need to join the game. 

To join a game, run `python3 play.py` and enter the game id that the game creator has provided you with.
