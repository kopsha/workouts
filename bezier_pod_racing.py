from __future__ import annotations
from typing import Iterable
from math import degrees, radians, remainder
from cmath import rect, polar, phase, pi
from collections import namedtuple, deque
import sys

from pod_utils import (
    Coord,
    clamp,
    humangle,
    to_coords,
    cubic_bezier,
    build_optimal_segments,
    build_bezier_path,
    find_nearest_entry,
)


CP_RADIUS = 600
CP_GRAVITY = CP_RADIUS // 10
TURN_SPEED = 400
HOLD_DURATION = 7


Pod = namedtuple("Pod", ["x", "y", "vx", "vy", "angle", "cpid"])

# ---- cut here ----
class PodRacer:
    def __init__(self, name, pod: Pod, checkpoints: list[Coord]) -> None:
        self.name = name
        self.has_boost = True
        self.speed_trace = deque(maxlen=5)
        self.update(pod, checkpoints)

    def update(self, pod: Pod, checkpoints: list[Coord]) -> None:
        self.last_position = getattr(self, "position", None)
        self.position = complex(pod.x, pod.y)

        self.velocity = complex(pod.vx, pod.vy)
        self.speed_trace.append(int(round(abs(self.velocity))))
        self.v_angle = phase(self.velocity)
        self.angle = radians(pod.angle)
        self.facing = pod.angle

        self.cpid = pod.cpid
        self.cp = complex(*checkpoints[pod.cpid])
        self.next_cp = complex(*checkpoints[(pod.cpid + 1) % len(checkpoints)])

        # dummy
        self.thrust = 100
        self.target = self.cp

    def touch(self, target: complex) -> complex:
        """Will barely touch the checkpoint"""
        along = self.position - target
        touch_delta = rect(CP_GRAVITY - CP_RADIUS, phase(along))
        return target - touch_delta

    def drift_towards_checkpoint(self):
        target = self.target
        thrust = 100
        distance = abs(self.position - self.cp)

        target_dev = remainder(phase(target - self.position) - self.v_angle, 2 * pi)
        next_cp_dev = remainder(self.v_angle - phase(self.next_cp - self.cp), 2 * pi)

        if distance <= sum(self.speed_trace):
            if self.speed_trace[-1] > 300:
                # change target sooner to allow rotation
                target = self.next_cp
            if abs(next_cp_dev) > pi / 2:
                thrust = 0
            elif abs(next_cp_dev) > pi / 4:
                thrust = 50
        else:
            if abs(target_dev) > 3 * pi / 4:
                thrust = 0 if self.speed_trace[-1] > 250 else 33
            elif abs(target_dev) > pi / 2:
                thrust = 66

        self.target = self.touch(target)
        self.thrust = thrust

    def correct_rotation(self) -> complex:
        facing = remainder(self.angle, 2 * pi)
        t_angle = phase(self.target - self.position)
        target_dev = remainder(t_angle - self.v_angle, 2 * pi)
        desired = self.target - self.position

        correction = clamp(target_dev / 4, -pi / 20, pi / 20)

        print(
            f"{self.name}> {humangle(facing)}, {humangle(self.v_angle)}, {humangle(t_angle)}",
            file=sys.stderr,
        )
        print(
            f"{self.name}> {humangle(target_dev)} Correction: {humangle(correction)}",
            file=sys.stderr,
        )

        rotate = rect(1, correction)
        return desired * rotate + self.position

    @property
    def next_position(self):
        if self.thrust == "SHIELD":
            thrust = 0
        elif self.thrust == "BOOST":
            thrust = 650
        else:
            thrust = self.thrust

        t_angle = phase(self.target - self.position)
        dev = t_angle - self.angle
        rot = clamp(dev, -pi / 10, pi / 10)

        acc = rect(int(thrust), self.angle + rot)
        movement = self.velocity + acc
        new_position = self.position + movement

        return new_position

    def defend_on_collision(self, opponents: Iterable[PodRacer]):
        for opp in opponents:
            next_dist = int(round(abs(self.next_position - opp.next_position)))
            speed_diff = abs(self.velocity - opp.velocity)

            if next_dist <= 888 and speed_diff > 250:
                self.thrust = "SHIELD"
                return

    def can_boost(self) -> bool:
        if self.has_boost:
            target_dev = remainder(
                phase(self.target - self.position) - self.v_angle, pi
            )
            distance = abs(self.position - self.cp)
            if abs(target_dev) < pi / 36 and distance > 4500:
                return True
        return False

    def boost(self) -> None:
        if self.has_boost:
            self.thrust = "BOOST"
            self.has_boost = False

    def __str__(self):
        return (
            f"{int(round(self.target.real))} "
            f"{int(round(self.target.imag))} "
            f"{self.thrust}"
        )

    def __repr__(self):
        return (
            f"F<:{self.facing}° "
            f"V:{int(round(abs(self.velocity))):4} m/s O:{self.thrust:4} "
            f"D:{int(round(abs(self.cp - self.position))):4} m "
            f"has boost: {self.has_boost}"
        )


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


def read_all_pods() -> dict:
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


def main():
    layout = read_race_layout()
    print(f"{layout=}", file=sys.stderr)

    # first turn
    pods = read_all_pods()
    me1 = PodRacer("me1", pods["me_first"], layout["checkpoints"])
    me2 = PodRacer("me2", pods["me_second"], layout["checkpoints"])
    him1 = PodRacer("him1", pods["him_first"], layout["checkpoints"])
    him2 = PodRacer("him2", pods["him_second"], layout["checkpoints"])

    # take the checkpoint as first target

    print(repr(me1), file=sys.stderr)
    print(repr(me2), file=sys.stderr)

    print(me1)
    print(me2)

    hold_boost = 0
    while True:
        pods = read_all_pods()
        me1.update(pods["me_first"], layout["checkpoints"])
        me2.update(pods["me_second"], layout["checkpoints"])
        him1.update(pods["him_first"], layout["checkpoints"])
        him2.update(pods["him_second"], layout["checkpoints"])

        me1.drift_towards_checkpoint()
        me1.correct_rotation()

        me2.drift_towards_checkpoint()
        # me2.correct_rotation()

        # TODO:
        # - evaluate, can we reach the target [postponed]
        # - avoid team collisions
        # - bezier racing lines for fastest target reach
        # - evaluate race positions
        # - avoid obstacles strategy
        # - add bullying strategy

        if hold_boost > 0:
            hold_boost -= 1
        else:
            if me1.can_boost():
                me1.boost()
                hold_boost = HOLD_DURATION
            elif me2.can_boost():
                me2.boost()
                hold_boost = HOLD_DURATION

        me1.defend_on_collision((him1, him2))
        me2.defend_on_collision((him2, him1))

        print(repr(me1), file=sys.stderr)
        print(repr(me2), file=sys.stderr)

        print(me1)
        print(me2)


if __name__ == "__main__":
    main()
# ---- cut here ----
