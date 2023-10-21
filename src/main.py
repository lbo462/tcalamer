from models.colony import Colony
from models.player import Player


def main():
    colony = Colony()
    player_1 = Player(1, colony)
    player_6 = Player(6, colony)

    print(colony, player_1, player_6)

    player_1.fetch_water()

    player_6.search_wreck()
    player_6.fetch_wood()

    print(colony, player_1, player_6)


if __name__ == "__main__":
    main()
