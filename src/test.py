from settings import number_of_player, wreck_probability
from game_engine import GameEngine

number_of_games = 1000

def main():
    wins = 0
    for _ in range(number_of_games):
        ge = GameEngine(
            number_of_players=number_of_player,
            wreck_probability=wreck_probability,
        )

        while not ge.game_over:
            for _ in ge.update():
                ...

        if ge.colony.at_least_one_left_the_isle:
                wins += 1
    print(f"Win ratio : {100 * wins / number_of_games} %")


if __name__ == "__main__":
    main()