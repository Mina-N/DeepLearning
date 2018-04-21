import csv

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.animation import FuncAnimation, writers
import time, datetime
import pickle

from geometry.Segment import *

WALK_DISTANCE = 1.9
WALK_MAX_ANGLE = 16.5
WALK_MIN_ANGLE = -WALK_MAX_ANGLE

ANGLE_RANGE = 0.1
ANGLE_MIN = 1.0 - ANGLE_RANGE
EPSILON = 0.2

MAX_TRACK_WIDTH = 3.52
MIN_TRACK_WIDTH = 3.48
MIN_TRACK_LENGTH = 300
MAX_TRACK_LENGTH = 500

MAX_STRAIGHT = 80.0
MAX_TURN = 50.0


######################################################################
######################################################################


def _vec2d_dist(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def _vec2d_sub(p1, p2):
    return p1[0] - p2[0], p1[1] - p2[1]


def _vec2d_mult(p1, p2):
    return p1[0] * p2[0] + p1[1] * p2[1]


def ramerdouglas(line, dist):
    """Does Ramer-Douglas-Peucker simplification of a curve with `dist`
    threshold.

    `line` is a list-of-tuples, where each tuple is a 2D coordinate

    Usage is like so:

    >>> myline = [(0.0, 0.0), (1.0, 2.0), (2.0, 1.0)]
    >>> simplified = ramerdouglas(myline, dist = 1.0)
    """

    if len(line) < 3:
        return line

    (begin, end) = (line[0], line[-1]) if line[0] != line[-1] else (line[0], line[-2])

    distSq = []
    for curr in line[1:-1]:
        tmp = (
            _vec2d_dist(begin, curr) - _vec2d_mult(_vec2d_sub(end, begin),
                                                   _vec2d_sub(curr, begin)) ** 2 / _vec2d_dist(begin, end))
        distSq.append(tmp)

    maxdist = max(distSq)
    if maxdist < dist ** 2:
        return [begin, end]

    pos = distSq.index(maxdist)
    return ramerdouglas(line[:pos + 2], dist) + ramerdouglas(line[pos + 1:], dist)[1:]


######################################################################

current_update = None
current_state = None


def press(event):
    global current_update
    if event.key == 'enter':
        current_update = update(0)
        plt.show()
    if event.key == 'q':
        timestamp = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)
        pickle.dump(np.random.get_state(), open("states/{}.state".format(timestamp), 'wb'))
        r_x, r_y, l_x, l_y, rs_x, rs_y, ls_x, ls_y = current_update
        file_name = ["cone_loc.csv", "simplified_cone_loc.csv"]
        print("Saved", *file_name, ". Stamp:", str(timestamp))
        plt.savefig(str(timestamp) + '.png', bbox_inches='tight')
        with open(file_name[0], 'w', encoding='utf8', newline='') as f1:
            writer = csv.writer(f1)
            writer.writerow(["X", "Y", timestamp])
            for a, b in zip(r_x, r_y):
                writer.writerow([a, b])
            for a, b in zip(l_x, l_y):
                writer.writerow([a, b])

        with open(file_name[1], 'w', encoding='utf8', newline='') as f1:
            writer = csv.writer(f1)
            writer.writerow(["X", "Y", str(timestamp)])
            for a, b in zip(rs_x, rs_y):
                writer.writerow([a, b])
            for a, b in zip(ls_x, ls_y):
                writer.writerow([a, b])


fig = plt.figure(1)
fig.set_size_inches(13, 13)
fig.canvas.mpl_connect('key_press_event', press)
ax = plt.subplot()  # type: Axes

ax.set_aspect('equal', 'datalim')
ax.grid(b=True, which='major', color='#757575', linestyle='-')
ax.grid(b=True, which='minor', color='#d1d1d1', linestyle='--')


def segment_length(p1, p2):
    np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def point_from_deg(x, y, seg_len, deg):
    nx = x + seg_len * np.sin(np.deg2rad(deg))
    ny = y + seg_len * np.cos(np.deg2rad(deg))
    return nx, ny


def update(i):
    global current_state
    # np.random.seed(920129370)
    # np.random.seed()
    # np.random.set_state(pickle.load(open("states/1489307250.04022.state", "rb")))

    track_length = int(np.random.uniform(MIN_TRACK_LENGTH, MAX_TRACK_LENGTH))

    ax.clear()
    ax.text(0.55, 0.999, 'enter = next map',
            horizontalalignment='right',
            verticalalignment='top',
            transform=ax.transAxes)
    ax.text(0.55, 0.984, 'q = save files',
            horizontalalignment='right',
            verticalalignment='top',
            transform=ax.transAxes)

    s1 = Segment(9, 9, 0, 0)
    s2 = Segment(10, 0, 0, 10)
    print(s1.intersects(s2))
    print(s1.get_length(), s2.get_length())
    print(s1.get_midpoint())

    ax.plot([s1.s.x, s1.e.x, s2.s.x, s2.e.x], [s1.s.y, s1.e.y, s2.s.y, s2.e.y], '*-', color="gray", label="_none",
            lw=0.8, ms=8)

    plt.minorticks_on()
    ax.grid(b=True, which='major', color='#757575', linestyle='-')
    ax.grid(b=True, which='minor', color='#d1d1d1', linestyle='--')
    x_list = np.linspace(0, track_length, track_length)
    y_list = [0.0] * track_length
    deg = [0.0] * track_length

    r_x = [0.0] * track_length
    r_y = [0.0] * track_length
    l_x = [0.0] * track_length
    l_y = [0.0] * track_length

    rx_col = [0.0] * track_length
    lx_col = [0.0] * track_length
    ry_col = [0.0] * track_length
    ly_col = [0.0] * track_length

    lines = []
    rlines = []  # type: list(Segment)
    llines = []  # type: list(Segment)

    col_list_x = []
    col_list_y = []

    new_theta = 0
    for i in range(0, len(x_list)):
        # print(i)
        theta = np.random.uniform(WALK_MIN_ANGLE, WALK_MAX_ANGLE)
        width = np.random.uniform(MIN_TRACK_WIDTH, MAX_TRACK_WIDTH)
        if i != 0:
            norm_ang = abs((theta - WALK_MIN_ANGLE) / (WALK_MAX_ANGLE - WALK_MIN_ANGLE) * ANGLE_RANGE + ANGLE_MIN)
            new_theta = deg[i - 1] + theta
            if new_theta >= 360:
                new_theta -= 360
            deg[i] = new_theta
            x_list[i], y_list[i] = point_from_deg(x_list[i - 1], y_list[i - 1], WALK_DISTANCE * norm_ang, new_theta)

        if i >= 1:
            lines.append(Segment(rx_col[i], ry_col[i], rx_col[i - 1], ry_col[i - 1]))
            lines.append(Segment(lx_col[i], ly_col[i], lx_col[i - 1], ly_col[i - 1]))

        r_x[i], r_y[i] = point_from_deg(x_list[i], y_list[i], width / 2, new_theta - 90)
        l_x[i], l_y[i] = point_from_deg(x_list[i], y_list[i], width / 2, new_theta + 90)
        if i != 0:
            rlines.append(Segment(r_x[i - 1], r_y[i - 1], r_x[i], r_y[i]))
            llines.append(Segment(l_x[i - 1], l_y[i - 1], l_x[i], l_y[i]))
            if i > 1 and len(rlines) > 1:
                rlines[i - 1].prev = rlines[i - 2]
                llines[i - 1].prev = llines[i - 2]

        rx_col[i], ry_col[i] = point_from_deg(x_list[i], y_list[i], width * 2.4, new_theta - 90)
        lx_col[i], ly_col[i] = point_from_deg(x_list[i], y_list[i], width * 2.4, new_theta + 90)
        # s = str.format(u"{0} ({1:-.2f}\u00b0)", i, new_theta)
        # ax.annotate(s, xy=(x[i], y[i]), xycoords='data', xytext=(2.5, 0.5), textcoords='offset points')

        if i > 2 and len(rlines) <= i:
            for l in lines:  # type: Segment
                r1 = l.intersects(rlines[i - 1])
                r2 = l.intersects(llines[i - 1])
                if r1:
                    col_list_x.append(r1[0])
                    col_list_y.append(r1[1])
                    # ax.annotate(str.format("{0:-.2f} {1:-.2f}", r1[0], r1[1]), xy=(r1[0], r1[1]), xycoords='data',
                    #             xytext=(2.5, 0.5), textcoords='offset points')
                if r2:
                    col_list_x.append(r2[0])
                    col_list_y.append(r2[1])
                    # ax.annotate(str.format("{0:-.2f} {1:-.2f}", r2[0], r2[1]), xy=(r2[0], r2[1]), xycoords='data',
                    #             xytext=(2.5, 0.5), textcoords='offset points')

    tlen = 0.0
    r = rlines[-1]  # type: Segment
    while r is not None:
        tl = r.get_length()
        if tl > 5.0:
            print(r.id, "was to long!")
        tlen += tl
        r = r.prev

    print("rlen", tlen)
    tlen = 0.0
    r = llines[-1]  # type: Segment
    while r is not None:
        tl = r.get_length()
        if tl > 5.0:
            print(r.id, "was to long!")
        tlen += tl
        r = r.prev

    print("llen", tlen)

    ax.plot(x_list, y_list, '.-', label="Centerline", lw=0.8, ms=4)

    rs_x, rs_y = zip(*ramerdouglas(list(zip(r_x, r_y)), EPSILON))
    ls_x, ls_y = zip(*ramerdouglas(list(zip(l_x, l_y)), EPSILON))
    ax.plot(rs_x, rs_y, '.--', lw=0.5, color='green', label="Simplified R Cones")
    ax.plot(ls_x, ls_y, '.--', lw=0.5, color='darkred', label="Simplified L Cones")

    ax.plot(r_x, r_y, '4-', color='lime', alpha=0.3, label="R Cones")
    ax.plot(l_x, l_y, '4-', color='red', alpha=0.3, label="L Cones")

    ax.plot(*zip(*ramerdouglas(list(zip(rx_col, ry_col)), 0.08)), '--', lw=0.9, ms=4, color='gold',
            label="_Collision 1")
    ax.plot(*zip(*ramerdouglas(list(zip(lx_col, ly_col)), 0.08)), '--', lw=0.9, ms=4, color='gold',
            label="_Collision 2")

    ax.plot(col_list_x, col_list_y, 'x', color="magenta", label="_none", lw=0.8, ms=8)

    ax.legend(fontsize=14.5)

    current_state = np.random.get_state()
    return r_x, r_y, l_x, l_y, rs_x, rs_y, ls_x, ls_y


plt.tight_layout()

# anim = FuncAnimation(fig, update, interval=100, repeat=False, frames=np.arange(0, 100, 1))
update(1)

# anim.save('paths.mp4', codec='libx264', fps=30)
# print("done saving!")

plt.show()
