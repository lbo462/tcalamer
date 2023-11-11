import os
from dataclasses import dataclass
from typing import List
import torch
from torch import nn
import math

from .world import Weather

"""
When modifying the amount of inputs or outputs, 
remember to update this variable :
"""
amount_of_inputs = 14
# len(_daily_actions.actions) can't be imported due to circular imports ...
amount_of_outputs = 4


@dataclass
class NNInputs:
    """Modelization of the inputs for the neural network"""

    blue_sky: bool
    cloudy_sky: bool
    raining_sky: bool
    stromy_sky: bool

    wood_dist: float
    water_dist: float
    food_dist: float

    wreck_interest: float

    player_axe: bool
    player_bucket: bool
    player_fishing_rod: bool

    colony_axes: float
    colony_buckets: float
    colony_fishing_rods: float

    @classmethod
    def from_player(cls, player):
        colony = player._colony  # noqa
        world = player._world  # noqa
        wreck = world._wreck  # noqa

        def _clamp(value, min_value, max_value):
            return min(max(value, min_value), max_value)

        def distance(needs: int, objective: int) -> float:
            return math.exp(-4 * _clamp(needs / objective, 0, 1))

        colony_axes = len(
            [p for p in colony.alive_players if p.has_axe and p is not player]
        )
        colony_buckets = len(
            [p for p in colony.alive_players if p.has_bucket and p is not player]
        )
        colony_fishing_rods = len(
            [p for p in colony.alive_players if p.has_fishing_rod and p is not player]
        )

        return cls(
            blue_sky=world.weather is Weather.BLUE_SKY,
            cloudy_sky=world.weather is Weather.CLOUDY,
            raining_sky=world.weather is Weather.RAINING,
            stromy_sky=world.weather is Weather.STORM,
            food_dist=distance(colony.food_needs, colony.food_objective),
            water_dist=distance(colony.water_needs, colony.water_objective),
            wood_dist=distance(colony.wood_needs, colony.wood_objective),
            wreck_interest=math.exp(-1.4 * wreck.fail_rate),
            player_axe=player.has_axe,
            player_bucket=player.has_bucket,
            player_fishing_rod=player.has_fishing_rod,
            colony_axes=colony_axes,
            colony_buckets=colony_buckets,
            colony_fishing_rods=colony_fishing_rods,
        )

    def to_list(self) -> List[float]:
        """Returns a formatted list of inputs to be consumed by the neural network"""
        return [
            1 if self.blue_sky else 0,
            1 if self.cloudy_sky else 0,
            1 if self.raining_sky else 0,
            1 if self.stromy_sky else 0,
            self.food_dist,
            self.water_dist,
            self.wood_dist,
            self.wreck_interest,
            1 if self.player_axe else 0,
            1 if self.player_bucket else 0,
            1 if self.player_fishing_rod else 0,
            self.colony_axes,
            self.colony_buckets,
            self.colony_fishing_rods,
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
