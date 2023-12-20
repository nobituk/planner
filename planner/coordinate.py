class Coordinate:
    """座標"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy

    def __str__(self):
        return str((self.x, self.y))

    def __repr__(self):
        return "Coordinate({}, {})".format(self.x, self.y)
