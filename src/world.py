import random
from enum import IntEnum
from typing import Union, List

from wreck import Wreck
from objects import T


class ResourceEmpty(Exception):
    """Raised when a certain resource is not present anymore"""


class Weather(IntEnum):
    BLUE_SKY = 0
    CLOUDY = 1
    RAINING = 2
    STORM = 3


class World:
    """
    The world has certain amount of resources
    The colony lives in the _world and take its resources
    The world also defines the weather
    """

    def __init__(
        self,
        wreck: Wreck,
        initial_water_level=5000,
        initial_wood_amount=5000,
        initial_food_amount=5000,
    ):
        self._wreck = wreck
        self._weather = Weather.BLUE_SKY

        self._initial_water_level = initial_water_level
        self._initial_wood_amount = initial_wood_amount
        self._initial_food_amount = initial_food_amount

        self._water_level = initial_water_level
        self._wood_amount = initial_wood_amount
        self._food_amount = initial_food_amount

        self._basic_water_fetch_factor = [3, 4, 5]
        self._basic_wood_fetch_factor = [3, 4, 5]
        self._basic_food_fetch_factor = [3, 4, 5]

    @property
    def initial_water_level(self) -> int:
        return self._initial_water_level

    @property
    def initial_wood_amount(self) -> int:
        return self._initial_wood_amount

    @property
    def initial_food_amount(self) -> int:
        return self._initial_food_amount

    @property
    def water_level(self) -> int:
        return self._water_level

    @property
    def wood_amount(self) -> int:
        return self._wood_amount

    @property
    def food_amount(self) -> int:
        return self._food_amount

    @property
    def weather(self) -> Weather:
        return self._weather

    """Fetch factors
    The fetch factors depends on the weather
    Theses changes the chances of getting more resources than requested
    """

    @property
    def _water_fetch_factor(self) -> List[int]:
        if self.weather is Weather.RAINING:
            return [2 * i for i in self._basic_water_fetch_factor]
        return self._basic_water_fetch_factor

    @property
    def _wood_fetch_factor(self) -> List[int]:
        if self.weather is Weather.STORM:
            return [2 * i for i in self._basic_wood_fetch_factor]
        return self._basic_wood_fetch_factor

    @property
    def _food_fetch_factor(self) -> List[int]:
        if self.weather is Weather.CLOUDY:
            return [2 * i for i in self._basic_wood_fetch_factor]
        return self._basic_food_fetch_factor

    """Fetch methods
    Get the resources out of the _world
    It is not possible to put resources back to the _world
    """

    def fetch_water(self, requested_amount: int) -> int:
        if self.water_level <= 0:
            raise ResourceEmpty("No more water ...")
        amount = requested_amount * random.choice(self._water_fetch_factor)

        if self.water_level - amount < 0:
            amount = self.water_level
            self._water_level = 0
            return amount

        self._water_level -= amount
        return amount

    def fetch_wood(self, requested_amount: int) -> int:
        if self.wood_amount <= 0:
            raise ResourceEmpty("No more wood ...")
        amount = requested_amount * random.choice(self._wood_fetch_factor)

        if self.wood_amount - amount < 0:
            amount = self.wood_amount
            self._wood_amount = 0
            return amount

        self._wood_amount -= amount
        return amount

    def fetch_food(self, requested_amount: int) -> int:
        if self.food_amount <= 0:
            raise ResourceEmpty("No more food ...")
        amount = requested_amount * random.choice(self._food_fetch_factor)

        if self.food_amount - amount < 0:
            amount = self.food_amount
            self._food_amount = 0
            return amount

        self._food_amount -= amount
        return amount

    def search_wreck(self) -> Union[None, T]:
        return self._wreck.search()

    def update(self):
        # Update the weather
        if self.weather is Weather.CLOUDY:
            self._weather = Weather.RAINING
        else:
            self._weather = random.choice(list(Weather))

    def __str__(self):
        return f"{self.water_level} water, {self.wood_amount} wood, {self.food_amount} food"
