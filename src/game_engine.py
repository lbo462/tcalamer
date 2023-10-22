from typing import Generator

from world import World
from colony import Colony, InsufficientResources
from player import Player, PlayerState


class GameEngine:
    """
    The GameEngine drives the whole game.
    It creates a colony and players in it.
    It defines the different steps of the game
    """

    def __init__(self, number_of_players: int):
        self.world = World()
        self.colony = Colony(self.world)
        self.players = []
        for i in range(0, number_of_players):
            self.players.append(Player(i, self.colony))

    @property
    def game_over(self) -> bool:
        """The game is over iff every player is dead or gone"""
        for player in self.players:
            if player.state in [PlayerState.ALIVE, PlayerState.SICK]:
                return False
        return True

    @property
    def in_game_players(self) -> Generator[Player, None, None]:
        """Returns an iterators of available players in the game"""
        for player in self.players:
            if player.state in [PlayerState.ALIVE, PlayerState.SICK]:
                yield player

    def update(self) -> Generator:
        """This updates the game and make the actions of a complete day, from dawn to dawn"""

        yield "THE DAY STARTS"

        # Step zero
        self.world.update()
        yield f"Weather of the day : {self.world.weather.name}"
        yield f"World resources : {self.world}"

        # First step : daily actions
        yield "EVERY ONE WORK"
        for player in self.in_game_players:
            for log in player.make_random_daily_action():
                yield log

        # Second step : Food and water count
        # enough_food = self.colony.food_amount >= len(self.players)
        # enough_water = self.colony.water_level >= len(self.players)

        # Third step : Eat and drink for the ones that can. The other dies
        yield f"NIGHT FALLS, COLONY RESOURCES : {self.colony}"
        for player in self.in_game_players:
            try:
                for log in player.eat():
                    yield log
                for log in player.drink():
                    yield log
            except InsufficientResources:
                for log in player.die():
                    yield log
