import random
from enum import IntEnum


class ResourceEmpty(Exception):
    """Raised when a certain resource is not present anymore"""


class Weather(IntEnum):
    BLUE_SKY = 0
    CLOUDY = 1
    RAINING = 2
    STORM = 3
    VOLCANO_ERUPTION = 4


class World:
    """
    The world has certain amount of resources
    The colony lives in the world and take its resources
    The world also defines the weather
    """

    def __init__(self):
        self._water_level = 10
        self._wood_amount = 10
        self._food_amount = 10

        self.weather = Weather.BLUE_SKY

    @property
    def water_level(self):
        return self._water_level

    @property
    def wood_amount(self):
        return self._wood_amount

    @property
    def food_amount(self):
        return self._food_amount

    def update(self):
        # Randomly change the weather
        self.weather = random.choice(list(Weather))

        # Add water to the world on rainy days
        if self.weather is Weather.RAINING:
            self._water_level += 10

    """Fetch methods
    Get the resources out of the world
    It is not possible to put resources back to the world
    """

    def fetch_water(self, amount: int) -> int:
        if self.water_level <= 0:
            raise ResourceEmpty("No more water ...")

        if self.water_level - amount < 0:
            amount_fetched = self.water_level
            self._water_level = 0
            return amount_fetched

        self._water_level -= amount
        return amount

    def fetch_wood(self, amount: int) -> int:
        if self.wood_amount <= 0:
            raise ResourceEmpty("No more wood ...")

        if self.wood_amount - amount < 0:
            amount_fetched = self.wood_amount
            self._wood_amount = 0
            return amount_fetched

        self._wood_amount -= amount
        return amount

    def fetch_food(self, amount: int) -> int:
        if self.food_amount <= 0:
            raise ResourceEmpty("No more food ...")

        if self.food_amount - amount < 0:
            amount_fetched = self.food_amount
            self._food_amount = 0
            return amount_fetched

        self._food_amount -= amount
        return amount

    def __str__(self):
        return f"{self.water_level} water, {self.wood_amount} wood, {self.food_amount} food"
