"""
This file doesn't define any action but handle their registering

In order to register an action, create an instance of ActionRegistry and call it as a decorator as such:
>>> ar = ActionRegistry()
>>> @ar(id_=1)
>>> def foo():
>>>   ...

The registered functions are accessible though the created instance as such:
>>> print(ar.actions)

To call a registered method, use
>>> ar.call_action(1, ...)
"""

from dataclasses import dataclass
from typing import List, Callable, Any


class UnregisteredAction(Exception):
    """Raised when the action required is not the registry"""


@dataclass
class Action:
    """Defines an action together with its ID to be registered"""

    function: Callable
    id_: int


class ActionRegistry:
    """Keep track of every possible _actions though its decorator"""

    def __init__(self):
        self.actions: List[Action] = []

    def __call__(self, id_: int):
        def register_function(func: Callable):
            self.actions.append(Action(func, id_))

            def wrapper(*args, **kwargs):
                func(*args, **kwargs)

            return wrapper

        return register_function

    def get_func(self, id_: int) -> Callable:
        """
        Returns the actions callable registered with the given ID
        :raises UnregisteredAction:
        """
        for action in self.actions:
            if action.id_ == id_:
                return action.function

        raise UnregisteredAction(f"ActionSummary #{id_} wasn't registered")

    def call_action(self, id_: int, *args, **kwargs) -> Any:
        """Calls the action registered under the given ID"""
        return self.get_func(id_)(*args, **kwargs)
