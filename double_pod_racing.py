from __future__ import annotations
from typing import Union
import math
import cmath
import sys
from collections import namedtuple, deque


CP_RADIUS = 600
CP_GRAVITY = CP_RADIUS // 10
TURN_SPEED = 400

Coord = namedtuple("Coord", ["x", "y"])
Pod = namedtuple("Pod", ["x", "y", "vx", "vy", "angle", "cpid"])


def clamp(x, left, right):
    return max(min(left, x), right)


class PodRacer:
    def __init__(self, name, pod: Pod, checkpoints: list[Coord]) -> None:
        self.name = name
        self.speed_trace = deque(maxlen=4)
        self.update(pod, checkpoints)

    def update(self, pod: Pod, checkpoints: list[Coord]) -> None:
        self.position = complex(pod.x, pod.y)
        self.velocity = complex(pod.vx, pod.vy)
        self.speed_trace.append(int(round(abs(self.velocity))))
        self.angle = math.radians(pod.angle)

        self.cp = complex(*checkpoints[pod.cpid])
        self.next_cp = complex(*checkpoints[(pod.cpid + 1) % len(checkpoints)])
        self.target = self.cp

        self.target, self.thurst = self.drift_towards_target()
        self.correct_rotation()

    def touch(self, target: complex) -> complex:
        """Will barely touch the checkpoint"""
        along = self.position - target
        touch_delta = cmath.rect(CP_GRAVITY - CP_RADIUS, cmath.phase(along))
        return target - touch_delta

    def drift_towards_target(self) -> tuple[complex, int]:

        distance = abs(self.position - self.cp)
        thrust = 100
        target = self.cp

        print("sum", sum(self.speed_trace), file=sys.stderr)

        if distance <= sum(self.speed_trace):

            target = self.next_cp

            desired = self.next_cp - self.position
            deviation = math.remainder(cmath.phase(self.velocity) - cmath.phase(desired), math.pi)
            print(f"{self.name}>", math.degrees(abs(deviation)), file=sys.stderr)
            if abs(deviation) > math.pi / 3:
                thrust = 0


        return target, thrust

    def correct_rotation(self):
        actual = self.velocity
        desired = self.target - self.position
        deviation = math.remainder(cmath.phase(actual) - cmath.phase(desired), cmath.pi)

        # print(f"Dev: {round(math.degrees(deviation))}", file=sys.stderr)

        rotate = cmath.rect(1, -deviation / 4)
        self.target = desired * rotate + self.position  # apply correction


    def break_near_target(self, thrust: int) -> Union[int, str]:
        """apply braking strategy based on distance to target"""
        distance = abs(self.position - self.target)
        if abs(self.velocity) > TURN_SPEED and distance < CP_RADIUS * 2:
            new_thrust = 0
        else:
            new_thrust = thrust

        return new_thrust

    def break_on_large_angles(self, thrust: Union[int, str]) -> Union[int, str]:
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
            thrust = 0

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
        return f"D:{int(round(abs(self.cp - self.position))):4} m V:{int(round(abs(self.velocity))):4} m/s O:{self.thurst:4}"


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
        "me1", pods["me_first"], layout["checkpoints"]
    )
    second_me = PodRacer(
        "me2", pods["me_second"], layout["checkpoints"]
    )

    first_me.thurst = 0
    second_me.thurst = "BOOST"
    print(first_me)
    print(second_me)

    while True:
        pods = read_all_pods()
        first_me.update(pods["me_first"], layout["checkpoints"])
        second_me.update(pods["me_second"], layout["checkpoints"])

        print(repr(first_me), file=sys.stderr)
        print(repr(second_me), file=sys.stderr)

        print(first_me)
        print(second_me)


if __name__ == "__main__":
    main()
