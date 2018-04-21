from geometry.Point import Point


class Line:
    """
    :type s: Point
    :type e: Point
    """

    def __init__(self, *args):
        if len(args) == 2:
            self.s = args[0]
            self.e = args[1]
        elif len(args) == 4:
            self.s = Point(args[0], args[1])
            self.e = Point(args[2], args[3])

    def m(self):
        return self.slope()

    def slope(self):
        """
        Slope between two points
        :return: float
        """
        return (self.s.y - self.e.y) / (self.s.x - self.e.x)

    def b(self):
        return self.s.y - self.slope() * self.s.x

    def __str__(self):
        return "Line({}, {}): y={:.3f}x{:+.3f}" \
            .format(self.s, self.e, self.m(), self.b())

    def make_perpendicular(self, point):
        # k = ((y2 - y1) * (x3 - x1) - (x2 - x1) * (y3 - y1)) / ((y2 - y1) ^ 2 + (x2 - x1) ^ 2)
        # x4 = x3 - k * (y2 - y1)
        # y4 = y3 + k * (x2 - x1)
        """
        :type point: Point
        """
        k = ((self.e.y - self.s.y) * (point.x - self.s.x) - (self.e.x - self.s.x) * (point.y - self.s.y)) / \
            ((self.e.y - self.s.y) ** 2 + (self.e.x - self.s.x) ** 2)
        r = Point(point.x - k * (self.e.y - self.s.y), point.y - k * (self.e.x - self.s.x))
        return Line(point, r)
