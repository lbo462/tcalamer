from typing import Dict, TypeVar
from pydantic import BaseModel as PBaseModel

T = TypeVar("T", bound=PBaseModel)


class BaseModel:
    """Represent the base model for every class of the game"""

    def summarize(self) -> T:
        raise NotImplementedError()
