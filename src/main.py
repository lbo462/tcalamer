from colony import Colony
from player import Player


def main():
    colony = Colony()
    player_6 = Player(6, colony)
    print(colony, player_6)

    player_6.make_random_daily_action()

    print(colony, player_6)


if __name__ == "__main__":
    main()
