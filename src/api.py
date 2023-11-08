import torch
from typing import Optional
from fastapi import FastAPI
from pydantic import FilePath

from .game_engine import GameEngine, GameSum
from .brain_trainer import BrainTrainer

app = FastAPI()


@app.get("/check-brain")
def check_brain() -> bool:
    """Verify the existence of brains"""
    return True


@app.get("/run")
def run_game(
    brain_location: Optional[FilePath] = None,
    number_of_players: int = 5,
) -> GameSum:
    """Runs the game"""
    return GameEngine(
        number_of_players=number_of_players,
        brain_location=brain_location,
    ).run()


@app.get("/test")
def test(
    brain_location: Optional[FilePath] = None,
    number_of_players: int = 5,
    amount_of_games: int = 1000,
) -> float:
    """Returns the win ratio"""
    wins = 0
    for _ in range(amount_of_games):
        ge = GameEngine(
            number_of_players=number_of_players,
            brain_location=brain_location,
        )

        ge.run()

        if ge.colony.at_least_one_left_the_isle:
            wins += 1
    return wins / amount_of_games


@app.post("/train")
def train_brain(
    number_of_players: int = 5,
    learning_rate: float = 0.001,
    discount_factor: float = 0.99,
    greedy_epsilon: float = 0.1,
    iter_amount: int = 1000,
) -> FilePath:
    """
    Trains a single brain with the given parameters
    The file is then saved at the given location and can be used in-game
    :return: path of the saved brain, same as the one given in parameters
    """
    location = "brains/trained_q_network.pth"

    brain_trainer = BrainTrainer(
        number_of_players=number_of_players,
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        greedy_epsilon=greedy_epsilon,
        iter_amount=iter_amount,
    )
    brain_trainer.train()
    torch.save(brain_trainer.q_net_dict, location)

    return location
