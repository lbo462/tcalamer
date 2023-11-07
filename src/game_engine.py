from typing import Generator

from src.wreck import Wreck
from src.world import World
from src.colony import Colony
from src.player import Player
from src.objects import Bucket, Axe, FishingRod


class GameEngine:
    """
    The GameEngine drives the whole game.
    It creates a _colony and players in it.
    It defines the different steps of the game
    """

    def __init__(
        self,
        number_of_players: int,
        wreck_probability: float,
        amount_of_wood_per_player_to_leave=20,
        amount_of_water_per_player_to_leave=2,
        amount_of_food_per_player_to_leave=2,
        training=False,
        brain_trainer: "BrainTrainer" = None,
    ):
        # Create wreck
        wreck = Wreck(wreck_probability)
        wreck.add_item(Bucket, 1)
        wreck.add_item(Axe, 1)
        wreck.add_item(FishingRod, 1)

        # Create world
        self._world = World(wreck)

        # Create colony
        self.colony = Colony(
            self._world,
            amount_of_wood_per_player_to_leave=amount_of_wood_per_player_to_leave,
            amount_of_water_per_player_to_leave=amount_of_water_per_player_to_leave,
            amount_of_food_per_player_to_leave=amount_of_food_per_player_to_leave,
        )

        # Add players
        for i in range(0, number_of_players):
            self.colony.add_player(Player(i, self.colony, training, brain_trainer))

        # Initiate day counter
        self._day = 0

    @property
    def game_over(self) -> bool:
        """The game is over iff every player is dead or gone"""
        return len(self.colony.alive_players) <= 0

    @property
    def current_day(self) -> int:
        return self._day

    def update(self) -> Generator[str, None, None]:
        """This updates the game and make the _actions of a complete day, from dawn to dawn"""

        # Step zero, world update
        self._day += 1
        self._world.update()
        self.colony.update()

        yield f"--- DAWN OF DAY #{self._day} ({self._world.weather.name})"
        yield f"/ ---"
        yield f"| World : {self._world}"
        yield f"| Colony : {self.colony}"
        yield f"| {len(self.colony.alive_players)} players lefts"
        yield f"\\ ---"

        # First step : daily _actions
        for player in self.colony.alive_players:
            yield f"  > {player.make_best_daily_action()}"

        yield ""
        yield f"--- SUN GETS DOWN - {self.colony}"

        # Second step : Some must die
        if not self.colony.enough_resources:
            limiting_factor = self.colony.limiting_factor
            amount_of_players_to_die = len(self.colony.alive_players) - limiting_factor
            yield f"NOT ENOUGH RESOURCES : {amount_of_players_to_die} players must die."

            for i in range(0, amount_of_players_to_die):
                player_to_die = self.colony.get_random_alive_player()
                player_to_die.die(self.current_day)
                yield f"  X {player_to_die} died on day #{player_to_die.day_of_death}."

        if not self.game_over:
            # Third step : Diner
            yield f"EVERY ONE DINE"
            for player in self.colony.dine():
                yield f"  - {player} dine"

            # Fourth step : Verify if there's enough resources to leave
            if self.colony.able_to_leave:
                yield f"SOME LEAVE THE ISLE !"
                count = 0
                for player in self.colony.leave_isle():
                    yield f"  >> {player} took the raft"
                    count += 1
                yield f"--------- {count} PLAYERS ESCAPED ---------"

            # Fifth step : Close your eyes and sleep my darling
            else:
                yield "--------- NIGHT FALLS ------------"

        else:
            yield "--------- GAME OVER ------------"

        # Day summary
        yield f"/ ---"
        yield f"| World : {self._world}"
        yield f"| Colony : {self.colony}"
        yield f"| {len(self.colony.alive_players)} players lefts"
        yield f"\\ ---"
