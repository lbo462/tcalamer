import torch
from fastapi import FastAPI
from pydantic import FilePath

from .game_engine import GameEngine, GameEngineParams, GameSum
from .brain_trainer import BrainTrainer

app = FastAPI()


@app.get("/check-brain")
def check_brain() -> bool:
    """Verify the existence of brains"""
    return True


@app.post("/run")
def run_game(ge_params: GameEngineParams) -> GameSum:
    """Runs the game"""
    return GameEngine(ge_params).run()


@app.post("/test")
def test(
    ge_params: GameEngineParams,
    amount_of_games: int = 1000,
) -> float:
    """Returns the win ratio"""
    wins = 0
    for _ in range(amount_of_games):
        ge = GameEngine(ge_params)
        ge.run()

        if ge.colony.at_least_one_left_the_isle:
            wins += 1
    return wins / amount_of_games


@app.post("/train")
def train_brain(
    ge_params: GameEngineParams,
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
        ge_params=ge_params,
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        greedy_epsilon=greedy_epsilon,
        iter_amount=iter_amount,
    )
    brain_trainer.train()
    torch.save(brain_trainer.q_net_dict, location)

    return location
