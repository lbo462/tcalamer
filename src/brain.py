import os
from dataclasses import dataclass
from typing import List
import torch
from torch import nn


"""
When modifying the amount of inputs or outputs, 
remember to update this variable :
"""
amount_of_inputs = 8
# len(_daily_actions.actions) can't be imported due to circular imports ...
amount_of_outputs = 4


@dataclass
class NNInputs:
    """Modelization of the inputs for the neural network"""

    bucket_amount: int
    axe_amount: int
    fishing_rod_amount: int
    water_level: int
    wood_amount: int
    food_amount: int
    weather: "Weather"
    wreck_visits_amount: int
    # players_to_the_wood: int
    # players_to_the_water: int
    # players_to_the_food: int
    # players_waiting: int

    @classmethod
    def from_player(cls, player: "Player"):
        colony = player._colony  # noqa
        world = player._world  # noqa
        wreck = world._wreck  # noqa

        return cls(
            player.bucket_amount,
            player.axe_amount,
            player.fishing_rod_amount,
            colony.water_level,
            colony.wood_amount,
            colony.food_amount,
            world.weather,
            wreck.number_of_times_fetched,
            # colony.amount_of_players_to_the_wood,
            # colony.amount_of_players_to_the_water,
            # colony.amount_of_players_to_the_food,
            # colony.amount_of_free_players,
        )

    def to_list(self) -> List[float]:
        """Returns a formatted list of inputs to be consumed by the neural network"""
        return [
            self.bucket_amount,
            self.axe_amount,
            self.fishing_rod_amount,
            self.water_level,
            self.wood_amount,
            self.food_amount,
            self.weather.value,
            self.wreck_visits_amount,
            # self.players_to_the_wood,
            # self.players_to_the_water,
            # self.players_to_the_food,
            # self.players_waiting,
        ]

    def __str__(self):
        return f"{', '.join([str(i) for i in self.to_list()])}"


class _QNetwork(nn.Module):
    """Simple Q-Network"""

    def __init__(self, input_size: int, output_size: int):
        super(_QNetwork, self).__init__()

        # Adds two fully-connected layers
        self.fc1 = nn.Linear(input_size, 16)
        self.fc2 = nn.Linear(16, output_size)

    def forward(self, x):
        x = self.fc1(x)
        return self.fc2(x)


class Brain:
    def __init__(self, nn_filename: str = None):
        self._q_network = _QNetwork(
            input_size=amount_of_inputs, output_size=amount_of_outputs
        )

        if nn_filename and os.path.exists(nn_filename):
            # Loads from file
            self._q_network.load_state_dict(torch.load(nn_filename))
        # else, a random QNetwork is used

        self._q_network.eval()

    def chose_action(self, inputs: NNInputs) -> int:
        """Choose the best action to do with the Q-Network
        :return: The ID of the best action
        """
        _inputs = inputs.to_list()

        with torch.no_grad():
            q_values = self._q_network(torch.Tensor(_inputs))
            return torch.argmax(q_values).item()
