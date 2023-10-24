import random
from typing import List, Any, Callable, Generator
from enum import IntEnum

from actions import ActionRegistry
from world import ResourceEmpty

from objects import Object, Bucket, Axe, FishingRod

_daily_actions = ActionRegistry()


class PlayerState(IntEnum):
    ALIVE = 1
    DEAD = 2
    ESCAPED = 3
    SICK = 4


class Player:
    """
    A player is defined by a _number (names ar for humans)
    He lives in a _colony and can add some resources to it.
    He also has objects in its _inventory to enhance his _actions
    """

    def __init__(self, number: int, colony):
        self._number = number
        self._colony = colony
        self._world = colony._world  # noqa
        self._state = PlayerState.ALIVE
        self._inventory: List[Object] = []
        self._actions: List[Callable] = []

        self._day_of_death = -1  # initialize purposefully with a wrong value

    @property
    def name(self) -> str:
        return f"N°{self._number}"

    @property
    def state(self) -> PlayerState:
        return self._state

    @property
    def day_of_death(self) -> int:
        if self._day_of_death == -1 or self.state is not PlayerState.DEAD:
            raise ValueError(f"{self} not dead yet")
        return self._day_of_death

    """Daily action methods
    These are the _actions that a player can do for the _colony during the daylight.
    Each action has a defined ID. This identifier will used by by the neural network to output _actions 
    """

    @_daily_actions(id_=1)
    def fetch_water(self) -> Generator[str, None, None]:
        amount_fetched = 1
        for o in self._inventory:
            if isinstance(o, Bucket):
                amount_fetched += o.use()

        try:
            amount_fetched = self._world.fetch_water(amount_fetched)
            yield f"{self} fetched {amount_fetched} water"
            self._colony.add_water(amount_fetched)
        except ResourceEmpty as e:
            yield f"{self} : {e}"

    @_daily_actions(id_=2)
    def fetch_wood(self) -> Generator[str, None, None]:
        amount_fetched = 1
        for o in self._inventory:
            if isinstance(o, Axe):
                amount_fetched += o.use()

        try:
            amount_fetched = self._world.fetch_wood(amount_fetched)
            yield f"{self} fetched {amount_fetched} wood"
            self._colony.add_wood(amount_fetched)
        except ResourceEmpty as e:
            yield f"{self} : {e}"

    @_daily_actions(id_=3)
    def fetch_food(self) -> Generator[str, None, None]:
        amount_fetched = 1
        for o in self._inventory:
            if isinstance(o, FishingRod):
                amount_fetched += o.use()

        try:
            amount_fetched = self._world.fetch_food(amount_fetched)
            yield f"{self} fetched {amount_fetched} fish(es)"
            self._colony.add_food(amount_fetched)
        except ResourceEmpty as e:
            yield f"{self} : {e}"

    @_daily_actions(id_=4)
    def search_wreck(self) -> Generator[str, None, None]:
        """
        The player can go to the wreck and search for objects.
        He has a chance of getting a new item in its _inventory
        """
        new_object = self._world.search_wreck()
        if new_object:
            yield f"{self} search wreck and found {new_object}"
            self._inventory.append(new_object)
        else:
            yield f"{self} search wreck and found nothing ..."

    """Eat & drink from _colony _actions
    These allows the player to get food and water from the _colony in order to survive to the next day
    """

    def eat(self):
        """Removes a unit of food from the _colony"""
        self._colony.retrieve_food(1)

    def drink(self):
        """Removes a unit of water from the _colony"""
        self._colony.retrieve_water(1)

    """States method
    Change the state of the player
    """

    def die(self, day_of_death: int):
        self._state = PlayerState.DEAD
        self._day_of_death = day_of_death

    def flee(self):
        self._state = PlayerState.ESCAPED

    def heal(self):
        self._state = PlayerState.ALIVE

    def get_sick(self):
        self._state = PlayerState.SICK

    """Action choice
    The player should choose its _actions with the following methods
    This will later be handled by neural networks
    """

    def _make_daily_action(self, action_id: int, *args, **kwargs) -> Any:
        """Calls the _actions referring the given ID"""
        return _daily_actions.call_action(action_id, self, *args, **kwargs)

    def make_random_daily_action(self, *args, **kwargs) -> Any:
        """Calls a random daily action"""
        random_id = random.randint(1, len(_daily_actions.actions))
        return self._make_daily_action(random_id, *args, **kwargs)

    def __str__(self):
        return f"{self.name} ({len(self._inventory)} items)"
