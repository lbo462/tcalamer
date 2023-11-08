import random
from typing import Type, List, Union
from pydantic import BaseModel as PBaseModel

from .base_model import BaseModel
from .objects import T, Axe, Bucket, FishingRod
from .player import Player


class WreckSum(PBaseModel):
    buckets: int
    axes: int
    fishing_rods: int


class _ItemSetEmpty(Exception):
    """Raised when taking an object in an empty bucket"""


class _ItemSet:
    """An item set contains a single type of object in a certain quantity"""

    def __init__(self, item_class: Type[T], quantity: int):
        self.item_class = item_class
        self.quantity = quantity

    @property
    def is_empty(self) -> bool:
        return self.quantity <= 0

    def take_item(self) -> T:
        if self.quantity <= 0:
            raise _ItemSetEmpty(f"ItemSet of {self.item_class.__name__} is empty")
        self.quantity -= 1
        return self.item_class()


class Wreck(BaseModel):
    """The wreck contains multiple _item_sets of objects"""

    def __init__(self, probability: float):
        """Creates a new wreck with a certain _probability of finding objects"""

        if not 0 <= probability <= 1:
            raise ValueError("Probability should be between 0 and 1")

        self._probability = probability
        self._item_sets: List[_ItemSet] = []
        self._number_of_times_fetched = 0
        self._number_of_failed_fetch = 0

    @property
    def number_of_times_fetched(self) -> int:
        return self._number_of_times_fetched

    @property
    def number_of_failed_fetch(self) -> int:
        return self._number_of_failed_fetch

    @property
    def fail_rate(self) -> float:
        if self.number_of_times_fetched == 0:
            return 0
        return self.number_of_failed_fetch / self.number_of_times_fetched

    def add_item(self, item_class: Type[T], quantity: int):
        self._item_sets.append(_ItemSet(item_class, quantity))

    def _amount(self, item_class: Type[T]) -> bool:
        for item_set in self._item_sets:
            if item_set.item_class is item_class:
                return True
        return False

    def search(self, player: Player) -> Union[None, T]:
        """Search the wreck
        Returns None if no objects was found,
        Returns an item if an item is found
        There's no way to know if the wreck is empty or if no item was found
        """
        self._number_of_times_fetched += 1

        if random.random() < self._probability and len(self._item_sets) > 0:
            item_set_found: _ItemSet = random.choice(self._item_sets)
            if player.has_item(item_set_found.item_class):
                return self.search(player)
            try:
                item = item_set_found.take_item()
            except _ItemSetEmpty:
                # This case shouldn't happen if every item set is filled at the dawn of times
                self._item_sets.remove(item_set_found)
                self._number_of_failed_fetch += 1
                return None

            if item_set_found.is_empty:
                self._item_sets.remove(item_set_found)
            return item

        self._number_of_failed_fetch += 1
        return None

    def summarize(self) -> WreckSum:
        return WreckSum(
            buckets=self._amount(Bucket),
            axes=self._amount(Axe),
            fishing_rods=self._amount(FishingRod),
        )
