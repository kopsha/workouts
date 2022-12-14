from __future__ import annotations
import math
import cmath
import sys
from collections import namedtuple, deque
from typing import Iterable


CP_RADIUS = 600
CP_GRAVITY = CP_RADIUS // 10
TURN_SPEED = 400

Coord = namedtuple("Coord", ["x", "y"])
Pod = namedtuple("Pod", ["x", "y", "vx", "vy", "angle", "cpid"])


class PodRacer:
    def __init__(self, name, pod: Pod, checkpoints: list[Coord]) -> None:
        self.name = name
        self.has_boost = True
        self.speed_trace = deque(maxlen=5)
        self.position = None
        self.update(pod, checkpoints)

    def update(self, pod: Pod, checkpoints: list[Coord]) -> None:
        self.last_position = self.position
        self.position = complex(pod.x, pod.y)

        self.velocity = complex(pod.vx, pod.vy)
        self.speed_trace.append(int(round(abs(self.velocity))))
        self.v_angle = cmath.phase(self.velocity)

        self.cpid = pod.cpid
        self.cp = complex(*checkpoints[pod.cpid])
        self.next_cp = complex(*checkpoints[(pod.cpid + 1) % len(checkpoints)])
        self.target, self.thurst = self.drift_towards(self.cp)
        self.target = self.correct_rotation()

    def touch(self, target: complex) -> complex:
        """Will barely touch the checkpoint"""
        along = self.position - target
        touch_delta = cmath.rect(CP_GRAVITY - CP_RADIUS, cmath.phase(along))
        return target - touch_delta

    def drift_towards(self, target) -> tuple[complex, int]:
        thrust = 100
        distance = abs(self.position - self.cp)
        # print(f"--- {self.name} ---", file=sys.stderr)
        # print(f"dist: {int(distance)}, velo: {sum(self.speed_trace)}", file=sys.stderr)

        target_dev = math.remainder(cmath.phase(target - self.position) - self.v_angle, cmath.pi)
        next_cp_dev = math.remainder(self.v_angle - cmath.phase(self.next_cp - self.cp), cmath.pi)

        if distance <= sum(self.speed_trace):
            if self.speed_trace[-1] > 300:
                # change target sooner to allow rotation
                target = self.next_cp
            if abs(next_cp_dev) > math.pi / 2:
                thrust = 0
        else:
            if target_dev > 3*math.pi / 4:
                thrust = 0
            elif target_dev > math.pi / 2:
                thrust = 66

        return target, thrust

    def correct_rotation(self) -> complex:
        target_dev = math.remainder(cmath.phase(self.target - self.position) - self.v_angle, cmath.pi)
        desired = self.target - self.position
        rotate = cmath.rect(1, target_dev / 3)
        return desired * rotate + self.position

    @property
    def next_position(self):
        """lame predictor"""
        return self.position + self.velocity

    def defend_on_collision(self, opponents: Iterable[PodRacer]):
        for opp in opponents:
            # TODO: only large angles
            future_dist = int(round(abs(self.next_position - opp.next_position)))
            if future_dist <= 900:
                self.thurst = "SHIELD"
                return

    def can_boost(self, layout: dict) -> bool:
        if self.has_boost:
            # if self.cpid == layout["longest"]:
            target_dev = math.remainder(cmath.phase(self.target - self.position) - self.v_angle, cmath.pi)
            distance = abs(self.position - self.cp)
            if abs(target_dev) < cmath.pi / 36 and distance > 4000:
                return True
        return False

    def boost(self) -> None:
        if self.has_boost:
            self.thurst = "BOOST"
            self.has_boost = False


    def __str__(self):
        return (
            f"{int(round(self.target.real))} "
            f"{int(round(self.target.imag))} "
            f"{self.thurst}"
        )

    def __repr__(self):
        return (
            f"D:{int(round(abs(self.cp - self.position))):4} m "
            f"V:{int(round(abs(self.velocity))):4} m/s O:{self.thurst:4} "
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


def find_longest_segment(checkpoints):
    distances = [
        int(math.dist(z1, z2))
        for z1, z2 in zip([checkpoints[-1]] + checkpoints[:-1], checkpoints)
    ]
    longest = max(distances)
    return distances.index(longest)


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


def to_coords(z):
    return int(round(z.real)), int(round(z.imag))


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


def main():
    layout = read_race_layout()
    layout["longest"] = find_longest_segment(layout["checkpoints"])

    # first turn
    pods = read_all_pods()
    me1 = PodRacer("me1", pods["me_first"], layout["checkpoints"])
    me2 = PodRacer("me2", pods["me_second"], layout["checkpoints"])
    him1 = PodRacer("him1", pods["him_first"], layout["checkpoints"])
    him2 = PodRacer("him2", pods["him_second"], layout["checkpoints"])

    print(me1)
    print(me2)

    while True:
        pods = read_all_pods()
        me1.update(pods["me_first"], layout["checkpoints"])
        me2.update(pods["me_second"], layout["checkpoints"])

        him1.update(pods["him_first"], layout["checkpoints"])
        him2.update(pods["him_second"], layout["checkpoints"])

        if me1.can_boost(layout):
            me1.boost()
        elif me2.can_boost(layout):
            me2.boost()

        # me1.defend_on_collision((him1, him2))
        # me2.defend_on_collision((him2, him1))

        # if isinstance(me2.thurst, int):
        #     me2.thurst = me2.thurst // 2

        print(repr(me1), file=sys.stderr)
        print(repr(me2), file=sys.stderr)

        print(me1)
        print(me2)


if __name__ == "__main__":
    main()
