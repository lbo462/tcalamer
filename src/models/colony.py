class InsufficientResources(Exception):
    """Raised when fetching too much of a resource compared to the amount stored in the colony"""


class Colony:
    """
    A colony has a certain amount of resources
    These resources are shared by the players living in the colony
    """

    def __init__(self):
        # Define the resources held by the colony
        self._water_level = 0
        self._wood_amount = 0
        self._food_amount = 0

    """
    The resources are protected attributes to force the use of the deposit methods
    To access the current amount of a resource, use the Python properties defined below :
    
    Each resource should be accessible though a property
    """

    @property
    def water_level(self):
        return self._water_level

    @property
    def wood_amount(self):
        return self._wood_amount

    @property
    def food_amount(self):
        return self._food_amount

    """Deposit methods
    These allows a player to add resources to the colony
    
    Each resource should define a deposit method
    """

    def add_water(self, amount: int):
        self._water_level += amount

    def add_wood(self, amount: int):
        self._wood_amount += amount

    def add_food(self, amount: int):
        self._food_amount += amount

    """Fetch methods
    These allows players to retrieve resources from the colony
    :raises InsufficientResources:
    :return: Amount retrieved
    
    Each resource should define a fetch method    
    """

    def retrieve_water(self, amount: int) -> int:
        if self.water_level - amount < 0:
            raise InsufficientResources("Water level too low")
        self._water_level -= amount
        return amount

    def retrieve_wood(self, amount: int) -> int:
        if self.wood_amount - amount < 0:
            raise InsufficientResources("Not enough wood")
        self._wood_amount -= amount
        return amount

    def retrieve_food(self, amount: int) -> int:
        if self.food_amount - amount < 0:
            raise InsufficientResources("Not enough food")
        self._food_amount -= amount
        return amount

    def __str__(self):
        return f"{self.water_level} water, {self.wood_amount} wood, {self.food_amount} food"
