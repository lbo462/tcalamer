import random
from typing import Generator, List

from wreck import Wreck
from world import World
from colony import Colony, InsufficientResources
from player import Player, PlayerState
from objects import Bucket, Axe, FishingRod


class GameEngine:
    """
    The GameEngine drives the whole game.
    It creates a _colony and players in it.
    It defines the different steps of the game
    """

    def __init__(self, number_of_players: int, wreck_probability: float):
        # Create wreck
        wreck = Wreck(wreck_probability)
        wreck.add_item(Bucket, 1)
        wreck.add_item(Axe, 1)
        wreck.add_item(FishingRod, 1)

        # Create _world
        self._world = World(wreck)

        # Create _colony
        self.colony = Colony(self._world, [])

        # Add players
        for i in range(0, number_of_players):
            self.colony.add_player(Player(i, self.colony))

    @property
    def game_over(self) -> bool:
        """The game is over iff every player is dead or gone"""
        return len(self.colony.alive_players) <= 0

    @property
    def summary(self) -> str:
        return (
            f"World : {self._world}, Colony : {self.colony}, "
            f"Number of players alive on the isle : {len(self.colony.alive_players)}"
        )

    def update(self) -> Generator[str, None, None]:
        """This updates the game and make the _actions of a complete day, from dawn to dawn"""

        yield "--- THE DAY STARTS"

        # Step zero
        self._world.update()
        yield f"- Weather report : {self._world.weather.name}"
        yield f"- World resources : {self._world}"

        # First step : daily _actions
        yield "--- EVERY ONE WORK"

        for player in self.colony.alive_players:
            for log in player.make_random_daily_action():
                yield log

        yield f"--- NIGHT FALLS, COLONY RESOURCES : {self.colony}"

        # Second step : Some must die
        if not self.colony.enough_resources:
            yield "NOT ENOUGH RESOURCES"
            limiting_factor = self.colony.limiting_factor
            amount_of_players_to_die = len(self.colony.alive_players) - limiting_factor
            yield f"{amount_of_players_to_die} players must die."

            for i in range(0, amount_of_players_to_die):
                player_to_die = self.colony.get_random_alive_player()
                player_to_die.die()
                yield f"{player_to_die} was chosen to die"

        if not self.game_over:
            # Third step : Diner
            yield f"--- EVERY ONE EATS DINER"
            for _ in self.colony.make_diner():
                ...

            # Fourth step : Verify if there's enough resources to leave
            if self.colony.able_to_leave:
                count = 0
                for player in self.colony.leave_isle():
                    yield f"{player} took the raft"
                    count += 1
                yield f"--------- {count} PLAYERS ESCAPED ---------"

            # Fifth step : Close your eyes and sleep my darling
            else:
                yield "--------- THE NEXT DAY ------------"

        else:
            yield "--------- GAME OVER ------------"

        # Day summary
        yield self.summary
