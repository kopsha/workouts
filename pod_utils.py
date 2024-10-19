from __future__ import annotations

from cmath import phase, pi, rect
from collections import namedtuple
from math import degrees, remainder

import numpy as np

Pod = namedtuple("Pod", ["x", "y", "vx", "vy", "angle", "cpid"])
Coord = namedtuple("Coord", ["x", "y"])
BEZIER_DETAIL = 8


def clamp(value: float, left: float, right: float):
    return max(left, min(value, right))


def to_coords(z: complex) -> tuple[int, int]:
    return int(round(z.real)), int(round(z.imag))


def humangle(alpha: float):
    return f"{int(round(degrees(alpha)))}°"


def thrust_value(a_thrust: int | str) -> int:
    if a_thrust == "SHIELD":
        thrust = 0
    elif a_thrust == "BOOST":
        thrust = 650
    else:
        thrust = int(a_thrust)
    return thrust


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b


def inv_lerp(a: float, b: float, v: float) -> float:
    """Inverse Linar Interpolation, get the fraction between a and b on which v resides.
    Examples
    --------
        0.5 == inv_lerp(0, 100, 50)
        0.8 == inv_lerp(1, 5, 4.2)
    """
    return (v - a) / (b - a)


def quadratic(a: float, b: float, c: float, t: float) -> float:
    rc = (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t**2 * c
    return rc


def quadratic_bezier(a: Coord, b: Coord, c: Coord) -> list[Coord]:
    curve = [
        Coord(quadratic(a.x, b.x, c.x, t), quadratic(a.y, b.y, c.y, t))
        for t in np.linspace(0, 1, BEZIER_DETAIL)
    ]
    return curve


def cubic(a: float, b: float, c: float, d: float, t: float) -> float:
    rc = (
        (1 - t) ** 3 * a
        + 3 * (1 - t) ** 2 * t * b
        + 3 * (1 - t) * t**2 * c
        + t**3 * d
    )
    return rc


def cubic_bezier(a: Coord, b: Coord, c: Coord, d: Coord) -> list[Coord]:
    curve = [
        Coord(cubic(a.x, b.x, c.x, d.x, t), cubic(a.y, b.y, c.y, d.y, t))
        for t in np.linspace(0, 1, BEZIER_DETAIL)
    ]
    return curve


def read_race_layout() -> dict:
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

    print(race_layout, file=sys.stderr)

    return race_layout


def read_pods() -> dict:
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


def pick_control_points(
    position: complex, target: complex, towards: complex
) -> tuple[complex, complex]:
    target_angle = phase(target - position)
    towards_angle = phase(towards - target)
    half_twist = remainder(target_angle - towards_angle, 2 * pi) / 2

    offset = (target - position) / 4
    d_offset = offset * rect(1, pi - half_twist)
    d_offset_opp = offset * rect(1, -half_twist)

    return target + d_offset, target + d_offset_opp


def build_optimal_segments(checkpoints: list[Coord]) -> list[tuple[Coord]]:
    segments = list()
    assert checkpoints

    # find all control points
    last_mirror_cp = checkpoints[0]
    for left, right, tow in zip(
        checkpoints,
        checkpoints[1:] + checkpoints[:1],
        checkpoints[2:] + checkpoints[:2],
    ):
        position = complex(*left)
        target = complex(*right)
        towards = complex(*tow)
        zcp, mirror_zcp = pick_control_points(position, target, towards)
        cp, mirror_cp = Coord(*to_coords(zcp)), Coord(*to_coords(mirror_zcp))

        segments.append((left, last_mirror_cp, cp, right))
        last_mirror_cp = mirror_cp

    # add missing control point for start position
    first_corrected = (
        segments[0][0],
        last_mirror_cp,
        segments[0][2],
        segments[0][3],
    )
    segments[0] = first_corrected

    return segments


def build_bezier_path(segments) -> list[Coord]:
    path = list()
    for a, b, c, d in segments:
        curve = cubic_bezier(a, b, c, d)
        path.extend(curve[:-1])
    return path


def find_optimal_angles(checkpoints: list[Coord]) -> list[tuple[Coord]]:
    segments = list()
    assert checkpoints

    # find all control points
    last_mirror_cp = checkpoints[0]
    for left, right, tow in zip(
        checkpoints,
        checkpoints[1:] + checkpoints[:1],
        checkpoints[2:] + checkpoints[:2],
    ):
        position = complex(*left)
        target = complex(*right)
        towards = complex(*tow)
        zcp, mirror_zcp = pick_control_points(position, target, towards)
        cp, mirror_cp = Coord(*to_coords(zcp)), Coord(*to_coords(mirror_zcp))

        segments.append((left, last_mirror_cp, cp, right))
        last_mirror_cp = mirror_cp

    # add missing control point for start position
    first_corrected = (
        segments[0][0],
        last_mirror_cp,
        segments[0][2],
        segments[0][3],
    )
    segments[0] = first_corrected

    return segments


def find_nearest_entry(position, facing, cpid, segments, curve):
    """
    Given current position, facing angle and existing bezier curve, finds the
    best point to enter the path...
    """

    segment_size = BEZIER_DETAIL - 1
    start = cpid * segment_size
    stop = ((cpid - 1) % len(segments)) * segment_size

    nearest = start
    point = complex(*curve[start])
    dist = abs(point - position)
    delta = remainder(facing - phase(point - position), 2 * pi)
    best = dist * delta**2

    if start == 0:
        start = len(curve) - 1

    for i in range(start - 1, stop, -1):
        point = complex(*curve[i])
        dist = abs(point - position)
        delta = remainder(facing - phase(point - position), 2 * pi)
        keyf = dist * delta**2

        if keyf < best:
            best = keyf
            nearest = i

    return curve[nearest]


## Captured samples
SAMPLE1 = {
    "lap_count": 3,
    "cp_count": 5,
    "checkpoints": [
        Coord(13050, 1919),
        Coord(6554, 7863),
        Coord(7490, 1379),
        Coord(12724, 7080),
        Coord(4053, 4660),
    ],
}
SAMPLE2 = {
    "lap_count": 3,
    "cp_count": 6,
    "checkpoints": [
        Coord(x=3030, y=5188),
        Coord(x=6253, y=7759),
        Coord(x=14105, y=7752),
        Coord(x=13861, y=1240),
        Coord(x=10255, y=4897),
        Coord(x=6080, y=2172),
    ],
}
SAMPLE3 = {
    "lap_count": 3,
    "cp_count": 3,
    "checkpoints": [
        Coord(x=9098, y=1847),
        Coord(x=5007, y=5276),
        Coord(x=11497, y=6055),
    ],
}
SAMPLE4 = {
    "lap_count": 3,
    "cp_count": 4,
    "checkpoints": [
        Coord(x=5661, y=2571),
        Coord(x=4114, y=7395),
        Coord(x=13518, y=2355),
        Coord(x=12948, y=7198),
    ],
}
SAMPLE5 = {
    "lap_count": 3,
    "cp_count": 6,
    "checkpoints": [
        Coord(x=3296, y=7255),
        Coord(x=14594, y=7682),
        Coord(x=10559, y=5045),
        Coord(x=13114, y=2310),
        Coord(x=4549, y=2172),
        Coord(x=7373, y=4959),
    ],
}
SAMPLE6 = {
    "lap_count": 3,
    "cp_count": 6,
    "checkpoints": [
        Coord(x=7666, y=5993),
        Coord(x=3169, y=7518),
        Coord(x=9505, y=4407),
        Coord(x=14498, y=7755),
        Coord(x=6335, y=4272),
        Coord(x=7786, y=852),
    ],
}
BRAKE_PROFILE = [
    (-504, 96),
    (-428, 81),
    (-363, 68),
    (-308, 57),
    (-261, 48),
    (-221, 40),
    (-187, 34),
    (-158, 28),
    (-134, 23),
    (-113, 19),
    (-96, 16),
    (-81, 13),
    (-68, 11),
    (-57, 9),
    (-48, 7),
    (-40, 5),
    (-34, 4),
    (-28, 3),
    (-23, 2),
    (-19, 1),
    (-16, 0),
    (-13, 0),
    (-11, 0),
    (-9, 0),
    (-7, 0),
    (-5, 0),
    (-4, 0),
    (-3, 0),
    (-2, 0),
    (-1, 0),
    (0, 0),
]
SHIELD_PROFILE = [
    (-504, 96),
    (-428, 81),
    (-363, 68),
    (-308, 57),
    (-261, 48),
    (-221, 40),
    (-187, 34),
    (-158, 28),
    (-134, 23),
    (-113, 19),
    (-96, 16),
    (-81, 13),
    (-68, 11),
    (-57, 9),
    (-48, 7),
    (-40, 5),
    (-34, 4),
    (-28, 3),
    (-23, 2),
    (-19, 1),
    (-16, 0),
    (-13, 0),
    (-11, 0),
    (-9, 0),
    (-7, 0),
    (-5, 0),
    (-4, 0),
    (-3, 0),
    (-2, 0),
    (-1, 0),
    (0, 0),
]
