from typing import List, Optional, Any
from pydantic import BaseModel as PBaseModel, FilePath

from .wreck import Wreck, WreckSum
from .world import World, WorldSum, Weather
from .colony import Colony, ColonySum
from .player import Player, _daily_actions
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


class GameEngineParams(PBaseModel):
    number_of_players: int = 22
    print_game: bool = False
    # Wreck
    wreck_probability: Optional[float] = 0.5
    bucket_amount: Optional[int] = 1
    axe_amount: Optional[int] = 1
    fishing_rod_amount: Optional[int] = 1
    # World
    initial_water_level: Optional[int] = 5000
    initial_food_amount: Optional[int] = 5000
    initial_wood_amount: Optional[int] = 5000
    basic_water_fetch_factor: Optional[List[int]] = None
    basic_wood_fetch_factor: Optional[List[int]] = None
    basic_food_fetch_factor: Optional[List[int]] = None
    default_weather: Optional[Weather] = Weather.BLUE_SKY
    # Colony
    amount_of_wood_per_player_to_leave: Optional[int] = 5
    amount_of_water_per_player_to_leave: Optional[int] = 1
    amount_of_food_per_player_to_leave: Optional[int] = 1
    initial_food_surviving_factor: Optional[int] = 2
    initial_water_surviving_factor: Optional[int] = 2
    # Training options
    brain_location: Optional[FilePath] = "brains/trained_q_network.pth"
    training: bool = False
    brain_trainer: Optional[Any] = None


class GameEngine:
    """
    The GameEngine drives the whole game.
    It creates a _colony and players in it.
    It defines the different steps of the game
    """

    def __init__(self, ge_params: GameEngineParams):
        self._print_game = ge_params.print_game

        # Create wreck
        wreck = Wreck(ge_params.wreck_probability)
        wreck.add_item(Bucket, ge_params.bucket_amount)
        wreck.add_item(Axe, ge_params.axe_amount)
        wreck.add_item(FishingRod, ge_params.fishing_rod_amount)
        self._wreck = wreck

        # Create world
        self._world = World(
            wreck=wreck,
            initial_water_level=ge_params.initial_water_level,
            initial_food_amount=ge_params.initial_food_amount,
            initial_wood_amount=ge_params.initial_wood_amount,
            basic_water_fetch_factor=ge_params.basic_water_fetch_factor or [1, 2, 3],
            basic_wood_fetch_factor=ge_params.basic_wood_fetch_factor or [1, 2, 3],
            basic_food_fetch_factor=ge_params.basic_food_fetch_factor or [1, 2, 3],
            default_weather=ge_params.default_weather,
        )

        # Create colony
        self.colony = Colony(
            world=self._world,
            amount_of_wood_per_player_to_leave=ge_params.amount_of_wood_per_player_to_leave,
            amount_of_water_per_player_to_leave=ge_params.amount_of_water_per_player_to_leave,
            amount_of_food_per_player_to_leave=ge_params.amount_of_food_per_player_to_leave,
            initial_food_surviving_factor=ge_params.initial_food_surviving_factor,
            initial_water_surviving_factor=ge_params.initial_water_surviving_factor,
        )

        # Add players
        for i in range(0, ge_params.number_of_players):
            self.colony.add_player(
                Player(
                    number=i,
                    colony=self.colony,
                    brain_location=ge_params.brain_location,
                    training=ge_params.training,
                    trainer=ge_params.brain_trainer,
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

        if self._print_game:
            print(
                f"/ --- DAWN OF DAY #{self._day} ({self._world.weather.name})\n"
                f"| World : {self._world}\n"
                f"| Colony : {self.colony}\n"
                f"\\ ---"
            )

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
            if self._print_game:
                print(f"{player} {_daily_actions.get_func(action_id).__name__}")

        # Second step : Some must die
        if not self.colony.enough_resources:
            limiting_factor = self.colony.limiting_factor
            amount_of_players_to_die = len(self.colony.alive_players) - limiting_factor

            for i in range(0, amount_of_players_to_die):
                player_to_die = self.colony.get_random_alive_player()
                player_to_die.die(self.current_day)
                if self._print_game:
                    print(f"{player_to_die} died")

        if not self._game_over:
            # Third step : Diner
            for _ in self.colony.dine():
                ...

            # Fourth step : Verify if there's enough resources to leave
            if self.colony.able_to_leave:
                for player in self.colony.leave_isle():
                    if self._print_game:
                        print(f"{player} leave !")

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

        print(f"{'✔️ victory' if self.colony.at_least_one_left_the_isle else '❌ defeat'} ({self.current_day} days)")

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
