import random
import math
from typing import List, Generator
from pydantic import BaseModel as PBaseModel

from .base_model import BaseModel
from .player import Player, PlayerState, PlayerSum
from .world import World


class ColonySum(PBaseModel):
    water: int
    food: int
    wood: int
    water_needs: int
    food_needs: int
    wood_needs: int
    players: List[PlayerSum]


class InsufficientResources(Exception):
    """Raised when fetching too much of a resource compared to the amount stored in the colony"""


class Colony(BaseModel):
    """
    A colony has a certain amount of resources
    These resources are shared by the players living in the _colony
    """

    def __init__(
        self,
        world: World,
        amount_of_wood_per_player_to_leave: int,
        amount_of_water_per_player_to_leave: int,
        amount_of_food_per_player_to_leave: int,
        initial_surviving_factor: int,
    ):
        self._world = world
        self._players: List[Player] = []

        # Defines initial colony resources
        self._water_level = 0
        self._wood_amount = 0
        self._food_amount = 0

        # This defines the amount of resources added per player in the colony
        self._initial_surviving_factor = initial_surviving_factor

        # Define the amount of resources to leave
        self._amount_of_wood_to_leave = amount_of_wood_per_player_to_leave
        self._amount_of_water_to_leave = amount_of_water_per_player_to_leave
        self._amount_of_food_to_leave = amount_of_food_per_player_to_leave

    @property
    def alive_players(self) -> List[Player]:
        """Returns the alive and sick players in the colony"""
        return [
            player
            for player in self._players
            if player.state in [PlayerState.ALIVE, PlayerState.SICK]
        ]

    @property
    def at_least_one_left_the_isle(self) -> bool:
        for player in self._players:
            if player.state is PlayerState.ESCAPED:
                return True
        return False

    @property
    def able_to_leave(self) -> bool:
        """Returns the possibility for the colony to leave"""
        return (
            self.wood_amount >= len(self.alive_players) * self._amount_of_wood_to_leave
            and self.food_amount
            >= len(self.alive_players) * self._amount_of_food_to_leave
            and self.water_level
            >= len(self.alive_players) * self._amount_of_water_to_leave
        )

    @property
    def limiting_factor(self) -> int:
        """Returns the amount of the least vital resource"""
        return min(self.water_level, self.food_amount)

    @property
    def enough_resources(self) -> bool:
        return self.limiting_factor >= len(self.alive_players)

    """Objectives"""

    @property
    def water_objective(self) -> int:
        return (self._amount_of_water_to_leave + 2) * len(self.alive_players)

    @property
    def food_objective(self) -> int:
        return (self._amount_of_food_to_leave + 2) * len(self.alive_players)

    @property
    def wood_objective(self) -> int:
        return self._amount_of_wood_to_leave * len(self.alive_players)

    """Needs"""

    @property
    def water_needs(self) -> int:
        return self.water_objective - self.water_level

    @property
    def food_needs(self) -> int:
        return self.food_objective - self.food_amount

    @property
    def wood_needs(self) -> int:
        return self.wood_objective - self.water_level

    @property
    def daily_fitness(self) -> float:
        wood_distance = self.wood_needs
        food_distance = self.food_needs
        water_distance = self.water_needs

        # Adapt distance to care about sign
        wood_distance = wood_distance if wood_distance > 0 else 0.1
        food_distance = food_distance if food_distance > 0 else 0.1
        water_distance = water_distance if water_distance > 0 else 0.1

        return 100 * (
            1 / math.exp(wood_distance)
            + 1 / math.exp(food_distance)
            + 1 / math.exp(water_distance)
        )

    """
    The resources are protected attributes to force the use of the deposit methods
    To access the current amount of a resource, use the Python properties defined below :
    
    Each resource should be accessible though a property
    """

    @property
    def water_level(self) -> int:
        return self._water_level

    @property
    def wood_amount(self) -> int:
        return self._wood_amount

    @property
    def food_amount(self) -> int:
        return self._food_amount

    """Deposit methods
    These allows a player to add resources to the colony
    
    Each resource should define a deposit method
    """

    def add_water(self, amount: int):
        self._water_level += amount

    def add_wood(self, amount: int):
        self._wood_amount += amount

    def add_food(self, amount: int):
        self._food_amount += amount

    """Fetch methods
    These allows players to retrieve resources from the colony
    :raises InsufficientResources:
    :return: Amount retrieved
    
    Each resource should define a fetch method    
    """

    def retrieve_water(self, amount: int) -> int:
        if self.water_level - amount < 0:
            raise InsufficientResources("Water level too low")
        self._water_level -= amount
        return amount

    def retrieve_wood(self, amount: int) -> int:
        if self.wood_amount - amount < 0:
            raise InsufficientResources("Not enough wood")
        self._wood_amount -= amount
        return amount

    def retrieve_food(self, amount: int) -> int:
        if self.food_amount - amount < 0:
            raise InsufficientResources("Not enough food")
        self._food_amount -= amount
        return amount

    """Other methods
    Some stuff I couldn't store
    """

    def add_player(self, player: Player):
        """Adds a new player in the colony"""
        self._players.append(player)

        # Add resources to live one day
        self.add_water(self._initial_surviving_factor)
        self.add_food(self._initial_surviving_factor)

    def get_random_alive_player(self) -> Player:
        return random.choice(self.alive_players)

    def dine(self) -> Generator[Player, None, None]:
        """Make every player eat and drink and returns an iterator of the players that eat and drink"""
        for player in self.alive_players:
            player.eat()
            player.drink()
            yield player

    def leave_isle(self) -> Generator[Player, None, None]:
        """Make every player leave the isle and return an iterator of the players leaving"""
        for player in self.alive_players:
            player.flee()
            yield player

    def summarize(self) -> ColonySum:
        return ColonySum(
            water=self.water_level,
            food=self.food_amount,
            wood=self.wood_amount,
            water_needs=self.water_needs,
            food_needs=self.food_needs,
            wood_needs=self.wood_needs,
            players=[p.summarize() for p in self._players],
        )

    def __str__(self):
        return f"{self.water_level} water, {self.wood_amount} wood, {self.food_amount} food"
