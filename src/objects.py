from typing import Any, TypeVar


class Object:
    """Abstract class to define every game items"""

    def use(self, *args, **kwargs) -> Any:
        """Defines the action when using an object"""

    def __str__(self):
        return self.__class__.__name__


class Bucket(Object):
    """Increase the amount of water fetched"""

    def use(self) -> int:
        """Return the bonus of water fetched"""
        return 1


class Axe(Object):
    """Increase the amount of wood fetched"""

    def use(self) -> int:
        """Return the bonus of wood fetched"""
        return 1


class FishingRod(Object):
    """Increase the amount of food fetched"""

    def use(self) -> int:
        """Return the bonus of food fetched"""
        return 1


T = TypeVar("T", bound=Object)
