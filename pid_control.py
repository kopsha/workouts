#!/usr/bin/env python3
import time
from collections import namedtuple


Coords = namedtuple("Coords", ("x", "y"))

actual = [
    7465,
    14949,
    22496,
    26723,
    31400,
    30278,
    41652,
    44566,
    34598,
    51410,
    30974,
    56745,
    54693,
    43409,
    39075,
    43252,
    43965,
    54914,
    47618,
    64159,
    48826,
    54376,
    32433,
    51236,
    67601,
]

TOP_SPEED = 30_000
LOW = 0
HIGH = 100


def PID(pk, ik, dk, initial_time):
    last_error = 0
    last_time = initial_time
    last_measured = 0
    output = 0
    proportional = 0
    integral = 0

    while True:
        set_point, measured, now = yield output
        error = set_point - measured
        delta_time = (now - last_time) * 1000
        delta_error = error - last_error

        proportional = pk * error
        integral += ik * error * delta_time
        derivative = dk * delta_error / delta_time

        output = proportional + integral + derivative
        # output = max(LOW, min(output, HIGH))
        print(f"({set_point:.1f}) {measured:10.0f} => {output:10.0f}")
        print(f"\t{error=:.1f}, {delta_error=:.1f}, {delta_time=:.1f}")
        print(f"\t{proportional=:.1f}, {integral=:.1f}, {derivative=:.1f}")

        # output = max(LOW, min(output, HIGH))
        last_error = error
        last_time = now


def main(path):
    print(path)

    last_time = time.monotonic()
    cc = PID(1, 1, 1, last_time)
    cc.send(None)
    time.sleep(0.13)

    for i in range(21):
        print(f"---- {i+1:03} ----")
        now = time.monotonic()
        delta_time = now - last_time
        acc = cc.send((TOP_SPEED, actual[i], now))

        time.sleep(0.13)
        last_time = now


def backup():
    while True:
        # read inputs
        x, y, cp_x, cp_y, cp_distance, angle = (int(i) for i in input().split())
        opponent = Coords(*(int(i) for i in input().split()))
        position = Coords(x, y)
        # target = Coords(cp_x, cp_y)
        target = Coords(0, y)
        now = time.monotonic()

        time_delta = now - last_time
        travel = distance(last_position, position)
        velocity = int(travel / time_delta)
        acc = HIGH
        better = pod_cc.send((TOP_SPEED, travel, now))

        if cp_distance < BRAKE_DISTANCE:
            if velocity > FAST:
                acc = 13
            elif velocity > SLOW:
                acc = 55
            else:  # too slow
                acc = 89

        if acc > 60 and abs(angle) > 45 and velocity > FAST:
            acc = 55

        print(f"{cp_distance=}, {angle=}", file=sys.stderr)
        print(f"{travel:.3f} {time_delta:.3f} {velocity}", file=sys.stderr)
        print(f"acc = {better}", file=sys.stderr)

        print(target.x, target.y, acc)
        last_position = position
        last_time = now


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser("download youtube videos")
    parser.add_argument("--to", dest="path", required=True, help="save files to ...")
    args = parser.parse_args()

    main(args.path.rstrip("/"))
