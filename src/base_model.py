from typing import Dict


class BaseModel:
    """Represent the base model for every class of the game"""

    def summarize(self) -> Dict:
        raise NotImplementedError()
