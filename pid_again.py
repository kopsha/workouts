import math
import cmath

from collections import deque


TURN_SPEED = 300
TOP_SPEED = 600
CHECKPOINT_RADIUS = 600
checkpoints = list()
last_checkpoint = (None, None)


def read_inputs():
    x, y, cx, cy, c_distance, c_angle = map(int, input().split())
    opx, opy = map(int, input().split())
    position = complex(x, y)
    checkpoint = complex(cx, cy)
    opponent = complex(opx, opy)

    cp = cx, cy
    c_index = None
    if cp != last_checkpoint:
        if cp in checkpoints:
            c_index = checkpoints.index(cp)
        else:
            c_index = len(checkpoints)
            checkpoints.append(cp)

    return position, opponent, checkpoint, c_distance, c_angle, c_index


def coords(cpoint):
    return int(cpoint.real), int(cpoint.imag)


def closer_target(position, checkpoint, gravity):
    along = position - checkpoint
    touchdelta = cmath.rect(gravity - CHECKPOINT_RADIUS, cmath.phase(along))
    return checkpoint - touchdelta


def inv_lerp(left: float, right: float, v: float) -> float:
    """
    Inverse Linar Interpolation, get the fraction between a and b on which v resides.
    Examples
    --------
        0.5 == inv_lerp(0, 100, 50)
        0.8 == inv_lerp(1, 5, 4.2)
    """
    return (v - left) / (right - left)


def main():
    boost = 1

    # first loop
    (
        last_position,
        last_opponent,
        last_target,
        c_distance,
        c_angle,
        c_index,
    ) = read_inputs()
    thrust = 100
    print(*coords(last_target), thrust)

    max_speed = 0

    while True:
        position, opponent, checkpoint, c_distance, c_angle, c_index = read_inputs()
        target = closer_target(position, checkpoint, CHECKPOINT_RADIUS // 10)
        velocity = position - last_position

        speed = int(abs(velocity))
        max_speed = max(speed, max_speed)

        angle = abs(c_angle)
        if angle < 45:
            thrust = 100
        elif angle < 90:
            thrust = 55
        else:
            thrust = 34

        actual = last_position - position
        desired = target - position
        deviation = math.remainder(cmath.phase(actual) - cmath.phase(desired), cmath.pi)
        rotate = cmath.rect(1, -deviation / 3)
        target = desired * rotate + position  # apply correction

        print(*coords(target), thrust)

        last_position = position
        last_opponent_ = opponent
        last_target = target


if __name__ == "__main__":
    # To debug: print("Debug messages...", file=sys.stderr)
    main()
