#!/usr/bin/env python3

from __future__ import annotations

import sys
from cmath import phase, pi, polar, rect
from collections import deque, namedtuple
from math import degrees, radians, remainder, sqrt
from typing import Iterable, Union

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


def dot(a: complex, b: complex) -> float:
    return a.real * b.real + a.imag * b.imag


def aim_ahead(pos_delta: complex, velo_delta: complex, speed: float) -> float | None:
    """
    Computes time delta when the pod will hit target, or None if impossible
    """
    # Quadratic equation: a*t^2 + b*t + c = 0
    a = dot(velo_delta, velo_delta) - speed**2
    b = dot(velo_delta, pos_delta) * 2
    c = dot(pos_delta, pos_delta)
    disc = b * b - 4 * a * c

    if disc < 0:
        return None

    x1 = 2 * c / (sqrt(disc) - b)
    x2 = 2 * c / (-sqrt(disc) - b)

    return x1


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
        self.cpid = int(1)
        self.next_cp = self.cp = self.target = complex()
        self.last_position = self.position = self.velocity = complex()
        self.angle = float()
        self.thrust = int()
        self.shield_count = int()
        self.remaining_checkpoints = 3 * len(checkpoints)

    def update(self, pod: Pod, checkpoints: list[Coord]) -> None:
        if self.shield_count:
            self.shield_count -= 1

        if self.cpid != pod.cpid:
            self.remaining_checkpoints -= 1
            self.cpid = pod.cpid

        self.last_position = self.position
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

    @property
    def remaining_work(self) -> int:
        return self.remaining_checkpoints * 100_000 + int(self.target_distance)

    def __str__(self):
        xc, yc = to_coords(self.target)
        return f"{xc} {yc} {self.thrust}"

    def __repr__(self):
        return (
            f"{self.name:>4} < "
            f"TD:{int(round(self.target_distance)):4}m, "
            f"V:{int(round(abs(self.velocity))):4} m/s, O:{self.thrust:3} "
            f"<):{humangle(self.angle):>4} boost: {int(self.has_boost)} "
            f"{self.remaining_work:10,}"
        )

    @property
    def can_boost(self) -> bool:
        return self.shield_count == 0 and self.has_boost

    @property
    def next_state(self) -> tuple[complex, float, complex]:
        """projected next position considering current target"""
        # compute pod rotation (max. 18 degrees)
        position = self.position
        angle = self.angle
        t_angle = phase(self.target - position)
        deviation = remainder(t_angle - angle, 2 * pi)
        angle += clamp(deviation, -pi / 10, pi / 10)

        # compute movement vectors
        use_thrust = thrust_value(self.thrust)
        movement = self.velocity + rect(use_thrust, angle)
        position += movement
        velocity = 0.85 * movement

        return position, angle, velocity

    def boost(self) -> None:
        if self.can_boost:
            self.thrust = "BOOST"
            self.has_boost = False

    def shield(self) -> None:
        self.shield_count = 3
        self.thrust = "SHIELD"

    def defend_on_collision(self, opponents: Iterable[PodRacer]):
        for opp in opponents:
            next_pos, next_angle, next_velocity = self.next_state
            next_dist = int(round(abs(self.next_position - opp.next_position)))
            speed_diff = int(round(abs(self.velocity - opp.velocity)))
            angle_diff = abs(
                remainder(phase(self.velocity) - phase(opp.velocity), 2 * pi)
            )

            if next_dist <= 844 and speed_diff >= 333 and angle_diff > pi / 5:
                self.shield()
                return

    def projection(
        self, use_thrust: Union[str, int], max_steps: int = 6
    ) -> tuple[int, complex, float, complex]:
        """Will stop if target is reached sooner than max_steps"""

        thrust = 0 if self.shield_count else thrust_value(use_thrust)
        position = self.position
        velocity = self.velocity
        angle = self.angle
        distance = int(round(self.target_dis))

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

    def boost_on_long_distance(self) -> bool:
        if self.has_boost:
            t_angle = phase(self.target - self.position)
            dev = remainder(t_angle - self.angle, 2 * pi)
            if self.target_distance > 5000 and abs(dev) <= pi / 36:
                self.boost()
                return self.thrust == "BOOST"
        return False

    def oversteer_towards_target(self) -> None:
        t_angle = phase(self.target - self.position)
        v_angle = phase(self.velocity)
        deviation = remainder(t_angle - v_angle, 2 * pi)
        desired = self.target - self.position

        correction = clamp(deviation / 4, -pi / 18, pi / 18)
        new_target = desired * rect(1, correction) + self.position
        self.target = new_target

    def intercept(self, goat: PodRacer):
        pos_delta = goat.position - self.position
        _, _, my_velocity = self.next_state
        _, _, goat_velocity = goat.next_state
        velo_delta = goat_velocity - my_velocity

        td = aim_ahead(pos_delta, velo_delta, abs(my_velocity))
        if td is None or td > 8 or td <= 0:
            print(
                f"{self.name} cannot intercept {goat.name} [{td or -1:.0f}]",
                file=sys.stderr,
            )
            return

        time_delta = int(round(td))
        moves, aim_point, _, aim_velo = goat.projection(
            goat.cp, goat.thrust, max_steps=time_delta
        )

        if moves < time_delta:
            print(
                "Goat will reach cp before collision, heading towards next target",
                goat.next_cp,
                file=sys.stderr,
            )
            self.target = goat.next_cp
            self.thrust = 100
        else:
            print(
                f"Projected collision in {moves} steps @ {to_coords(aim_point)}",
                file=sys.stderr,
            )
            self.target = aim_point
            self.thrust = 100

        next_dist = int(round(abs(self.next_position - goat.next_position)))
        if next_dist <= 808:
            self.shield()


## --- PodRacer: end ---


## --- more utils ---
def touch(position: complex, target: complex) -> complex:
    """Will barely touch the checkpoint"""
    along = position - target
    touch_delta = rect(CP_GRAVITY - CP_RADIUS, phase(along))
    return target - touch_delta


def drift_towards_checkpoint(pod: PodRacer) -> tuple[complex, Union[int, str]]:
    far_enough = abs(pod.velocity) * 8
    if pod.target_distance > far_enough or pod.shield_count:
        # too far to evaluate drift
        return pod.cp, pod.thrust

    best_angle = phase(pod.next_cp - pod.cp)
    choose = dict()
    for acc in range(0, 100, 20):
        ss, pos, ang, _ = pod.projection(pod.cp, acc)
        dss, dpos, dang, _ = pod.drift_projection(pod.cp, acc, pod.next_cp)

        if ss < 5:
            dist = abs(pod.cp - pos)
            deviation = remainder(best_angle - ang, 2 * pi)
            dev = degrees(abs(deviation))
            choose[acc] = ss, dev * dist, dist, False

        if dss is not None and dss < 5:
            dist = abs(pod.cp - dpos)
            deviation = remainder(best_angle - dang, 2 * pi)
            dev = degrees(abs(deviation))
            choose[acc] = ss, dev * dist, dist, True

    if choose:
        best = min(choose, key=lambda k: choose[k])
        return pod.next_cp if choose[best][3] else pod.cp, best

    return pod.cp, pod.thrust


def drift(my_pods: list[PodRacer]):
    for pod in my_pods:
        target, thrust = drift_towards_checkpoint(pod)
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

    hold_boost = 0
    while True:
        pods = read_pods()

        me1.update(pods["me_first"], layout["checkpoints"])
        me2.update(pods["me_second"], layout["checkpoints"])
        him1.update(pods["him_first"], layout["checkpoints"])
        him2.update(pods["him_second"], layout["checkpoints"])

        ranked_pods = sorted(my_pods + his_pods, key=lambda pod: pod.remaining_work)
        drift(my_pods)

        mine = list()
        his = list()
        for i, pod in enumerate(ranked_pods):
            if pod.name.startswith("him"):
                his.append(pod)
            else:
                mine.append(pod)

        mine[0].oversteer_towards_target()
        mine[1].intercept(his[0])

        me1.defend_on_collision(his_pods)
        me2.defend_on_collision(his_pods)

        if hold_boost:
            hold_boost -= 1
        else:
            if me1.boost_on_long_distance():
                hold_boost = 7
            elif me2.boost_on_long_distance():
                hold_boost = 7

        print(me1)
        print(me2)


if __name__ == "__main__":
    main()
