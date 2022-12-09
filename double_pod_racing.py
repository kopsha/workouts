import math
import cmath
import sys

from collections import namedtuple


CP_RADIUS = 600
TURN_SPEED = 400  # TODO: do we really need this?

Coord = namedtuple("Coord", ["x", "y"])
Pod = namedtuple("Pod", ["x", "y", "vx", "vy", "angle", "cp_id"])


def read_race_layout():
    """
    Initialization input
    Line 1: `laps`: the number of laps to complete the race.
    Line 2: `checkpoint_count`: the number of checkpoints in the circuit.
    Next `checkpoint_count` lines: 2 integers (x, y) for the coordinates of
    each checkpoint.
    """
    lap_count = int(input())
    cp_count = int(input())
    checkpoints = [Coord(*map(int, input().split())) for _ in range(cp_count)]

    race_layout = dict(
        lap_count=lap_count,
        cp_count=cp_count,
        checkpoints=checkpoints,
    )

    return race_layout


def read_all_pods():
    """
    Read input for one game turn
    First 2 lines: Your two pods.
    Next 2 lines: The opponent's pods.
    Each pod is represented by:
    - 6 integers, (x, y) for the position
    - (vx, vy) for the speed vector
    - angle for the rotation angle in degrees
    - nextCheckPointId for the number of the next checkpoint the pod must go through.
    """
    me_first = Pod(*map(int, input().split()))
    me_second = Pod(*map(int, input().split()))
    him_first = Pod(*map(int, input().split()))
    him_second = Pod(*map(int, input().split()))

    return dict(
        me_first=me_first,
        me_second=me_second,
        him_first=him_first,
        him_second=him_second,
    )


def to_coords(z):
    return int(round(z.real)), int(round(z.imag))


def closer_target(position, checkpoint, gravity):
    along = position - checkpoint
    touchdelta = cmath.rect(gravity - CP_RADIUS, cmath.phase(along))
    return checkpoint - touchdelta


def break_on_large_angles(thrust, c_angle):
    """apply braking strategy based on angle to target"""
    angle = abs(c_angle)
    if angle < 45:
        thrust = thrust
    elif angle < 90:
        thrust = 66
    else:
        thrust = 34

    return thrust


def break_on_close_target(c_dist, velocity):
    """apply braking strategy based on distance to target"""
    thrust = 100
    if abs(velocity) > TURN_SPEED:
        if c_dist < CP_RADIUS * 1.4:
            thrust = 34

    return thrust


def steer_towards_opponent(target, position, opponent, last_opponent):
    # TODO: rework this
    ph1 = cmath.phase(target - position)
    ph2 = cmath.phase(opponent - last_opponent)
    opp_angle = abs(math.remainder(ph1 - ph2, cmath.pi))

    opponent_dist = abs(position - opponent)
    if opp_angle < cmath.pi / 5 and opponent_dist <= CP_RADIUS * 3:
        x = (target.real * 2 + opponent.real) / 3
        y = (target.imag * 2 + opponent.imag) / 3
        target = complex(x, y)
    return target


def boost_on_long_distance(thrust, c_dist, c_angle, c_index):
    # TODO: rework this
    if c_dist > 5000 and abs(c_angle) < 5:
        thrust = "BOOST"

    return thrust


def execute(orders):
    for cmd in orders:
        print(*cmd)


def main():
    # first loop
    layout = read_race_layout()
    print(layout, file=sys.stderr)

    while True:
        pods = read_all_pods()
        print(pods, file=sys.stderr)

        # lame strategy
        orders = [
            (*layout["checkpoints"][pods["me_first"].cp_id], 100),
            (*layout["checkpoints"][pods["me_second"].cp_id], 100),
        ]
        execute(orders)


if __name__ == "__main__":
    main()
