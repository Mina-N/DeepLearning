from uuid import uuid4

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import collections as mc
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes

from TrackGen import ramerdouglas
from geometry.Curve import Curve
from geometry.Segment import *
from geometry.Track import Track

######################################################################
######################################################################


fig = plt.figure(1)
fig.set_size_inches(12, 12)
# plt.get_current_fig_manager().window.wm_geometry("+0+0")

ax = plt.subplot()  # type: Axes
collisions = 0
paused = True
play_once = False


def press(event):
    global paused, play_once
    if event.key == 'enter':
        play_once = True
        while not update(1):
            pass
        plt.show()
    if event.key == ' ':  # so retarded
        paused = not paused


fig.canvas.mpl_connect('key_press_event', press)


# np.random.seed(209)

def update(i):
    global collisions, play_once
    if paused:
        if play_once:
            play_once = False
        else:
            return
    Segment.master_list = []
    ax.clear()
    track = Track()
    track.first_pass()
    xpog = []
    ypog = []
    for i, p in enumerate(track.p):
        xpog.append(p.x)
        ypog.append(p.y)
        # lime green star numbers
        # ax.annotate("{}, {}".format(p.x, p.y), xy=(p.x, p.y),
        #             xycoords='data',
        #             xytext=(22, 22),
        #             color='lime',
        #             size=10,
        #             textcoords='offset points')
    ax.set_aspect('equal', 'datalim')

    segments = track.second_pass()
    xp = []
    yp = []
    for i, p in enumerate(track.p):
        xp.append(p.x)
        yp.append(p.y)
        # diamond numbers
        # ax.annotate(i, xy=(p.x, p.y),
        #             xycoords='data',
        #             color='orange',
        #             xytext=(-10.5, -10.5),
        #             textcoords='offset points')
    ax.set_aspect('equal', 'datalim')
    ax.grid(b=True, which='major', color='#757575', linestyle='-')
    ax.grid(b=True, which='minor', color='#d1d1d1', linestyle='--')

    # t = ax.text(0.55, 0.984, '',
    #             horizontalalignment='right',
    #             verticalalignment='top',
    #             transform=ax.transAxes)
    #
    # for s in range(0, 3):
    #     rr = np.clip(track.get_random(), 0.001, 50 ** 2)
    #     t.set_text("{1:} $\epsilon={0:.2f}$".format(rr, t.get_text()))
    #     lol = copy.copy(Segment.master_list)
    #     for sl in lol:  # type: Segment
    #         # sl.halve_norm(np.random.triangular(-0.7, 0, 0.7))
    #         sl.halve_norm(np.random.normal(0, rr))

    col_list_x = []
    col_list_y = []
    for ii in range(0, len(segments)):
        for iii in range(ii, len(segments)):
            if segments[ii].id == segments[iii].id:
                continue
            if segments[ii].next is not None and segments[ii].next.id == segments[iii].id:
                continue
            if segments[ii].prev is not None and segments[ii].prev.id == segments[iii].id:
                continue
            c = segments[iii].intersects(segments[ii])  # type: Point
            if isinstance(c, Point):
                print("COLLISION", collisions, c)
                col_list_x.append(c.x)
                col_list_y.append(c.y)
                collisions += 1
                ax.annotate(collisions, xy=(c.x, c.y),
                            xycoords='data',
                            xytext=(2.5, 0.5),
                            textcoords='offset points')
    if collisions > 0:
        ax.text(0.02, 0.994, "{} Collision(s)!".format(collisions), horizontalalignment='left',
                verticalalignment='top', transform=ax.transAxes, color='red', size=16)
        # collisions = 0
        # return False
    x_pts = []
    y_pts = []
    p = Segment.master_list[0]  # type: Segment
    die_next = False
    while p is not None:
        x_pts.append(p.get_xs())
        y_pts.append(p.get_ys())
        # ax.annotate(str(p.id), xy=p.get_midpoint(),
        #             xycoords='data',
        #             xytext=(2.5, 0.5),
        #             textcoords='offset points')
        p = p.next
        if die_next: break
        if p is not None and p.next is Segment.master_list[0]:
            die_next = True
    del p
    # ax.plot(x_pts, y_pts, '.:', color="darkgreen", label="_none", lw=0.8, ms=4)  # type: Line2D

    x_pts = []
    y_pts = []
    Segment.master_list = []
    track.third_pass()
    Track.check_links(Segment.master_list)
    p = Segment.master_list[0]  # type: Segment
    center_line = []
    center_segs = []
    die_next = False
    while p is not None:
        # x_pts.append(p.get_xs())
        # y_pts.append(p.get_ys())
        center_line.append(p.collect())
        center_segs.append(p)
        # if np.abs(p.prev.angle - p.angle) > Curve.WALK_MAX_ANGLE:  # or p.id in track.s_id_list:
        #     ax.annotate(str(p.id), xy=p.get_midpoint(),
        #                 xycoords='data',
        #                 xytext=(2.5, 0.5),
        #                 textcoords='offset points')
        p = p.next
        if die_next: break
        if p is not None and p.next is Segment.master_list[0]:
            die_next = True
    del p
    cl = mc.LineCollection(center_line, 0.8, color='purple', linestyles='dashed')
    ax.add_collection(cl)

    lines = []
    l2 = []
    for l in track.smoothed:
        lines.append(l.collect())
    lc = mc.LineCollection(lines, color='gray', linewidths=2)

    for l in track.sm_l:
        l2.append(l.collect())
    lc2 = mc.LineCollection(l2, color='orange', linewidths=2)
    ax.add_collection(lc2)

    # for l in track.poly:
    #     # main center line (with colorful graphs...)
    #     ax.plot(l[0], l[1])

    # for pos, ang in track.ano_angles:
    #     ax.annotate(ang, xy=pos,
    #                 xycoords='data',
    #                 color='brown',
    #                 xytext=(20, 0.5),
    #                 textcoords='offset points')

    # ax.add_collection(lc) # print line collection?

    # ### #
    # ax.plot(xpog, ypog, '.', color="yellow", label="_none", lw=0.8, ms=15)
    # ax.plot(xp, yp, 'd', color="orange", label="_none", lw=0.8, ms=6)
    ax.plot(col_list_x, col_list_y, 'x', color="magenta", label="_none", lw=0.8, ms=8)

    # make sides
    track_length = len(center_line)
    r_x = [0.0] * track_length
    r_y = [0.0] * track_length
    l_x = [0.0] * track_length
    l_y = [0.0] * track_length
    r_segs = []  # type: list[Segment]
    l_segs = []  # type: list[Segment]

    fix_corners_r = []
    fix_corners_l = []

    toggle = 0

    for i in range(0, track_length):
        # print("{:<10} {:<10.3f} {:<10.3f} {:>10.3f}\xb0 "
        #       "N{:<10.3f}\xb0 P{:<10.3f}\xb0".format(i,
        #                                              center_line[i][0][0],
        #                                              center_line[i][0][1],
        #                                              center_segs[i].angle,
        #                                              center_segs[i].angle - 90,
        #                                              center_segs[i].angle + 90))

        # if toggle % 5 == 0:
        #     ax.annotate("{} {:.1f}".format(i, center_segs[i].angle),
        #                 xy=(center_line[i][0][0], center_line[i][0][1]),
        #                 xycoords='data',
        #                 color='darkblue',
        #                 xytext=(0, 0),
        #                 size=10,
        #                 textcoords='offset points')
        # toggle += 1

        width = np.random.uniform(Curve.MIN_TRACK_WIDTH, Curve.MAX_TRACK_WIDTH)

        r_x[i], r_y[i] = Segment.point_from_deg(center_line[i][0][0], center_line[i][0][1], width / 2,
                                                center_segs[i].angle - 90)
        l_x[i], l_y[i] = Segment.point_from_deg(center_line[i][0][0], center_line[i][0][1], width / 2,
                                                center_segs[i].angle + 90)
        if i != 0:
            r_segs.append(Segment(r_x[i], r_y[i], r_x[i - 1], r_y[i - 1]))
            l_segs.append(Segment(l_x[i], l_y[i], l_x[i - 1], l_y[i - 1]))
            if i > 1 and len(r_segs) > 1:
                r_segs[i - 2].next = r_segs[i - 1]
                r_segs[i - 1].prev = r_segs[i - 2]
                l_segs[i - 2].next = l_segs[i - 1]
                l_segs[i - 1].prev = l_segs[i - 2]

            for ii, me in enumerate(r_segs):
                oth = r_segs[i - 1]
                if oth.e == me.s:
                    continue
                r_i = me.intersects(oth)
                if r_i:
                    fix_corners_r.append((r_i, me, oth))

            for ii, me in enumerate(l_segs):
                oth = l_segs[i - 1]
                if oth.e == me.s:
                    continue
                r_i = me.intersects(oth)
                if r_i:
                    fix_corners_l.append((r_i, me, oth))

    r_segs[0].prev = r_segs[-1]
    r_segs[-1].next = r_segs[0]

    l_segs[0].prev = l_segs[-1]
    l_segs[-1].next = l_segs[0]

    for cp, s1, s2 in fix_corners_r:
        for r in range(14):
            fw = s1.forward(r)
            bw = s1.back(r)
            if fw == s2:
                s1.next = s2
                s2.prev = s1
            if bw == s2:
                pass

    for cp, s1, s2 in fix_corners_l:
        s1.next = s2
        s2.prev = s1

    r_x = []
    r_y = []
    l_x = []
    l_y = []

    s = r_segs[0]
    while s is not r_segs[-1]:
        r_x.append(s.s.x)
        r_y.append(s.s.y)
        s = s.next

    s = l_segs[0]
    while s is not l_segs[-1]:
        l_x.append(s.s.x)
        l_y.append(s.s.y)
        s = s.next

    rs_x, rs_y = zip(*ramerdouglas(list(zip(r_x, r_y)), Curve.EPSILON))
    ls_x, ls_y = zip(*ramerdouglas(list(zip(l_x, l_y)), Curve.EPSILON))
    ax.plot(rs_x, rs_y, '.--', lw=0.5, color='green', label="Simplified R Cones")
    ax.plot(ls_x, ls_y, '.--', lw=0.5, color='darkred', label="Simplified L Cones")

    ax.plot(r_x, r_y, '.-', color='lime', alpha=0.2, label="R Cones")
    ax.plot(l_x, l_y, '.-', color='red', alpha=0.2, label="L Cones")

    # SAVE DATA
    unique = str(uuid4())[:6]
    s, e = zip(*center_line)
    sx, sy = zip(*s)
    right = pd.DataFrame({
        'x': r_x,
        'y': r_y,
    })
    left = pd.DataFrame({
        'x': l_x,
        'y': l_y,
    })
    right.to_csv('data/{}_r_raw_cones.csv'.format(unique))
    left.to_csv('data/{}_l_raw_cones.csv'.format(unique))

    center = pd.DataFrame({
        'x': sx,
        'y': sy,
    })
    center.to_csv('data/{}_center_line.csv'.format(unique))

    simplel = pd.DataFrame({
        'x': ls_x,
        'y': ls_y
    })
    simplel.to_csv('data/{}_l_cones.csv'.format(unique))

    simpler = pd.DataFrame({
        'x': rs_x,
        'y': rs_y,
    })
    simpler.to_csv('data/{}_r_cones.csv'.format(unique))

    # ##########################################

    # EXAMPLE READ CSV
    # df = pd.read_csv('data/2caebd_r_cones.csv')
    # print(df.loc[0, 'x'], df.loc[0, 'y'])  # prints index zero x and y

    # ##########################################

    ax.relim()
    ax.autoscale_view()
    # save or show, pick one
    # plt.show()
    plt.savefig("data/{}_img.png".format(unique))

    print('*' * 40)
    print('successfully generated', unique)
    # END DATA
    # print(i, 'No of Segments:', len(Segment.master_list))
    collisions = 0
    return True


if __name__ == "__main__":
    plt.tight_layout()
    anim = FuncAnimation(fig, update, interval=1000, repeat=False)
    play_once = True
    update(1)
    exit(0)

    # anim.save('paths.mp4', codec='libx264', fps=30)
    # print("done saving!")
    # figManager = plt.get_current_fig_manager()
    # figManager.window.state('zoomed')  # works fine on Windows!
