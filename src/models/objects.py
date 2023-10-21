class Object:
    """"""

    def use(self):
        """"""

    def __str__(self):
        return self.__class__.__name__


class Bucket(Object):
    def use(self) -> int:
        return 1


class Axe(Object):
    def use(self) -> int:
        return 1


class FishingRod(Object):
    def use(self) -> int:
        return 1
