import cmath
import math
import sys

TURN_SPEED = 400
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
    distances = [
        int(math.dist(z1, z2))
        for z1, z2 in zip([checkpoints[-1]] + checkpoints[:-1], checkpoints)
    ]
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


def break_on_large_angles(thrust, c_angle):
    """apply braking strategy based on angle to target"""

    angle = abs(c_angle)
    if angle < 45:
        thrust = thrust
    elif angle < 90:
        thrust = 66
    else:
        thrust = 34

    return thrust


def break_on_close_target(c_dist, velocity):
    """apply braking strategy based on distance to target"""

    thrust = 100
    if abs(velocity) > TURN_SPEED:
        if c_dist < CHECKPOINT_RADIUS * 1.4:
            thrust = 34
        # elif c_dist < CHECKPOINT_RADIUS * 2.8:
        #     thrust = 66

    return thrust


def steer_towards_opponent(target, position, opponent, last_opponent):
    ph1 = cmath.phase(target - position)
    ph2 = cmath.phase(opponent - last_opponent)
    opp_angle = abs(math.remainder(ph1 - ph2, cmath.pi))

    opponent_dist = abs(position - opponent)
    if opp_angle < cmath.pi / 5 and opponent_dist <= CHECKPOINT_RADIUS * 3:
        print(f"Opp angle: {math.degrees(opp_angle):.1f}°", file=sys.stderr)
        x = (target.real * 2 + opponent.real) / 3
        y = (target.imag * 2 + opponent.imag) / 3
        target = complex(x, y)
    return target


def boost_on_long_distance(thrust, c_dist, c_angle, c_index):
    if c_dist > 5000 and abs(c_angle) < 5 and lap > 1 and longest_segment == c_index:
        thrust = "BOOST"

    return thrust


def main():
    # first loop
    (
        last_position,
        last_opponent,
        last_target,
        c_distance,
        c_angle,
        c_index,
    ) = read_inputs()
    thrust = "BOOST"
    print(*coords(last_target), thrust)

    while True:
        position, opponent, checkpoint, c_distance, c_angle, c_index = read_inputs()
        target = closer_target(position, checkpoint, CHECKPOINT_RADIUS // 10)

        actual = last_position - position
        desired = target - position
        deviation = math.remainder(cmath.phase(actual) - cmath.phase(desired), cmath.pi)
        rotate = cmath.rect(1, -deviation / 4)
        target = desired * rotate + position  # apply correction

        target = steer_towards_opponent(target, position, opponent, last_opponent)
        thrust = break_on_close_target(c_distance, velocity=actual)
        thrust = break_on_large_angles(thrust, c_angle)

        # thrust = boost_on_long_distance(thrust, c_distance, c_angle, c_index)

        print(
            f"LAP {lap}: {int(abs(actual)):3}m/s, {c_distance:5}m, {c_angle:4}°",
            file=sys.stderr,
        )
        print(*coords(target), thrust)

        last_position = position
        last_opponent = opponent
        last_target = target


if __name__ == "__main__":
    # To debug: print("Debug messages...", file=sys.stderr)
    main()
