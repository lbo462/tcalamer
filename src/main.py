from settings import number_of_player, wreck_probability
from game_engine import GameEngine


def main():
    ge = GameEngine(
        number_of_players=number_of_player,
        wreck_probability=wreck_probability,
    )

    summary = ge.run()
    print(summary.model_dump_json())


if __name__ == "__main__":
    main()
