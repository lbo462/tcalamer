"""
This file defines every objects the game contains
To add a new object, create a subclass of Object and add it to the object_class_list
"""
from typing import Any


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


# Add every existing objects in the following list :
object_class_list = [
    Bucket,
    Axe,
    FishingRod,
]
