class Colony:
    """"""

    def __init__(self):
        self._water_level = 0
        self._wood_amount = 0
        self._food_amount = 0

    """"""

    @property
    def water_level(self):
        return self._water_level

    @property
    def wood_amount(self):
        return self._wood_amount

    @property
    def food_amount(self):
        return self._food_amount

    """"""

    def add_water(self, amount: int):
        self._water_level += amount

    def add_wood(self, amount: int):
        self._wood_amount += amount

    def add_food(self, amount: int):
        self._food_amount += amount

    def __str__(self):
        return f"{self.water_level} water, {self.wood_amount} wood, {self.food_amount} food"
