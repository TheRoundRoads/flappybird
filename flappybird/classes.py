class Bird:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = 0

    def jump(self, height):
        self.velocity = -height


class Pipe:
    def __init__(self, x, y, width, height, below):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.below = below
        self.check = False


class PipePair:
    def __init__(self, top, bottom, distance):
        self.top = top
        self.bottom = bottom
        self.distance = distance