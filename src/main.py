from game_engine import GameEngine


def main():
    ge = GameEngine(
        number_of_players=50,
        wreck_probability=0.5,
    )

    while not ge.game_over:
        for log in ge.update():
            print(log)


if __name__ == "__main__":
    main()
