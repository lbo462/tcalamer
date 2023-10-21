from typing import List

from .colony import Colony
from .objects import Object, Bucket, Axe, FishingRod


class Player:
    def __init__(self, number: int, colony: Colony):
        self.number = number
        self.colony = colony
        self.inventory: List[Object] = []

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
        self.inventory.append(Axe())

    def __str__(self):
        return f"N°{self.number} - {', '.join([str(o) for o in self.inventory])}"
