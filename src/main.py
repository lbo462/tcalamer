from models.colony import Colony
from models.player import Player


def main():
    colony = Colony()
    player_6 = Player(6, colony)
    print(colony, player_6)

    player_6.search_wreck()
    print(colony, player_6)

    player_6.search_wreck()
    print(colony, player_6)

    player_6.search_wreck()
    print(colony, player_6)

    player_6.search_wreck()
    print(colony, player_6)

    player_6.search_wreck()
    print(colony, player_6)

    player_6.search_wreck()
    print(colony, player_6)

    player_6.fetch_water()
    player_6.fetch_wood()
    player_6.fetch_food()

    print(colony, player_6)


if __name__ == "__main__":
    main()
