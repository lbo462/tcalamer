from settings import number_of_player, wreck_probability
from game_engine import GameEngine


def main():
    ge = GameEngine(
        number_of_players=number_of_player,
        wreck_probability=wreck_probability,
    )

    while not ge.game_over:
        for log in ge.update():
            print(f". {log}")
        print("\n")


if __name__ == "__main__":
    main()
