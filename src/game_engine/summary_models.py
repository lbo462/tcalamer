from typing import List, Optional
from pydantic import BaseModel

from ..player import PlayerState
from ..world import Weather


class PlayerSummary(BaseModel):
    number: int
    state: PlayerState
    inventory: List[str]


class ResourcesSummary(BaseModel):
    wood_amount: int
    fish_amount: int
    water_level: int


class WreckItemSetSummary(BaseModel):
    item_class_name: str
    quantity: int


class WreckSummary(BaseModel):
    item_sets: List[WreckItemSetSummary]


class WorldStateSummary(BaseModel):
    resource: ResourcesSummary
    wreck_state: WreckSummary


class ColonyStateSummary(BaseModel):
    amounts_of_alive_players: int
    number_of_wreck_visits: int
    resources: ResourcesSummary


class GlobalStateSummary(BaseModel):
    world_state: WorldStateSummary
    colony_state: ColonyStateSummary


class ActionSummary(BaseModel):
    player_id: int
    action_id: int
    amount_retrieved: Optional[int]
    object_found: Optional[str]


class TurnSummary(BaseModel):
    weather: Weather
    players: List[PlayerSummary]
    morning_state: GlobalStateSummary
    daily_actions: List[ActionSummary]
    night_state: GlobalStateSummary


class GameSummary(BaseModel):
    turns: List[TurnSummary]
