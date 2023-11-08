from typing import List, Optional
from pydantic import BaseModel as PBaseModel, FilePath, Field

from .wreck import Wreck, WreckSum
from .world import Weather, World, WorldSum
from .colony import Colony, ColonySum
from .player import Player
from .objects import Bucket, Axe, FishingRod


class PlayerAction(PBaseModel):
    player_id: int
    action_id: int


class GameStateSum(PBaseModel):
    world: WorldSum
    wreck: WreckSum
    colony: ColonySum


class DaySum(PBaseModel):
    day: int
    actions: List[PlayerAction]
    night_state: GameStateSum


class GameSum(PBaseModel):
    initial_state: GameStateSum
    days: List[DaySum]


class GameEngine:
    """
    The GameEngine drives the whole game.
    It creates a _colony and players in it.
    It defines the different steps of the game
    """

    def __init__(
        self,
        number_of_players: int,
        brain_location: Optional[FilePath] = "brains/trained_q_network.pth",
        # Wreck
        wreck_probability: float = 0.5,
        bucket_amount: int = 1,
        axe_amount: int = 1,
        fishing_rod_amount: int = 1,
        # World
        initial_water_level: int = 5000,
        initial_food_amount: int = 5000,
        initial_wood_amount: int = 5000,
        basic_water_fetch_factor: List[int] = None,
        basic_wood_fetch_factor: List[int] = None,
        basic_food_fetch_factor: List[int] = None,
        default_weather: Weather = Weather.BLUE_SKY,
        # Colony
        amount_of_wood_per_player_to_leave: int = 5,
        amount_of_water_per_player_to_leave: int = 1,
        amount_of_food_per_player_to_leave: int = 1,
        initial_surviving_factor: int = 3,
        # Training
        training: bool = False,
        brain_trainer=None,
    ):
        # Create wreck
        wreck = Wreck(wreck_probability)
        wreck.add_item(Bucket, bucket_amount)
        wreck.add_item(Axe, axe_amount)
        wreck.add_item(FishingRod, fishing_rod_amount)
        self._wreck = wreck

        # Create world
        self._world = World(
            wreck=wreck,
            initial_water_level=initial_water_level,
            initial_food_amount=initial_food_amount,
            initial_wood_amount=initial_wood_amount,
            basic_water_fetch_factor=basic_water_fetch_factor or [3, 4, 5],
            basic_wood_fetch_factor=basic_wood_fetch_factor or [3, 4, 5],
            basic_food_fetch_factor=basic_food_fetch_factor or [3, 4, 5],
            default_weather=default_weather,
        )

        # Create colony
        self.colony = Colony(
            world=self._world,
            amount_of_wood_per_player_to_leave=amount_of_wood_per_player_to_leave,
            amount_of_water_per_player_to_leave=amount_of_water_per_player_to_leave,
            amount_of_food_per_player_to_leave=amount_of_food_per_player_to_leave,
            initial_surviving_factor=initial_surviving_factor,
        )

        # Add players
        for i in range(0, number_of_players):
            self.colony.add_player(
                Player(
                    number=i,
                    colony=self.colony,
                    brain_location=brain_location,
                    training=training,
                    trainer=brain_trainer,
                )
            )

        # Initiate day counter
        self._day = 0

    @property
    def _game_over(self) -> bool:
        """The game is over iff every player is dead or gone"""
        return len(self.colony.alive_players) <= 0

    @property
    def current_day(self) -> int:
        return self._day

    def _update(self) -> DaySum:
        """This updates the game and make the _actions of a complete day, from dawn to dawn"""

        # Step zero, world update
        self._day += 1
        self._world.update()

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
                player_to_die.die(self.current_day)

        if not self._game_over:
            # Third step : Diner
            for _ in self.colony.dine():
                ...

            # Fourth step : Verify if there's enough resources to leave
            if self.colony.able_to_leave:
                for _ in self.colony.leave_isle():
                    ...

        return DaySum(
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
        days: List[DaySum] = []

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

    def run_single(self) -> Optional[DaySum]:
        """Runs a single day if game is not over
        returns the day summary
        """
        if self._game_over:
            return None
        return self._update()
