import random
from typing import TypeVar, Type, List, Union

from objects import Object

T = TypeVar("T", bound=Object)


class ItemSetEmpty(Exception):
    """Raised when taking an object in an empty bucket"""


class ItemSet:
    """An item set contains a single type of object in a certain quantity"""

    def __init__(self, item_class: Type[T], quantity: int):
        self.item_class = item_class
        self.quantity = quantity

    @property
    def is_empty(self) -> bool:
        return self.quantity <= 0

    def take_item(self) -> T:
        if self.quantity <= 0:
            raise ItemSetEmpty(f"ItemSet of {self.item_class.__name__} is empty")
        self.quantity -= 1
        return self.item_class()


class Wreck:
    """The wreck contains multiple item_sets of objects"""

    def __init__(self, probability: float):
        """Creates a new wreck with a certain probability of finding objects"""

        if not 0 <= probability <= 1:
            raise ValueError("Probability should be between 0 and 1")

        self.probability = probability
        self.item_sets: List[ItemSet] = []

    def add_item(self, item_class: Type[T], quantity: int):
        self.item_sets.append(ItemSet(item_class, quantity))

    def search(self) -> Union[None, T]:
        """Search the wreck
        Returns None if no objects was found,
        Returns an item if an item is found
        There's no way to know if the wreck is empty or if no item was found
        """
        if random.random() < self.probability and len(self.item_sets) > 0:
            item_set_found: ItemSet = random.choice(self.item_sets)
            try:
                item = item_set_found.take_item()
            except ItemSetEmpty:
                # This case shouldn't happen if every item set is filled at the dawn of times
                self.item_sets.remove(item_set_found)
                return None

            if item_set_found.is_empty:
                self.item_sets.remove(item_set_found)
            return item

        return None
