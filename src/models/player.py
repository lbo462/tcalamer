import random
from typing import List
from enum import IntEnum

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
        self.state = PlayerState.ALIVE
        self.inventory: List[Object] = []

    """Action methods
    These are the actions that a player can do for the colony 
    """

    def fetch_water(self):
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, Bucket):
                amount_fetched += o.use()

        self.colony.add_water(amount_fetched)

    def fetch_wood(self):
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, Axe):
                amount_fetched += o.use()

        self.colony.add_wood(amount_fetched)

    def fetch_food(self):
        amount_fetched = 1
        for o in self.inventory:
            if isinstance(o, FishingRod):
                amount_fetched += o.use()

        self.colony.add_food(amount_fetched)

    def search_wreck(self):
        """
        The player can go to the wreck and search for objects.
        He has a chance of getting a new item in its inventory
        """
        if random.random() < 0.5:  # 50 % chances
            new_object_class = random.choice(object_class_list)
            self.inventory.append(new_object_class())

    def __str__(self):
        return f"N°{self.number} - {', '.join([str(o) for o in self.inventory])}"
