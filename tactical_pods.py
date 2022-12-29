from __future__ import annotations
from typing import Union, Iterable
import sys

from math import degrees, radians, remainder
from cmath import rect, polar, phase, pi
from collections import namedtuple, deque
import numpy as np


CP_RADIUS = 600
CP_GRAVITY = CP_RADIUS // 5
HOLD_DURATION = 7


Pod = namedtuple("Pod", ["x", "y", "vx", "vy", "angle", "cpid"])

## --- pod_utils: start ---
Coord = namedtuple("Coord", ["x", "y"])
BEZIER_DETAIL = 8


def clamp(value: float, left: float, right: float) -> float:
    return max(left, min(value, right))


def to_coords(z: complex) -> tuple[int, int]:
    return int(round(z.real)), int(round(z.imag))


def humangle(alpha: float) -> str:
    return f"{int(round(degrees(alpha)))}°"


def thrust_value(a_thrust: Union[int, str]) -> int:
    if a_thrust == "SHIELD":
        thrust = 0
    elif a_thrust == "BOOST":
        thrust = 650
    else:
        thrust = int(a_thrust)
    return thrust


def lerp(a: float, b: float, t: float) -> float:
    return (1 - t) * a + t * b


def inv_lerp(a: float, b: float, v: float) -> float:
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


## --- pod_utils: end ---


## --- PodRacer: start ---
class PodRacer:
    def __init__(self, name, pod: Pod, checkpoints: list[Coord]) -> None:
        self.name = name
        self.has_boost = True
        self.speed_trace = deque(maxlen=4)
        self.cpid = int()
        self.next_cp = self.cp = self.target = complex()
        self.last_position = self.position = self.velocity = complex()
        self.angle = float()
        self.thrust = int()
        self.shield_count = int()
        self.update(pod, checkpoints)

    def update(self, pod: Pod, checkpoints: list[Coord]) -> None:
        self.last_position = self.position
        if self.shield_count:
            self.shield_count -= 1

        self.cpid = pod.cpid
        self.position = complex(pod.x, pod.y)
        self.angle = radians(pod.angle)
        self.velocity = complex(pod.vx, pod.vy)
        self.speed_trace.append(int(round(abs(self.velocity))))

        self.cp = complex(*checkpoints[pod.cpid])
        self.next_cp = complex(*checkpoints[(pod.cpid + 1) % len(checkpoints)])

        # set dummy target
        self.thrust = 100
        self.target = self.cp

    @property
    def target_distance(self) -> float:
        return abs(self.cp - self.position)

    def __str__(self):
        xc, yc = to_coords(self.target)
        return f"{xc} {yc} {self.thrust}"

    def __repr__(self):
        return (
            f"TD:{int(round(self.target_distance)):4}m, "
            f"V:{int(round(abs(self.velocity))):4} m/s, O:{self.thrust:3} "
            f"<):{humangle(self.angle):4}° boost: {int(self.has_boost)}"
        )

    def boost(self) -> None:
        if self.has_boost:
            self.thrust = "BOOST"
            self.has_boost = False

    def shield(self) -> None:
        self.shield_count = 3
        self.thrust = "SHIELD"

    def defend_on_collision(self, opponents: Iterable[PodRacer]):
        for opp in opponents:
            next_dist = int(round(abs(self.next_position - opp.next_position)))
            speed_diff = abs(self.velocity - opp.velocity)

            if next_dist <= 888 and speed_diff > 233:
                self.shield()
                return

    @property
    def next_position(self) -> complex:
        """projected next position considering current target"""
        thrust = thrust_value(self.thrust)
        t_angle = phase(self.target - self.position)
        dev = t_angle - self.angle
        rot = clamp(dev, -pi / 10, pi / 10)

        acc = rect(thrust, self.angle + rot)
        movement = self.velocity + acc
        new_position = self.position + movement

        return new_position

    def projection(
        self,
        use_target: complex,
        use_thrust: Union[str, int],
        max_steps: int = 5,
    ) -> tuple[int, complex, float, complex]:
        """Will stop if target is reached sooner than max_steps"""

        thrust = 0 if self.shield_count else thrust_value(use_thrust)
        position = self.position
        velocity = self.velocity
        angle = self.angle
        distance = int(round(abs(position - use_target)))

        step = 0
        while distance > (CP_RADIUS - CP_GRAVITY) and step < max_steps:
            step += 1

            # compute pod rotation (max. 18 degrees)
            t_angle = phase(use_target - position)
            deviation = remainder(t_angle - angle, 2 * pi)
            angle += clamp(deviation, -pi / 10, pi / 10)

            # compute movement vectors
            movement = velocity + rect(thrust, angle)
            position += movement
            distance = int(round(abs(position - use_target)))
            velocity = 0.85 * movement

        return step, position, angle, velocity

    def drift_projection(
        self,
        use_target: complex,
        use_thrust: Union[str, int],
        towards: complex,
        max_steps: int = 5,
    ) -> tuple[Union[int, None], complex, float, complex]:
        """Will stop if target is reached sooner than max_steps"""

        thrust = 0 if self.shield_count else thrust_value(use_thrust)
        position = self.position
        velocity = self.velocity
        angle = self.angle
        distance = int(round(abs(position - use_target)))

        step = 0
        while distance > (CP_RADIUS - CP_GRAVITY) and step < max_steps:
            step += 1

            # compute pod rotation (max. 18 degrees)
            to_angle = phase(towards - position)
            deviation = remainder(to_angle - angle, 2 * pi)
            angle += clamp(deviation, -pi / 10, pi / 10)

            # compute movement vectors
            movement = velocity + rect(thrust, angle)  # move towards next target
            position += movement
            velocity = 0.85 * movement
            new_distance = int(
                round(abs(position - use_target))
            )  # computed agains target

            if new_distance < distance:
                distance = new_distance
            else:
                step = None
                break

        return step, position, angle, velocity


## --- PodRacer: end ---

## --- more utils ---
def touch(position: complex, target: complex) -> complex:
    """Will barely touch the checkpoint"""
    along = position - target
    touch_delta = rect(CP_GRAVITY - CP_RADIUS, phase(along))
    return target - touch_delta


def can_drift(pod: PodRacer) -> tuple[complex, Union[int, str]]:
    far_enough = abs(pod.velocity) * 8
    if pod.target_distance > far_enough or pod.shield_count:
        return pod.cp, pod.thrust

    # priority 1: reach cp
    best_angle = phase(pod.next_cp - pod.cp)
    choose = dict()
    for acc in range(0, 100, 20):
        steps, pos, ang, vel = pod.projection(pod.cp, acc)
        if steps < 5:
            dist = abs(pod.cp - pos)
            dev = abs(best_angle - ang)
            choose[acc] = steps, dist, dev

    # priority 2: drift towards next cp
    for acc in range(5, 100, 20):
        steps, pos, ang, vel = pod.drift_projection(pod.cp, acc, pod.next_cp)
        if steps is not None and steps < 5:
            dist = abs(pod.cp - pos)
            dev = abs(best_angle - ang)
            choose[acc] = steps, dist, dev

    print(choose, file=sys.stderr)
    if choose:
        best = max(
            choose, key=lambda k: (choose[k][0], choose[k][1] * (choose[k][2] ** 2))
        )
        print(f"{best}: {choose[best]}", file=sys.stderr)

        return pod.next_cp if best % 5 == 0 else pod.cp, best

    return pod.cp, pod.thrust


def drift(my_pods: list[PodRacer]):
    for pod in my_pods:
        target, thrust = can_drift(pod)
        pod.target = target
        pod.thrust = thrust


def main():
    layout = read_race_layout()
    print(f"{layout=}", file=sys.stderr)

    # first turn
    pods = read_pods()
    me1 = PodRacer("me1", pods["me_first"], layout["checkpoints"])
    me2 = PodRacer("me2", pods["me_second"], layout["checkpoints"])
    him1 = PodRacer("him1", pods["him_first"], layout["checkpoints"])
    him2 = PodRacer("him2", pods["him_second"], layout["checkpoints"])

    my_pods = [me1, me2]
    his_pods = [him1, him2]

    # take the checkpoint as first target
    print(repr(me1), file=sys.stderr)
    print(repr(me2), file=sys.stderr)

    print(me1)
    print(me2)

    while True:
        pods = read_pods()

        me1.update(pods["me_first"], layout["checkpoints"])
        me2.update(pods["me_second"], layout["checkpoints"])
        him1.update(pods["him_first"], layout["checkpoints"])
        him2.update(pods["him_second"], layout["checkpoints"])

        drift(my_pods)
        map(lambda pod: pod.defend_on_collision(his_pods), my_pods)

        print(repr(me1), file=sys.stderr)
        print(repr(me2), file=sys.stderr)

        print(me1)
        print(me2)


if __name__ == "__main__":
    main()
