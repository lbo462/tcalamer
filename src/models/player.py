import random
from typing import List, Any, Callable
from enum import IntEnum

from .actions import action_registry, UnregisteredAction
from .colony import Colony
from .objects import Object, object_class_list, Bucket, Axe, FishingRod


class PlayerState(IntEnum):
    ALIVE = 1
    DEAD = 2
    GONE = 3
    SICK = 4


class Player:
    """
    A player is defined by a number (names ar for humans)
    He lives in a colony and can add some resources to it.
    He also has objects in its inventory to enhance his actions
    """

    def __init__(self, number: int, colony: Colony):
        self.number = number
        self.colony = colony
        self._state = PlayerState.ALIVE
        self.inventory: List[Object] = []
        self.actions: List[Callable] = []

    @property
    def state(self) -> PlayerState:
        return self._state

    """Action methods
    These are the actions that a player can do for the colony.
    Each action has a defined ID. This identifier will used by by the neural network to output actions 
    """

    @action_registry(id_=1)
    def fetch_water(self):
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, Bucket):
                amount_fetched += o.use()

        self.colony.add_water(amount_fetched)

    @action_registry(id_=2)
    def fetch_wood(self):
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, Axe):
                amount_fetched += o.use()

        self.colony.add_wood(amount_fetched)

    @action_registry(id_=3)
    def fetch_food(self):
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, FishingRod):
                amount_fetched += o.use()

        self.colony.add_food(amount_fetched)

    @action_registry(id_=4)
    def search_wreck(self):
        """
        The player can go to the wreck and search for objects.
        He has a chance of getting a new item in its inventory
        """
        if random.random() < 0.5:  # 50 % chances
            new_object_class = random.choice(object_class_list)
            self.inventory.append(new_object_class())

    """Eat & drink from colony actions
    These allows the player to get food and water from the colony in order to survive to the next day
    """

    def eat(self):
        """Removes a unit of food from the colony"""
        self.colony.retrieve_food(1)

    def drink(self):
        """Removes a unit of water from the colony"""
        self.colony.retrieve_water(1)

    """States method
    Change the state of the player
    """

    def die(self):
        self._state = PlayerState.DEAD

    def flee(self):
        self._state = PlayerState.GONE

    def heal(self):
        if self.state is PlayerState.SICK:
            self._state = PlayerState.ALIVE

    def get_sick(self):
        if self.state is PlayerState.ALIVE:
            self._state = PlayerState.SICK

    """Action choice
    The player should choose its actions with the following methods
    This will later be handled by neural networks
    """

    def make_action(self, action_id: int, *args, **kwargs) -> Any:
        """Calls the actions referring the given ID"""
        for action in action_registry.actions:
            if action.id_ == action_id:
                return action.function(self, *args, **kwargs)

        raise UnregisteredAction(f"Action #{action_id} wasn't registered")

    def __str__(self):
        return f"N°{self.number} - {', '.join([str(o) for o in self.inventory])}"
