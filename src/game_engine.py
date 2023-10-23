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
    It creates a colony and players in it.
    It defines the different steps of the game
    """

    def __init__(self, number_of_players: int, wreck_probability: float):
        # Create wreck
        wreck = Wreck(wreck_probability)
        wreck.add_item(Bucket, 1)
        wreck.add_item(Axe, 1)
        wreck.add_item(FishingRod, 1)

        # Create world
        self.world = World(wreck)

        # Create colony
        self.colony = Colony(self.world)

        # Add players
        self.players = []
        for i in range(0, number_of_players):
            self.players.append(Player(i, self.colony))
            # Add a basic resource for each player
            self.colony.add_water(2)
            self.colony.add_wood(2)
            self.colony.add_food(2)

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

    @property
    def in_game_order_at_random(self) -> List[Player]:
        """Returns the shuffled list of available players in the game"""
        players = []
        for player in self.in_game_players:
            players.append(player)
        random.shuffle(players)
        return players

    @property
    def alive_players(self) -> int:
        return len(self.in_game_order_at_random)

    @property
    def summary(self) -> str:
        return (
            f"World : {self.world}, Colony : {self.colony}, "
            f"Number of players alive on the isle : {len(self.in_game_order_at_random)}"
        )

    @property
    def able_to_leave(self) -> bool:
        """Returns the possibility for the colony to leave"""
        return (
            self.colony.wood_amount >= self.alive_players * 5
            and self.colony.food_amount >= self.alive_players
            and self.colony.water_level >= self.alive_players
        )

    def update(self) -> Generator:
        """This updates the game and make the actions of a complete day, from dawn to dawn"""

        yield "THE DAY STARTS"

        # Step zero
        self.world.update()
        yield f"Weather of the day : {self.world.weather.name}"
        yield f"World resources : {self.world}"

        # First step : daily actions
        yield "EVERY ONE WORK"
        for player in self.in_game_order_at_random:
            for log in player.make_random_daily_action():
                yield log

        yield f"--- NIGHT FALLS, COLONY RESOURCES : {self.colony}"

        # Second step : Food and water count
        enough_food = self.colony.food_amount >= self.alive_players
        enough_water = self.colony.water_level >= self.alive_players
        yield f"Enough food : {enough_food}, Enough water : {enough_water}"

        # Second - bis step : Vote for the players to die
        if not enough_water or not enough_food:
            limiting_factor = min(self.colony.water_level, self.colony.food_amount)
            amount_of_players_to_die = self.alive_players - limiting_factor
            yield f"{amount_of_players_to_die} players must die."
            # TODO vote system
            for i in range(0, amount_of_players_to_die):
                player_to_die: Player = random.choice(self.in_game_order_at_random)
                yield f"{player_to_die} was chosen to die"
                player_to_die.die()

        # Third step : Eat and drink
        for player in self.in_game_players:
            player.eat_and_drink()

        # Fourth step : Verify if there's enough resources to leave
        if self.able_to_leave and not self.game_over:
            number_of_winners = self.alive_players
            for player in self.in_game_players:
                yield f"{player} took the raft and left"
                player.flee()
            yield f"{number_of_winners} PLAYERS ESCAPED"
        else:
            # Day summary
            yield self.summary

            yield "--------- THE NEXT DAY ------------"
