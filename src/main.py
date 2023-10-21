from models.colony import Colony
from models.player import Player


def main():
    colony = Colony()
    player_6 = Player(6, colony)
    print(colony, player_6)

    player_6.make_action(2)

    print(colony, player_6)


if __name__ == "__main__":
    main()
