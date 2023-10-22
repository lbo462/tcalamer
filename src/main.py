from game_engine import GameEngine


def main():
    ge = GameEngine(number_of_players=10)

    while not ge.game_over:
        for log in ge.update():
            print(log)

        print("------------ THE NEXT DAY -------------")


if __name__ == "__main__":
    main()
