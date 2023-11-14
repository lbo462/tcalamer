"""

This programs trains a neural network for the game
The created brain is then used by the player to make actions during the real game

"""

import random
import torch
from torch import nn, optim
from typing import Dict

from .game_engine import GameEngine, GameEngineParams
from .player import PlayerState, _daily_actions
from .brain import _QNetwork, NNInputs, amount_of_inputs, amount_of_outputs


class BrainTrainer:
    def __init__(
        self,
        ge_params: GameEngineParams,
        learning_rate: float,
        discount_factor: float,
        greedy_epsilon: float,
        iter_amount: int,
        max_win_streak: int,
    ):
        # Learning parameters
        self._learning_rate = learning_rate
        self._discount_factor = discount_factor
        self._greedy_epsilon = greedy_epsilon
        self._num_iterations = iter_amount
        self._max_win_streak = max_win_streak

        # Create a new neural network
        self._q_network = _QNetwork(
            input_size=amount_of_inputs, output_size=amount_of_outputs
        )
        self._optimizer = optim.Adam(
            self._q_network.parameters(), lr=self._learning_rate
        )

        # Choose parameters for the game engine
        ge_params.training = True
        ge_params.brain_trainer = self
        self._ge_params = ge_params

    @property
    def q_net_dict(self) -> Dict:
        return self._q_network.state_dict()

    def choose_action(self, inputs: NNInputs) -> int:
        """Take the inputs to return an action ID though the greedy epsilon algorithm"""

        # Falls to random action thanks to greedy epsilon
        if random.random() < self._greedy_epsilon:
            return random.randint(0, amount_of_outputs - 1)

        # Else, choose the current best action
        with torch.no_grad():
            q_values = self._q_network(torch.Tensor(inputs.to_list()))
            return q_values.argmax().item()

    def train(self):
        win_streak = 0
        for iteration in range(self._num_iterations):
            # Creates a new game engine for training purposes
            ge = GameEngine(self._ge_params)
            total_reward = 0

            day_sum = ge.run_single()
            while day_sum is not None:
                for player in [
                    p for p in ge.colony._players if p.nn_action_taken is not None
                ]:
                    # Take a look of the vision before and after the action
                    morning_inputs = player.nn_vision_before_action
                    night_inputs = player.nn_vision_after_action
                    # And the action chosen by the player
                    action_taken = player.nn_action_taken

                    # Compute its reward
                    reward = player.nn_fitness_after_action
                    if player.state is PlayerState.DEAD:
                        reward = 0
                        player.nn_action_taken = None
                    elif player.state is PlayerState.ESCAPED:
                        reward = 100
                        player.nn_action_taken = None
                    total_reward += reward
                    """
                    print(
                        f"Day #{ge.current_day} n°{player.number} "
                        f"{morning_inputs} : {player.nn_fitness_before_action:.5f} "
                        f"-> {_daily_actions.get_func(action_taken).__name__} = {reward:.5f}"
                    )
                    """
                    # Now, observe the result of the chosen action regarding the inputs
                    q_values = self._q_network(torch.Tensor(morning_inputs.to_list()))
                    next_q_values = self._q_network(
                        torch.Tensor(night_inputs.to_list())
                    )

                    # Update the value Q of the action using the Q-learning rule
                    q_values[action_taken] += self._learning_rate * (
                        reward
                        + self._discount_factor * next_q_values.max()
                        - q_values[action_taken]
                    )

                    # Update the Q-Network
                    self._optimizer.zero_grad()
                    loss = nn.MSELoss()(
                        q_values,
                        self._q_network(torch.Tensor(morning_inputs.to_list())),
                    )
                    loss.backward()
                    self._optimizer.step()

                day_sum = ge.run_single()

            if ge.colony.at_least_one_left_the_isle:
                win_streak += 1
            else:
                win_streak = 0

            if win_streak > self._max_win_streak:
                print("Stopped by win streak")
                break

            print(
                f"{1+iteration}/{self._num_iterations} "
                f"{'✔️' if ge.colony.at_least_one_left_the_isle else '❌'} "
                f"({win_streak}/{self._max_win_streak}) "
                f"{total_reward/(ge.current_day * len(ge.colony._players))}"
            )
