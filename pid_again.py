import math
import cmath
import sys


CHECKPOINT_RADIUS = 600
checkpoints = list()
longest_segment = None
last_checkpoint = (None, None)
lap = 1


def read_inputs():
    global last_checkpoint
    global lap
    global longest_segment
    global checkpoints
    x, y, cx, cy, c_distance, c_angle = map(int, input().split())
    opx, opy = map(int, input().split())
    position = complex(x, y)
    checkpoint = complex(cx, cy)
    opponent = complex(opx, opy)

    cp = cx, cy
    c_index = None
    if cp != last_checkpoint:
        if cp in checkpoints:
            if checkpoints.index(cp) == 0:
                lap += 1
                longest_segment = compute_distances(checkpoints)
        else:
            checkpoints.append(cp)

    last_checkpoint = cp
    c_index = checkpoints.index(cp)

    return position, opponent, checkpoint, c_distance, c_angle, c_index


def compute_distances(checkpoints):
    distances = [int(math.dist(z1, z2)) for z1, z2 in zip([checkpoints[-1]] + checkpoints[:-1], checkpoints)]
    longest = max(distances)
    return distances.index(longest)


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


def break_on_large_angles(c_angle):
    """apply braking strategy based on angle to target"""

    angle = abs(c_angle)
    if angle < 45:
        thrust = 100
    elif angle < 90:
        thrust = 66
    else:
        thrust = 34

    return thrust

def boost_on_long_distance(thrust, has_boost, c_angle, c_index):
    if has_boost and abs(c_angle) < 10 and lap > 1 and longest_segment == c_index:
        has_boost = False
        thrust = "BOOST"

    return has_boost, thrust


def main():
    has_boost = True

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

    while True:
        position, opponent, checkpoint, c_distance, c_angle, c_index = read_inputs()
        target = closer_target(position, checkpoint, CHECKPOINT_RADIUS//10)

        actual = last_position - position
        desired = target - position
        deviation = math.remainder(cmath.phase(actual) - cmath.phase(desired), cmath.pi)
        rotate = cmath.rect(1, -deviation/3)
        target = desired * rotate + position  # apply correction

        # apply braking based on angle
        thrust = break_on_large_angles(c_angle)

        # apply boost strategy
        has_boost, thrust = boost_on_long_distance(thrust, has_boost, c_angle, c_index)

        print(f"LAP {lap}: {c_distance:5}m, {c_angle:4}°, {has_boost}", file=sys.stderr)
        distances = [int(math.dist(z1, z2)) for z1, z2 in zip(checkpoints, checkpoints[1:] + [checkpoints[0]])]
        print(f"CP: {checkpoints}", file=sys.stderr)
        print(f"D: {distances}", file=sys.stderr)
        print(f"Current: {c_index}, Longest: {longest_segment}", file=sys.stderr)
        print(*coords(target), thrust)

        last_position = position
        last_opponent_ = opponent
        last_target = target


if __name__ == "__main__":
    # To debug: print("Debug messages...", file=sys.stderr)
    main()
