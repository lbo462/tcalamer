import os
from typing import List
import torch
from torch import nn

from world import Weather

"""
When modifying the amount of inputs or outputs, 
remember to update this variable :
"""
amount_of_inputs = 8
# len(_daily_actions.actions) can't be imported due to circular imports ...
amount_of_outputs = 4


class NNInputs:
    """Modelization of the inputs for the neural network"""

    def __init__(
        self,
        amount_of_buckets_of_the_player: int,
        amount_of_axes_of_the_player: int,
        amount_of_fishing_rods_of_the_player: int,
        amount_of_water_held_by_the_colony: int,
        amount_of_wood_held_by_the_colony: int,
        amount_of_food_held_by_the_colony: int,
        current_weather: Weather,
        number_times_wreck_searched: int,
    ):
        self._amount_of_buckets_of_the_player = amount_of_buckets_of_the_player
        self._amount_of_axes_of_the_player = amount_of_axes_of_the_player
        self._amount_of_fishing_rods_of_the_player = (
            amount_of_fishing_rods_of_the_player
        )

        self._amount_of_water_held_by_the_colony = amount_of_water_held_by_the_colony
        self._amount_of_wood_held_by_the_colony = amount_of_wood_held_by_the_colony
        self._amount_of_food_held_by_the_colony = amount_of_food_held_by_the_colony

        self._current_weather = current_weather

        self._number_times_wreck_searched = number_times_wreck_searched

    def to_list(self) -> List[int]:
        """Returns a formatted list of inputs to be consumed by the neural network"""
        return [
            self._amount_of_buckets_of_the_player,
            self._amount_of_axes_of_the_player,
            self._amount_of_fishing_rods_of_the_player,
            self._amount_of_water_held_by_the_colony,
            self._amount_of_wood_held_by_the_colony,
            self._amount_of_food_held_by_the_colony,
            self._current_weather.value,
            self._number_times_wreck_searched,
        ]

    def __str__(self):
        return (
            f"{self._current_weather.name}, "
            f"{self._amount_of_buckets_of_the_player}b, "
            f"{self._amount_of_axes_of_the_player}a, "
            f"{self._amount_of_fishing_rods_of_the_player}f, "
            f"{self._amount_of_water_held_by_the_colony}wa, "
            f"{self._amount_of_wood_held_by_the_colony}wo, "
            f"{self._amount_of_food_held_by_the_colony}fo, "
            f"{self._number_times_wreck_searched}we"
        )


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
