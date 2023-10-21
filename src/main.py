from models.colony import Colony
from models.player import Player


def main():
    colony = Colony()
    player = Player(6, colony)

    print(colony, player)

    player.fetch_water()
    player.search_wreck()
    player.fetch_wood()

    print(colony, player)


if __name__ == "__main__":
    main()
