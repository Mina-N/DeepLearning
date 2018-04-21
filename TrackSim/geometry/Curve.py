from scipy.spatial.distance import euclidean

from geometry.Segment import *


class Curve:
    """
    :type s: Point
    :type last_seg: Segment
    """
    WALK_DISTANCE = 0.65
    WALK_RANDOM_ANGLE = 1.55
    WALK_MAX_ANGLE = 12.0
    WALK_MIN_ANGLE = -WALK_MAX_ANGLE

    ANGLE_RANGE = 0.1
    ANGLE_MIN = 1.0 - ANGLE_RANGE
    EPSILON = 0.1

    DESIRED_WIDTH = 7
    MAX_TRACK_WIDTH = DESIRED_WIDTH + DESIRED_WIDTH * 0.02
    MIN_TRACK_WIDTH = DESIRED_WIDTH - DESIRED_WIDTH * 0.02
    MIN_TRACK_LENGTH = 300
    MAX_TRACK_LENGTH = 500

    MAX_STRAIGHT = 80.0
    MAX_TURN = 50.0

    MAX_SEGMENTS = 150

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Point):
            self.start_point = args[0]
        else:
            self.start_point = Point(0, 0)

        self.end = None
        self.start = None

    def __str__(self):
        return "Curve([{:.2f} {:.2f}], [{:.2f} {:.2f}])".format(*self.start, *self.end)

    @staticmethod
    def point_from_deg(x, y, seg_len, deg):
        """

        :param x: float
        :param y: float
        :param seg_len: float
        :param deg: float
        :return:
        """
        nx = x + seg_len * np.sin(np.deg2rad(deg))
        ny = y + seg_len * np.cos(np.deg2rad(deg))
        return nx, ny

    def turn_toward(self, point, count):
        dist = euclidean([*self.start_point], [*point])
        last_dist = dist
        counter = 0
        cont = True
        while cont:
            if dist <= last_dist:
                if self.start is None and self.end is None:
                    new_ang = np.rad2deg(np.arctan2(*point - self.start_point))
                    s = self.next_seg(self.start_point, new_ang, new_ang, count)
                    self.end = s
                    self.start = s
                    dist = euclidean([*self.end.e], [*point])
                elif self.start is self.end:
                    s = self.next_seg(self.end.e, np.rad2deg(np.arctan2(*point - self.end.e)), self.end.angle, count)
                    self.start.next = s
                    s.prev = self.start
                    self.end = s
                elif self.start is not self.end:
                    s = self.next_seg(self.end.e, np.rad2deg(np.arctan2(*point - self.end.e)), self.end.angle, count)
                    self.end.next = s
                    s.prev = self.end
                    self.end = s
            else:
                cont = False
                if self.end.prev is not None:
                    self.end.prev.next = None
                    self.end = self.end.prev
                    Segment.master_list.remove(s)
            last_dist = dist
            dist = euclidean([*self.end.e], [*point])
            counter += 1
            if counter >= Curve.MAX_SEGMENTS:
                break
        return self.start, self.end

    @staticmethod
    def next_seg(pt0, ang, last_ang, count):
        """
        Generates the next segment based on previous ones
        :param last_ang: float last angle in degrees
        :type pt0: Point
        :type count: int
        :type ang: float angle in degrees
        :rtype: Segment
        """
        theta = np.random.uniform(0, Curve.WALK_RANDOM_ANGLE)
        norm_ang = abs((theta - Curve.WALK_MIN_ANGLE) /
                       (Curve.WALK_MAX_ANGLE - Curve.WALK_MIN_ANGLE) * Curve.ANGLE_RANGE + Curve.ANGLE_MIN)
        theta = norm_ang + theta + ang
        # new_theta = np.clip(theta, last_ang + Curve.WALK_MIN_ANGLE, last_ang + Curve.WALK_MAX_ANGLE)
        # print('[{}] last: {:+6.2f}\tbefore: {:+6.2f}\t\tCLIPPED: {:+6.2f}'.format(count, last_ang, theta, new_theta))
        x, y = Curve.point_from_deg(*pt0, Curve.WALK_DISTANCE * norm_ang, theta)
        # print(u"{:.3f} {:.3f} {:.2f}\u00b0".format(x, y, deg))
        ret = Segment(pt0.x, pt0.y, x, y, name=count)
        ret.angle = theta
        return ret
