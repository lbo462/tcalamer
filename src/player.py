import random
from typing import List, Callable, Generator
from enum import IntEnum

from settings import playable_brain_location
from actions import ActionRegistry
from world import ResourceEmpty
from objects import Object, Bucket, Axe, FishingRod
from brain import Brain, NNInputs

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

    def __init__(
        self, number: int, colony, training=False, trainer: "BrainTrainer" = None
    ):
        if training and not trainer:
            raise ValueError("Please, give a trainer to enable training")

        self._number = number
        self._colony = colony
        self._world = colony._world  # noqa
        self._state = PlayerState.ALIVE
        self._inventory: List[Object] = []
        self._actions: List[Callable] = []

        self._day_of_death = -1  # initialize purposefully with a wrong value

        # Brain and NN stuffs blah blah blah
        # don't set brain when training enabled, the trainer do the job
        self._brain = Brain(playable_brain_location) if not training else None
        self._training_enable = training
        self._trainer = trainer
        self.nn_vision_before_action: NNInputs = None  # noqa
        self.nn_vision_after_action: NNInputs = None  # noqa
        self.nn_action_taken: int = None  # noqa
        self.nn_fitness_before_action: float = None  # noqa
        self.nn_fitness_after_action: float = None  # noqa

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

    @property
    def bucket_amount(self) -> int:
        counter = 0
        for o in self._inventory:
            if isinstance(o, Bucket):
                counter += 1
        return counter

    @property
    def axe_amount(self) -> int:
        counter = 0
        for o in self._inventory:
            if isinstance(o, Axe):
                counter += 1
        return counter

    @property
    def fishing_rod_amount(self) -> int:
        counter = 0
        for o in self._inventory:
            if isinstance(o, FishingRod):
                counter += 1
        return counter

    def get_current_vision(self) -> NNInputs:
        return NNInputs.from_player(self)

    """Daily action methods
    These are the _actions that a player can do for the _colony during the daylight.
    Each action has a defined ID. This identifier will used by by the neural network to output _actions 
    """

    @_daily_actions(id_=0)
    def fetch_water(self) -> str:
        amount_fetched = 1 + self.bucket_amount

        try:
            amount_fetched = self._world.fetch_water(amount_fetched)
            self._colony.add_water(amount_fetched)
            return f"{self} fetched {amount_fetched} water"
        except ResourceEmpty as e:
            return f"{self} : {e}"

    @_daily_actions(id_=1)
    def fetch_wood(self) -> str:
        amount_fetched = 1 + self.axe_amount

        try:
            amount_fetched = self._world.fetch_wood(amount_fetched)
            self._colony.add_wood(amount_fetched)
            return f"{self} fetched {amount_fetched} wood"
        except ResourceEmpty as e:
            return f"{self} : {e}"

    @_daily_actions(id_=2)
    def fetch_food(self) -> str:
        amount_fetched = 1 + self.fishing_rod_amount

        try:
            amount_fetched = self._world.fetch_food(amount_fetched)
            self._colony.add_food(amount_fetched)
            return f"{self} fetched {amount_fetched} fish(es)"
        except ResourceEmpty as e:
            return f"{self} : {e}"

    @_daily_actions(id_=3)
    def search_wreck(self) -> str:
        """
        The player can go to the wreck and search for objects.
        He has a chance of getting a new item in its _inventory
        """
        new_object = self._world.search_wreck()
        if new_object:
            self._inventory.append(new_object)
            return f"{self} search wreck and found {new_object}"
        return f"{self} search wreck and found nothing ..."

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

    def _make_daily_action(self, action_id: int) -> str:
        """Calls the _actions referring the given ID"""
        return _daily_actions.call_action(action_id, self)

    def make_random_daily_action(self) -> str:
        """Calls a random daily action"""
        return random.choice(_daily_actions.actions).function()

    def make_best_daily_action(self) -> str:
        """
        Uses a brain to choose the best daily action and calls it
        If training was enabled, the player uses its brain trainer to make the decision
        This updates the vision before and after the action
        """
        inputs = self.get_current_vision()
        self.nn_vision_before_action = inputs
        self.nn_fitness_before_action = self._colony.daily_fitness

        if self._training_enable:
            action_id = self._trainer.choose_action(inputs)
        else:
            action_id = self._brain.chose_action(inputs)

        self.nn_action_taken = action_id
        output: str = self._make_daily_action(action_id)

        self.nn_vision_after_action = self.get_current_vision()
        self.nn_fitness_after_action = self._colony.daily_fitness
        return output

    def __str__(self):
        return f"{self.name} ({len(self._inventory)} items)"
