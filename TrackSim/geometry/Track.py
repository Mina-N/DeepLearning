import copy

from numpy.linalg import inv
from scipy.interpolate import interp1d

from geometry.Curve import *


class Track:
    """
    :type p: list[Point]
    :type segs: list[Segment]
    :type smoothed: list[Segment]
    """

    ITERATIONS = 3

    def __init__(self):
        self.p = []
        self.segs = []
        self.smoothed = []
        self.sm_l = []
        self.s_id_list = []
        self.ano_angles = []
        self.poly = []
        self.last_random = 8 ** 2

    @staticmethod
    def check_links(data):
        for idx, r in enumerate(data):
            if not isinstance(r, Segment):
                continue
            if r.next is None and r.prev is None:
                print(idx, ' * ', r, '<- No Link!')
            else:
                if r.next is None:
                    print(idx, '** ', r, '<- Broken Next!')
                if r.prev is None:
                    print(idx, ' **', r, '<- Broken Previous!')
            if r.next.s == r.e:
                r.next.s = r.e
            if r.prev.e == r.s:
                r.prev.e = r.s

    def first_pass(self):
        self.p.append(Point(-40, -60))
        self.p.append(Point(30, -30))
        self.p.append(Point(60, 10))
        self.p.append(Point(10, 60))
        self.p.append(Point(-60, 20))

    def get_random(self):
        self.last_random = np.log(self.last_random ** 2)
        return self.last_random

    def second_pass(self, iterations=ITERATIONS):
        start = None  # type: Segment
        end = None  # type: Segment
        assert len(self.p) > 2, "Not enough track hint points"
        for i in range(0, len(self.p) - 1):
            if start is None and end is None:
                s = Segment(self.p[0], self.p[1], name="SEED0")
                start = s
                end = s
            elif start is end:
                s = Segment(end.e, self.p[i + 1], p=start, name="SEED")
                start.next = s
                end = s
            elif start is not end:
                s = Segment(end.e, self.p[i + 1], p=end, name="SEED")
                end.next = s
                end = s
            else:
                raise AssertionError("Closed segment creation error (!)")
            self.segs.append(s)
        s2 = Segment(end.e, self.p[0], n=start, p=end, name="SEEDE")
        end.next = s2
        start.prev = s2
        self.segs.append(s2)

        for s in self.segs:
            print(s)
        # iterate x times to split segments into smaller segments with
        # successively smaller random angles
        for s in range(0, iterations):
            rr = np.clip(self.get_random(), 0.001, 50 ** 2)

            lol = copy.copy(Segment.master_list)
            for sl in lol:  # type: Segment
                # sl.halve_norm(np.random.triangular(-0.7, 0, 0.7))
                sl.halve_norm(np.random.normal(0, rr))

        s = Segment.master_list[0]  # type: Segment
        new_points = []  # :type p: list[Point]
        die_next = False
        while s is not None:
            new_points.append(s.s)
            s = s.next
            if die_next: break
            if s is not None and s.next is Segment.master_list[0]:
                die_next = True
        del s
        self.p = new_points
        return Segment.master_list

    def third_pass(self):
        starts = []  # type: list[Segment]
        ends = []  # type: list[Segment]
        for x in range(0, len(self.p) - 1):
            if len(ends) > 0:
                c = Curve(ends[-1].e)
            else:
                c = Curve(self.p[x])
            start, end = c.turn_toward(self.p[x + 1], x)
            starts.append(start)
            ends.append(end)
            # print(euclidean([*end.e], [*starts[0].s]))
            # print('start', start, 'end', end)
            if x > 0:
                starts[x].prev = ends[x - 1]
                ends[x - 1].next = starts[x]

        # make closed
        c = Curve(ends[-1].e)
        start, end = c.turn_toward(self.p[0], len(self.p))
        starts.append(start)
        ends.append(end)
        starts[len(self.p) - 1].prev = ends[len(self.p) - 2]
        ends[len(self.p) - 2].next = starts[len(self.p) - 1]
        ends[-1].next = starts[0]
        starts[0].prev = ends[-1]
        # final step - smooth
        # self.smooth()  # uncomment me

    def smooth(self):
        p = Segment.master_list[0]  # type: Segment
        start_id = Segment.master_list[0].id
        end_id = Segment.master_list[-1].id
        new_begin = None
        while p is not None:
            abs_a = np.abs(p.prev.angle - p.angle)
            if abs_a > Curve.WALK_MAX_ANGLE:  # 19
                new_ang = self.average_bearing(p.prev.angle, p.angle)
                start = 0
                end = 4
                if abs_a > Curve.WALK_MAX_ANGLE * 3.5:
                    end = 11
                elif abs_a > Curve.WALK_MAX_ANGLE * 3:
                    end = 9
                elif abs_a > Curve.WALK_MAX_ANGLE * 2.4:
                    end = 8
                elif abs_a > Curve.WALK_MAX_ANGLE * 1.8:
                    end = 6
                elif abs_a > Curve.WALK_MAX_ANGLE * 1.2:
                    end = 5
                else:
                    end = 3

                s_new_begin = None
                s_new_index = -1
                fix_s = p
                for i in range(0, end):
                    if Segment.master_list[0] == fix_s:
                        s_new_begin = Segment.master_list[0]
                        s_new_index = i
                    fix_s = fix_s.prev

                e_new_begin = None
                e_new_index = -1
                fix_e = p
                for i in range(0, end):
                    if Segment.master_list[0] == fix_e:
                        e_new_begin = Segment.master_list[0]
                        e_new_index = i
                    fix_e = fix_e.next

                dir_angle = np.rad2deg(np.arctan2(*fix_e.s - fix_s.e))
                # print('Too sharp:', p.id, 'average:', new_ang, 'diff:', abs_a)
                self.ano_angles.append([p.s, "{:.2f}$\degree$".format(abs_a)])
                # x, y = Curve.point_from_deg(*p.s, (p.get_length()) / 2, dir_angle)
                gray_line = Segment(fix_s.e, fix_e.s, add=False)
                self.s_id_list.append(fix_s.id)
                self.s_id_list.append(fix_e.id)
                try:
                    mid = Segment(gray_line.closet_point(p.s), p.s, add=False)
                except ValueError:
                    p = p.next
                    if p is Segment.master_list[0] or p.id == start_id:
                        break
                    continue

                theta = np.arctan2(gray_line.e.y - gray_line.s.y, gray_line.e.x - gray_line.s.x)
                R = np.matrix([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
                x = np.matrix([fix_s.e.x, mid.get_midpoint().x, fix_e.s.x]).transpose()
                y = np.matrix([fix_s.e.y, mid.get_midpoint().y, fix_e.s.y]).transpose()

                v = np.concatenate((x, y), axis=1)
                # print('R', R, 'X', x, 'Y', y, 'V', v, '\n')
                ret = v * R
                x = ret[:, 0].squeeze().tolist()[0]
                y = ret[:, 1].squeeze().tolist()[0]
                # print(ret, 'x', x, 'y', y, '\n')

                f2 = interp1d(list(x), list(y), kind=2, bounds_error=False, assume_sorted=False)
                x_new = np.matrix(np.linspace(x[0], x[-1], 10))
                y_new = np.matrix(f2(x_new))

                v = np.concatenate((x_new.transpose(), y_new.transpose()), axis=1)
                # print(v.item(0, 0), v.item(0, 1), v.shape[0])
                curve = []  # type: list[Segment]
                back = v * inv(R)
                x = back[:, 0].squeeze().tolist()[0]
                y = back[:, 1].squeeze().tolist()[0]

                self.poly.append((x, y))

                old_begin = e_new_begin or s_new_begin

                for i in range(len(back) - 1):
                    x1, y1 = x[i], y[i]
                    x2, y2 = x[i + 1], y[i + 1]
                    s = Segment(x1, y1, x2, y2, add=False)
                    curve.append(s)

                    if i == e_new_index or i == s_new_index:
                        Segment.master_list[0] = s

                    if i > 0:
                        curve[i - 1].next = curve[i]
                        curve[i].prev = curve[i - 1]

                fix_s.next = curve[0]
                curve[0].prev = fix_s

                fix_e.prev = curve[-1]
                curve[-1].next = fix_e

                # trying to fix angles
                # if not ((curve[0].prev.angle < 0 and curve[-1].next.angle < 0) or
                #         (curve[0].prev.angle > 0 and curve[-1].next.angle > 0)):
                #
                #     # angles = np.linspace(curve[0].prev.angle, curve[-1].next.angle, len(curve))
                #
                #     angles = [0.0] * len(curve)
                #     if curve[-1].next.angle > 0:
                #
                #         change_per = (180 - curve[0].prev.angle + curve[-1].next.angle + 180)
                #         change_per /= len(angles) - 1
                #
                #         angles[0] = curve[0].prev.angle
                #         angles[-1] = curve[-1].next.angle
                #         for ii in range(1, len(curve)):
                #             angles[ii] = angles[ii - 1] + change_per
                #             if angles[ii] >= 180:
                #                 angles[ii] -= 360
                #     else:
                #         angles = np.linspace(curve[0].prev.angle, curve[-1].next.angle, len(curve))
                #
                #     print('swapped', angles)
                #
                # else:
                angles = np.linspace(curve[0].prev.angle, curve[-1].next.angle, len(curve))

                for i in range(len(back) - 1):
                    curve[i].angle = angles[i]

                self.smoothed.append(gray_line)
            p = p.next
            if p is Segment.master_list[0]:
                break
        del p

    @staticmethod
    def average_bearing(a, b):
        """
        :param a: float
        :param b: float
        :return: 
        """
        if a > b:
            temp = a
            a = b
            b = temp

        if b - a > 180:
            b -= 360
        final_bearing = (b + a) / 2

        # if final_bearing < 0:
        #     final_bearing += 360

        return final_bearing
