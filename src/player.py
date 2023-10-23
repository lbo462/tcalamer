import random
from typing import List, Any, Callable, Generator
from enum import IntEnum

from actions import ActionRegistry
from world import ResourceEmpty
from colony import Colony
from objects import Object, Bucket, Axe, FishingRod

_daily_actions = ActionRegistry()


class PlayerState(IntEnum):
    ALIVE = 1
    DEAD = 2
    ESCAPED = 3
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
        self.world = colony.world
        self._state = PlayerState.ALIVE
        self.inventory: List[Object] = []
        self.actions: List[Callable] = []

    @property
    def state(self) -> PlayerState:
        return self._state

    """Daily action methods
    These are the actions that a player can do for the colony during the daylight.
    Each action has a defined ID. This identifier will used by by the neural network to output actions 
    """

    @_daily_actions(id_=1)
    def fetch_water(self) -> Generator[str, None, None]:
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, Bucket):
                amount_fetched += o.use()

        try:
            amount_fetched = self.world.fetch_water(amount_fetched)
            yield f"{self} fetched {amount_fetched} water"
            self.colony.add_water(amount_fetched)
        except ResourceEmpty as e:
            yield f"{self} : {e}"

    @_daily_actions(id_=2)
    def fetch_wood(self) -> Generator[str, None, None]:
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, Axe):
                amount_fetched += o.use()

        try:
            amount_fetched = self.world.fetch_wood(amount_fetched)
            yield f"{self} fetched {amount_fetched} wood"
            self.colony.add_wood(amount_fetched)
        except ResourceEmpty as e:
            yield f"{self} : {e}"

    @_daily_actions(id_=3)
    def fetch_food(self) -> Generator[str, None, None]:
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, FishingRod):
                amount_fetched += o.use()

        try:
            amount_fetched = self.world.fetch_food(amount_fetched)
            yield f"{self} fetched {amount_fetched} fish(es)"
            self.colony.add_food(amount_fetched)
        except ResourceEmpty as e:
            yield f"{self} : {e}"

    @_daily_actions(id_=4)
    def search_wreck(self) -> Generator[str, None, None]:
        """
        The player can go to the wreck and search for objects.
        He has a chance of getting a new item in its inventory
        """
        new_object = self.world.search_wreck()
        if new_object:
            yield f"{self} search wreck and found {new_object}"
            self.inventory.append(new_object)
        else:
            yield f"{self} search wreck and found nothing ..."

    """Eat & drink from colony actions
    These allows the player to get food and water from the colony in order to survive to the next day
    """

    def eat(self):
        """Removes a unit of food from the colony"""
        self.colony.retrieve_food(1)

    def drink(self):
        """Removes a unit of water from the colony"""
        self.colony.retrieve_water(1)

    def eat_and_drink(self):
        self.eat()
        self.drink()

    """States method
    Change the state of the player
    """

    def die(self):
        self._state = PlayerState.DEAD

    def flee(self):
        self._state = PlayerState.ESCAPED

    def heal(self):
        self._state = PlayerState.ALIVE

    def get_sick(self):
        self._state = PlayerState.SICK

    """Action choice
    The player should choose its actions with the following methods
    This will later be handled by neural networks
    """

    def make_daily_action(self, action_id: int, *args, **kwargs) -> Any:
        """Calls the actions referring the given ID"""
        return _daily_actions.call_action(action_id, self, *args, **kwargs)

    def make_random_daily_action(self, *args, **kwargs) -> Any:
        """Calls a random daily action"""
        random_id = random.randint(1, len(_daily_actions.actions))
        return _daily_actions.call_action(random_id, self, *args, **kwargs)

    def __str__(self):
        return f"N°{self.number}"
