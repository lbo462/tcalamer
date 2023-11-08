from typing import Any, TypeVar


class Object:
    """Abstract class to define every game items"""

    def use(self, *args, **kwargs) -> Any:
        """Defines the action when using an object"""

    def __str__(self):
        return self.__class__.__name__


class Bucket(Object):
    """Increase the amount of water fetched"""


class Axe(Object):
    """Increase the amount of wood fetched"""


class FishingRod(Object):
    """Increase the amount of food fetched"""


T = TypeVar("T", bound=Object)
