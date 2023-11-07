from typing import List
from pydantic import BaseModel

from player import PlayerState
from world import Weather


class PlayerFullState(BaseModel):
    number: int
    state: PlayerState
    inventory: List[str]


class Resources(BaseModel):
    wood_amount: int
    fish_amount: int
    water_level: int


class WreckItemSet(BaseModel):
    item_class_name: str
    quantity: int


class WreckState(BaseModel):
    item_sets: List[WreckItemSet]


class WorldState(BaseModel):
    resource: Resources
    wreck_state: WreckState


class ColonyState(BaseModel):
    amounts_of_alive_players: int
    number_of_wreck_visits: int
    resources: Resources


class GlobalState(BaseModel):
    world_state: WorldState
    colony_state: ColonyState


class Action(BaseModel):
    player_id: int


class Turn(BaseModel):
    weather: Weather
    morning_state: GlobalState
    night_state: GlobalState
