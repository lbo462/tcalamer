import random
from typing import List, Callable, Type, Optional
from enum import IntEnum
from pydantic import BaseModel as PBaseModel, FilePath

from .base_model import BaseModel
from .actions import ActionRegistry
from .world import ResourceEmpty
from .objects import Object, Bucket, Axe, FishingRod, T
from .brain import Brain, NNInputs

_daily_actions = ActionRegistry()


class PlayerState(IntEnum):
    ALIVE = 1
    DEAD = 2
    ESCAPED = 3
    SICK = 4


class PlayerSum(PBaseModel):
    number: int
    alive: bool
    has_bucket: bool
    has_axe: bool
    has_fishing_rod: bool


class Player(BaseModel):
    """
    A player is defined by a _number (names ar for humans)
    He lives in a _colony and can add some resources to it.
    He also has objects in its _inventory to enhance his _actions
    """

    def __init__(
        self,
        number: int,
        colony,
        brain_location: Optional[FilePath] = None,
        training: bool = False,
        trainer=None,
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
        self._brain = Brain(brain_location) if not training else None
        self._training_enable = training
        self._trainer = trainer
        self.nn_vision_before_action: Optional[NNInputs] = None
        self.nn_vision_after_action: Optional[NNInputs] = None
        self.nn_action_taken: Optional[int] = None
        self.nn_fitness_before_action: Optional[float] = None
        self.nn_fitness_after_action: Optional[float] = None

    @property
    def name(self) -> str:
        return f"N°{self._number}"

    @property
    def number(self) -> int:
        return self._number

    @property
    def state(self) -> PlayerState:
        return self._state

    @property
    def day_of_death(self) -> int:
        if self._day_of_death == -1 or self.state is not PlayerState.DEAD:
            raise ValueError(f"{self} not dead yet")
        return self._day_of_death

    def get_current_vision(self) -> NNInputs:
        return NNInputs.from_player(self)

    """Items checkup"""

    def has_item(self, item_class: Type[T]) -> bool:
        for o in self._inventory:
            if isinstance(o, item_class):
                return True
        return False

    @property
    def has_bucket(self) -> bool:
        return self.has_item(Bucket)

    @property
    def has_axe(self) -> bool:
        return self.has_item(Axe)

    @property
    def has_fishing_rod(self) -> bool:
        return self.has_item(FishingRod)

    """Daily action methods
    These are the _actions that a player can do for the _colony during the daylight.
    Each action has a defined ID. This identifier will used by by the neural network to output _actions 
    """

    @_daily_actions(id_=0)
    def fetch_water(self) -> str:
        amount_fetched = 2 if self.has_bucket else 1

        try:
            amount_fetched = self._world.fetch_water(amount_fetched)
            self._colony.add_water(amount_fetched)
            return f"{self} fetched {amount_fetched} water"
        except ResourceEmpty as e:
            return f"{self} : {e}"

    @_daily_actions(id_=1)
    def fetch_wood(self) -> str:
        amount_fetched = 2 if self.has_axe else 1

        try:
            amount_fetched = self._world.fetch_wood(amount_fetched)
            self._colony.add_wood(amount_fetched)
            return f"{self} fetched {amount_fetched} wood"
        except ResourceEmpty as e:
            return f"{self} : {e}"

    @_daily_actions(id_=2)
    def fetch_food(self) -> str:
        amount_fetched = 2 if self.has_fishing_rod else 1

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
        new_object = self._world.search_wreck(self)
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

    """ActionSummary choice
    The player should choose its _actions with the following methods
    This will later be handled by neural networks
    """

    def _make_daily_action(self, action_id: int) -> str:
        """Calls the _actions referring the given ID"""
        return _daily_actions.call_action(action_id, self)

    def make_random_daily_action(self) -> str:
        """Calls a random daily action"""
        return random.choice(_daily_actions.actions).function(self)

    def make_best_daily_action(self) -> int:
        """
        Uses a brain to choose the best daily action and calls it
        If training was enabled, the player uses its brain trainer to make the decision
        This updates the vision before and after the action
        :return: ID of the action chosen
        """
        inputs = self.get_current_vision()
        self.nn_vision_before_action = inputs
        self.nn_fitness_before_action = self._colony.daily_fitness

        if self._training_enable:
            action_id = self._trainer.choose_action(inputs)
        else:
            action_id = self._brain.chose_action(inputs)

        self.nn_action_taken = action_id
        self._make_daily_action(action_id)

        self.nn_vision_after_action = self.get_current_vision()
        self.nn_fitness_after_action = self._colony.daily_fitness
        return action_id

    def summarize(self) -> PlayerSum:
        return PlayerSum(
            number=self._number,
            alive=self._state in [PlayerState.ALIVE, PlayerState.ESCAPED],
            has_bucket=self.has_bucket,
            has_axe=self.has_axe,
            has_fishing_rod=self.has_fishing_rod,
        )

    def __str__(self):
        return f"{self.name} ({len(self._inventory)} items)"
