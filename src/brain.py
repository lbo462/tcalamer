import os
from typing import List
import torch
from torch import nn

"""
When modifying the amount of inputs or outputs, 
remember to update this variable :
"""
amount_of_inputs = 10
# len(_daily_actions.actions) can't be imported due to circular imports ...
amount_of_outputs = 4


class NNInputs:
    """Modelization of the inputs for the neural network"""

    def __init__(self, player: "Player"):
        self._player = player
        self._colony = player._colony  # noqa
        self._world = self._colony._world  # noqa
        self._wreck = self._world._wreck  # noqa

    def to_list(self) -> List[float]:
        """Returns a formatted list of inputs to be consumed by the neural network"""
        return [
            # self._player.bucket_amount,
            # self._player.axe_amount,
            # self._player.fishing_rod_amount,
            self._colony.water_level,
            self._colony.wood_amount,
            self._colony.food_amount,
            self._world.weather.value,
            self._wreck.number_of_times_fetched,
            self._colony.amount_of_player_to_the_water,
            self._colony.amount_of_player_to_the_wood,
            self._colony.amount_of_player_to_the_food,
            self._colony.amount_of_player_to_the_wreck,
            self._colony.amount_of_free_players,
        ]

    def __str__(self):
        return f"{', '.join([str(i) for i in self.to_list()])}"


class _QNetwork(nn.Module):
    """Simple Q-Network"""

    def __init__(self, input_size: int, output_size: int):
        super(_QNetwork, self).__init__()

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