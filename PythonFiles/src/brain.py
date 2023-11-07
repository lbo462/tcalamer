import os
from dataclasses import dataclass
from typing import List
import torch
from torch import nn
import math

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
    
    blue_sky : bool
    cloudy_sky : bool
    raining_sky : bool
    stromy_sky : bool

    wood_dist : float
    water_dist : float
    fish_dist : float

    wreck_interest : float

    player_axe : bool
    player_bucket : bool
    player_fishing_rod :bool

    colony_axes : float
    colony_buckets : float
    colony_fishing_rods :float


    @classmethod
    def from_player(cls, player):
        colony = player._colony  # noqa
        world = player._world  # noqa
        wreck = world._wreck  # noqa

        def clamp(value, min_value, max_value):
            return min(max(value, min_value), max_value)

        # Attribution de la météo
        blue_sky = 1 if world.weather is Weather.BLUE_SKY else 0
        cloudy_sky = 1 if world.weather is Weather.CLOUDY else 0
        raining_sky = 1 if world.weather is Weather.RAINING else 0
        stromy_sky = 1 if world.weather is Weather.STORM else 0

        #TODO : dont repeat yourself
        # Attribution des distances 
        wood_obj = colony._amount_of_wood_to_leave * len(colony.alive_players)
        fish_obj = (colony._amount_of_food_to_leave + 2) * len(colony.alive_players)
        water_obj = (colony._amount_of_water_to_leave + 2) * len(colony.alive_players)
            # Calculer distance + normaliser + restreindre entre 0 et 1 + exponentielle négative
        fish_dist = math.exp(-4*clamp((wood_objective - colony.wood_amount) / wood_obj,0,1))
        water_dist = math.exp(-4*clamp((wood_objective - colony.wood_amount) / wood_obj,0,1))      
        wood_dist = math.exp(-4*clamp((wood_objective - colony.wood_amount) / wood_obj,0,1))
        
        # Intérêt épave 
        ratio = wreck.number_of_failed_fetch / wreck.number_of_times_fetched
        wreck_interest = math.exp(-(ratio*1.4))

        # Joueur 
        player_axe = 1 if player.has_axe else 0
        player_bucket = 1 if player.has_bucket else 0
        player_fishing_rod = 1 if player.has_fishing_rod else 0

        # Groupe
        colony_axe_number = (-1) if player.has_axe else 0
        colony_fishing_rod_number = (-1) if player.has_bucket else 0
        colony_bucket_number = (-1) if player.has_fishing_rod else 0

        for player in colony.alive_players :
            colony_bucket_number += (1 if player.has_bucket else 0)
            colony_fishing_rod_number += (1 if player.has_fishing_rod else 0)
            colony_axe_number += (1 if player.has_axe else 0)

        colony_axes = colony_axe_number / len(colony.alive_players)
        colony_buckets = colony_bucket_number / len(colony.alive_players)
        colony_fishing_rods = colony_fishing_rod_number / len(colony.alive_players)
        
        return cls(
            
            blue_sky,
            cloudy_sky,
            raining_sky,
            stromy_sky,
            fish_dist,
            water_dist,
            wood_dist,
            wreck_interest,
            player_axe,
            player_bucket,
            player_fishing_rod,
            colony_axe,
            colony_bucket,
            colony_fishing_rod,
        )

    def to_list(self) -> List[float]:
        """Returns a formatted list of inputs to be consumed by the neural network"""
        return [
            self.blue_sky,
            self.cloudy_sky,
            self.raining_sky,
            self.stromy_sky,
            self.fish_dist,
            self.water_dist,
            self.wood_dist,
            self.wreck_interest,
            self.player_axe,
            self.player_bucket,
            self.player_fishing_rod,
            self.colony_axe,
            self.colony_bucket,
            self.colony_fishing_rod,
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
