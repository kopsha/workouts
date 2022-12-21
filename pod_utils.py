from __future__ import annotations

from cmath import rect, phase, pi
from math import remainder, degrees
from collections import namedtuple
import numpy as np


Coord = namedtuple("Coord", ["x", "y"])
BEZIER_DETAIL = 8
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


def clamp(value: float, left: float, right: float):
    return max(left, min(value, right))


def to_coords(z: complex) -> tuple[int, int]:
    return int(round(z.real)), int(round(z.imag))


def humangle(alpha: float):
    return f"{int(round(degrees(alpha)))}°"


def lerp(a: Coord, b: Coord, t: float) -> Coord:
    rx = (1 - t) * a.x + t * b.x
    ry = (1 - t) * a.y + t * b.y
    return Coord(rx, ry)


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
