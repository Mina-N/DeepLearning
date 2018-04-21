from geometry.Point import *


class Segment:
    """
    :type s: Point
    :type e: Point
    :type next: Segment
    :type prev: Segment
    """
    __last_id = 0
    master_list = []

    @staticmethod
    def point_from_deg(x, y, seg_len, deg):
        x_sin = np.sin(np.deg2rad(deg))
        y_cos = np.cos(np.deg2rad(deg))

        if x < 0 and y > 0:  # Q2
            nx = seg_len * np.sin(np.deg2rad(deg)) + x
            ny = seg_len * np.cos(np.deg2rad(deg)) + y
        else:
            nx = seg_len * x_sin + x
            ny = seg_len * y_cos + y
        return nx, ny

    def __init__(self, *args, n=None, p=None, add=True, name=""):
        """
        Creates line segment object
        :rtype: Segment
        :type p: Segment
        :type n: Segment
        :param either (x1,y1), (x2,y2) or x1, y1, x2, y2
        """
        if len(args) < 2:
            raise ValueError("Invalid instancing")
        elif len(args) == 2:
            if not hasattr(args[0], "__getitem__") and hasattr(args[1], "__getitem__"):
                raise ValueError(
                    "Invalid instancing {} and/or {}".format(type(args[0]).__name__, type(args[1]).__name__))
            self.s = Point(*args[0])
            self.e = Point(*args[1])
        elif len(args) == 4:
            self.s = Point(args[0], args[1])
            self.e = Point(args[2], args[3])
        if n is not None and isinstance(n, Segment):
            self.next = n
        else:
            self.next = None
        if p is not None and isinstance(p, Segment):
            self.prev = p
        else:
            self.prev = None
        if self.s == self.e:
            raise ValueError("Start and end are the same point!")
        self.name = name
        self.id = Segment.__last_id
        Segment.__last_id += 1
        self.angle = None
        if add:
            Segment.master_list.append(self)

    def intersects(self, *args):
        """
        Returns intersection if exists otherwise false.
        Accepts either a Segment or two points.
        :rtype: Union[Point, Boolean]
        """

        if len(args) == 1 and isinstance(args[0], Segment):
            if args[0] is self:
                return False
            a = args[0]
        elif len(args) == 2:
            a = Segment(args[0], args[1], add=False)
        elif len(args) == 4:
            a = Segment(args[0], args[1], args[2], args[3], add=False)
        else:
            raise ValueError("Invalid argument to intersects")

        s1_x = self.e.x - self.s.x
        s1_y = self.e.y - self.s.y
        s2_x = a.e.x - a.s.x
        s2_y = a.e.y - a.s.y

        s = (-s1_y * (self.s.x - a.s.x) + s1_x * (self.s.y - a.s.y)) / (-s2_x * s1_y + s1_x * s2_y)
        t = (s2_x * (self.s.y - a.s.y) - s2_y * (self.s.x - a.s.x)) / (-s2_x * s1_y + s1_x * s2_y)

        if 0 <= s <= 1 and 0 <= t < 1:
            i_x = self.s.x + (t * s1_x)
            i_y = self.s.y + (t * s1_y)
            return Point(i_x, i_y)
        return False

    def get_length(self):
        return np.sqrt((self.e.x - self.s.x) ** 2 + (self.e.y - self.s.y) ** 2)

    def get_midpoint(self):
        return Point((self.e.x + self.s.x) / 2, (self.e.y + self.s.y) / 2)

    def distance_on_seg(self, dist):
        t = dist / self.get_length()
        t = np.clip(t, 0.0, 1.0)
        x, y = (1 - t) * self.s.x + t * self.e.x, (1 - t) * self.s.y + t * self.e.y
        return Point(x, y)

    def halve(self):
        self.split(self.get_midpoint())

    def halve_norm(self, err=0.1):
        if (not isinstance(self.e, Point)) and (not isinstance(self.s, Point)):
            ValueError("Start or End was not set to a Point!")
        m = self.get_midpoint()
        x, y = self.point_from_deg(m.x, m.y, err, 0)
        self.split(Point(x, y))

    def split(self, point):
        """
        Creates two segments with point as the common 'middle'
        :type point: Point
        """
        if not isinstance(point, Point):
            raise ValueError("Must be called with Point!")
        old_next = self.next
        self.next = Segment(point, self.e, n=old_next, p=self)
        self.e = point

    def closet_point(self, P):
        """
        Finds the closet point on this line to Point P.
        :param P: Point
        :return: Point closet point
        """
        A = self.s
        B = self.e
        a_to_p = [P.x - A.x, P.y - A.y]  # Storing vector A->P
        a_to_b = [B.x - A.x, B.y - A.y]  # Storing vector A->B

        atb2 = a_to_b[0] ** 2 + a_to_b[1] ** 2
        #   Basically finding the squared magnitude of a_to_b
        atp_dot_atb = a_to_p[0] * a_to_b[0] + a_to_p[1] * a_to_b[1]
        # The dot product of a_to_p and a_to_b
        t = atp_dot_atb / atb2  # The normalized "distance" from a to
        t = np.clip(t, 0, 1)
        return Point(A.x + a_to_b[0] * t, A.y + a_to_b[1] * t)

    def get_xs(self):
        return self.s.x, self.e.x

    def get_ys(self):
        return self.s.y, self.e.y

    def collect(self):
        return [(self.s.x, self.s.y), (self.e.x, self.e.y)]

    def back(self, count):
        """
        Goes back n segments 
        :param count: int
        :return: Segment
        """
        p = self
        for i in range(0, count):
            p = p.prev
        return p

    def forward(self, count):
        """
        Goes forward n segments
        :param count: int
        :return: Segment
        """
        p = self
        for i in range(0, count):
            p = p.next
        return p

    @staticmethod
    def link_all():
        for i in range(0, len(Segment.master_list) - 1):
            Segment.master_list[i].next = Segment.master_list[i + 1]

    def generate_angle(self):
        ab = self.prev.s - self.e
        self.angle = (np.rad2deg(np.arctan2(*ab)) + self.prev.angle) % 360
        self.angle = self.prev.angle

    def __str__(self):
        return "Segment<{}>([{:.2f} {:.2f}], [{:.2f} {:.2f}], {:.2f}, n={}, p={})".format(str(self.name), *self.s,
                                                                                          *self.e, self.get_length(),
                                                                                          str(self.next is not None),
                                                                                          str(self.prev is not None))

    def __getitem__(self, item):
        return self.s, self.e
