import numpy as np


class Point:
    def __init__(self, x, y):
        if isinstance(x, Point) or isinstance(y, Point):
            raise ValueError("Nested points don't make sense!")
        if not (np.isfinite(x) and np.isfinite(y)):
            raise ValueError("This is a real point, I need real numbers ({}, {})!".format(x, y))
        self.x = x
        self.y = y

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError("This only has a x and y!")

    def __iter__(self):
        yield self.x
        yield self.y

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __str__(self):
        return "Point({:.2f}, {:.2f})".format(self.x, self.y)

    def __eq__(self, other):
        # if not isinstance(other, self.__class__):
        #     return False
        return np.isclose(self.x, other.x, rtol=1.e-8) and np.isclose(self.y, other.y, rtol=1.e-8)

    def __ne__(self, other):
        return not self.__eq__(other)
