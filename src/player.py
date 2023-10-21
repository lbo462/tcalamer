import random
from typing import List, Any, Callable, Generator
from enum import IntEnum

from actions import ActionRegistry
from colony import Colony
from objects import Object, object_class_list, Bucket, Axe, FishingRod

_daily_actions = ActionRegistry()


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

        yield f"{self} fetched {amount_fetched} water"
        self.colony.add_water(amount_fetched)

    @_daily_actions(id_=2)
    def fetch_wood(self) -> Generator[str, None, None]:
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, Axe):
                amount_fetched += o.use()

        yield f"{self} fetched {amount_fetched} wood"
        self.colony.add_wood(amount_fetched)

    @_daily_actions(id_=3)
    def fetch_food(self) -> Generator[str, None, None]:
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, FishingRod):
                amount_fetched += o.use()

        yield f"{self} fetched {amount_fetched} fish(es)"
        self.colony.add_food(amount_fetched)

    @_daily_actions(id_=4)
    def search_wreck(self) -> Generator[str, None, None]:
        """
        The player can go to the wreck and search for objects.
        He has a chance of getting a new item in its inventory
        """
        if random.random() < 0.5:  # 50 % chances
            new_object_class = random.choice(object_class_list)
            new_object = new_object_class()
            yield f"{self} search wreck and found {new_object}"
            self.inventory.append(new_object)
        else:
            yield f"{self} search wreck and found nothing ..."

    """Eat & drink from colony actions
    These allows the player to get food and water from the colony in order to survive to the next day
    """

    def eat(self) -> Generator[str, None, None]:
        """Removes a unit of food from the colony"""
        self.colony.retrieve_food(1)
        yield f"{self} eats"

    def drink(self) -> Generator[str, None, None]:
        """Removes a unit of water from the colony"""
        self.colony.retrieve_water(1)
        yield f"{self} drinks"

    """States method
    Change the state of the player
    """

    def die(self) -> Generator[str, None, None]:
        yield f"{self} died"
        self._state = PlayerState.DEAD

    def flee(self) -> Generator[str, None, None]:
        yield f"{self} escaped"
        self._state = PlayerState.GONE

    def heal(self) -> Generator[str, None, None]:
        if self.state is PlayerState.SICK:
            yield f"{self} is now healed"
            self._state = PlayerState.ALIVE
        else:
            yield f"{self} was not sick"

    def get_sick(self) -> Generator[str, None, None]:
        if self.state is PlayerState.ALIVE:
            yield f"{self} is now sick"
            self._state = PlayerState.SICK
        else:
            yield f"{self} was already sick"

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
