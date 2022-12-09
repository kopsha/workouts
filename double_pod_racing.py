from __future__ import annotations

import math
import cmath
import sys
from collections import namedtuple


CP_RADIUS = 600
CP_GRAVITY = CP_RADIUS // 10
TURN_SPEED = 400

Coord = namedtuple("Coord", ["x", "y"])
Pod = namedtuple("Pod", ["x", "y", "vx", "vy", "angle", "cpid"])


class PodRacer:
    def __init__(self, name, pod: Pod, target: Coord) -> None:
        self.name = name
        self.position = complex(pod.x, pod.y)
        self.velocity = complex(pod.vx, pod.vy)
        self.angle = math.radians(pod.angle)
        self.target = self.touch(complex(*target))
        self.thurst = self.break_near_target(100)
        self.thurst = self.break_on_large_angles(self.thurst)
        self.has_boost = True

    def touch(self, target: complex) -> complex:
        """Will barely touch the checkpoint"""
        along = self.position - target
        touch_delta = cmath.rect(CP_GRAVITY - CP_RADIUS, cmath.phase(along))
        return target - touch_delta

    def break_near_target(self, thrust: int) -> int:
        """apply braking strategy based on distance to target"""
        distance = abs(self.position - self.target)
        if abs(self.velocity) > TURN_SPEED and distance < CP_RADIUS * 2:
            new_thrust = 34
        else:
            new_thrust = thrust

        return new_thrust

    def break_on_large_angles(self, thrust: int) -> int:
        """apply braking strategy based on angle to target"""
        target_angle = cmath.phase(self.target - self.position)
        if target_angle < 0:
            target_angle = 2 * cmath.pi + target_angle

        actual = abs(target_angle - self.angle)
        if actual < cmath.pi / 4:
            thrust = thrust
        elif actual < cmath.pi / 2:
            thrust = 66
        else:
            thrust = 34

        return thrust

    @property
    def next_position(self):
        """lame predictor"""
        return self.position + self.velocity

    def defend_on_collision(self, opponent: PodRacer):
        future_dist = int(round(abs(self.next_position - opponent.next_position)))
        if future_dist < 1200:
            print(self.name, future_dist, "m from", opponent.name, file=sys.stderr)
        if future_dist < 800:
            self.thurst = "SHIELD"

    def __str__(self):
        return (
            f"{int(round(self.target.real))} "
            f"{int(round(self.target.imag))} "
            f"{self.thurst}"
        )

    def __repr__(self):
        return f"V:{int(round(abs(self.velocity))):4} m/s O:{self.thurst:4}"


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


def boost_on_long_distance(thrust, c_dist, c_angle, c_index):
    # TODO: rework this
    if c_dist > 5000 and abs(c_angle) < 5:
        thrust = "BOOST"

    return thrust


def main():
    layout = read_race_layout()

    # first turn
    pods = read_all_pods()
    first_me = PodRacer(
        "me1", pods["me_first"], layout["checkpoints"][pods["me_first"].cpid]
    )
    second_me = PodRacer(
        "me2", pods["me_second"], layout["checkpoints"][pods["me_second"].cpid]
    )

    first_me.thurst = "BOOST"
    print(first_me)
    print(second_me)

    while True:
        pods = read_all_pods()
        first_me = PodRacer(
            "me1", pods["me_first"], layout["checkpoints"][pods["me_first"].cpid]
        )
        second_me = PodRacer(
            "me2", pods["me_second"], layout["checkpoints"][pods["me_second"].cpid]
        )
        him1 = PodRacer(
            "him1", pods["him_first"], layout["checkpoints"][pods["him_first"].cpid]
        )
        him2 = PodRacer(
            "him2", pods["him_second"], layout["checkpoints"][pods["him_second"].cpid]
        )

        # print(repr(first_me), pods["me_first"], file=sys.stderr)
        # print(repr(second_me), pods["me_second"], file=sys.stderr)

        # second_me.thurst = 55

        first_me.defend_on_collision(him1)
        first_me.defend_on_collision(him2)
        second_me.defend_on_collision(him1)
        second_me.defend_on_collision(him2)

        print(first_me)
        print(second_me)


if __name__ == "__main__":
    main()
