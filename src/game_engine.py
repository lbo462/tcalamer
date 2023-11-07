from typing import List
from pydantic import BaseModel as PBaseModel

from wreck import Wreck, WreckSum
from world import World, WorldSum
from colony import Colony, ColonySum
from player import Player
from objects import Bucket, Axe, FishingRod


class PlayerAction(PBaseModel):
    player_id: int
    action_id: int


class GameStateSum(PBaseModel):
    world: WorldSum
    wreck: WreckSum
    colony: ColonySum


class Day(PBaseModel):
    day: int
    actions: List[PlayerAction]
    night_state: GameStateSum


class GameSum(PBaseModel):
    initial_state: GameStateSum
    days: List[Day]


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
        brain_trainer=None,
    ):
        # Create wreck
        wreck = Wreck(wreck_probability)
        wreck.add_item(Bucket, 1)
        wreck.add_item(Axe, 1)
        wreck.add_item(FishingRod, 1)
        self._wreck = wreck

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
    def _game_over(self) -> bool:
        """The game is over iff every player is dead or gone"""
        return len(self.colony.alive_players) <= 0

    @property
    def _current_day(self) -> int:
        return self._day

    def _update(self) -> Day:
        """This updates the game and make the _actions of a complete day, from dawn to dawn"""

        # Step zero, world update
        self._day += 1
        self._world.update()
        self.colony.update()

        # First step : daily actions
        actions: List[PlayerAction] = []
        for player in self.colony.alive_players:
            action_id = player.make_best_daily_action()
            actions.append(
                PlayerAction(
                    player_id=player.number,
                    action_id=action_id,
                )
            )

        # Second step : Some must die
        if not self.colony.enough_resources:
            limiting_factor = self.colony.limiting_factor
            amount_of_players_to_die = len(self.colony.alive_players) - limiting_factor

            for i in range(0, amount_of_players_to_die):
                player_to_die = self.colony.get_random_alive_player()
                player_to_die.die(self._current_day)

        if not self._game_over:
            # Third step : Diner
            for _ in self.colony.dine():
                ...

            # Fourth step : Verify if there's enough resources to leave
            if self.colony.able_to_leave:
                for _ in self.colony.leave_isle():
                    ...

        return Day(
            day=self._day,
            actions=actions,
            night_state=GameStateSum(
                world=self._world.summarize(),
                wreck=self._wreck.summarize(),
                colony=self.colony.summarize(),
            ),
        )

    def run(self) -> GameSum:
        initial_state: GameStateSum
        days: List[Day] = []

        # Compute initial state
        initial_state = GameStateSum(
            world=self._world.summarize(),
            wreck=self._wreck.summarize(),
            colony=self.colony.summarize(),
        )

        # Compute days
        while not self._game_over:
            day = self._update()
            days.append(day)

        return GameSum(
            initial_state=initial_state,
            days=days,
        )
