"""

This programs trains a neural network for the game
The created brain is then used by the player to make actions during the real game

"""

import random
from typing import Generator

import torch
from torch import nn, optim

from settings import number_of_player, wreck_probability, trained_brain_location
from game_engine import GameEngine
from player import PlayerState
from brain import _QNetwork, NNInputs, amount_of_inputs, amount_of_outputs


class BrainTrainer:
    def __init__(self):
        # Learning parameters
        self._learning_rate = 0.001
        self._discount_factor = 0.99
        self._greedy_epsilon = 0.1
        self._num_iterations = 200

        # Choose parameters for the game engine
        self._number_of_player = number_of_player
        self._wreck_probability = wreck_probability

        # Create a new neural network
        self._q_network = _QNetwork(
            input_size=amount_of_inputs, output_size=amount_of_outputs
        )
        self._optimizer = optim.Adam(
            self._q_network.parameters(), lr=self._learning_rate
        )

    def choose_action(self, inputs: NNInputs) -> int:
        """Take the inputs to return an action ID though the greedy epsilon algorithm"""

        # Falls to random action thanks to greedy epsilon
        if random.random() < self._greedy_epsilon:
            return random.randint(0, amount_of_outputs - 1)

        # Else, choose the current best action
        with torch.no_grad():
            q_values = self._q_network(torch.Tensor(inputs.to_list()))
            return q_values.argmax().item()

    def train(self) -> Generator[str, None, None]:
        for iteration in range(self._num_iterations):
            # Creates a new game engine for training purposes
            ge = GameEngine(
                number_of_players=self._number_of_player,
                wreck_probability=self._wreck_probability,
                training=True,
                brain_trainer=self,
            )

            total_reward = 0

            while not ge.game_over:
                """
                Update the game for the current day,
                where the players chooses a training action
                """
                for _ in ge.update():
                    ...

                for player in ge.colony.alive_players:
                    # Take a look of the vision before and after the action
                    morning_inputs = player.nn_vision_before_action
                    night_inputs = player.nn_vision_after_action
                    # And the action chosen by the player
                    action_taken = player.nn_action_taken

                    # Compute its reward
                    reward = player.nn_fitness_after_action
                    if player.state is PlayerState.DEAD:
                        reward = -100
                    elif player.state is PlayerState.ESCAPED:
                        reward = 1000 / ge.current_day
                    total_reward += reward

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

            yield f"{iteration} : {total_reward}"


if __name__ == "__main__":
    brain_trainer = BrainTrainer()
    for log in brain_trainer.train():
        print(log)

    torch.save(brain_trainer._q_network.state_dict(), trained_brain_location)  # noqa
    print(f"Saved brain at {trained_brain_location}")
