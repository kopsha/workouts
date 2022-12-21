from __future__ import annotations
from typing import Iterable

from math import degrees, radians, remainder
from cmath import rect, polar, phase, pi
from collections import namedtuple, deque
import sys

from pod_utils import Coord, clamp, humangle, to_coords


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
        self.speed_trace = deque(maxlen=4)
        self.update(pod, checkpoints)
        self.drift_count = 0
        self.drift_thrust = 0

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

    def oversteer_towards_target(self) -> None:
        t_angle = phase(self.target - self.position)
        deviation = remainder(t_angle - self.v_angle, 2 * pi)
        desired = self.target - self.position

        correction = clamp(deviation / 4, -pi / 10, pi / 10)
        new_target = desired * rect(1, correction) + self.position
        self.target = new_target

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

    def projection(self, use_target, use_thrust, steps=3):
        if use_thrust == "SHIELD":
            thrust = 0
        elif use_thrust == "BOOST":
            thrust = 650
        else:
            thrust = int(use_thrust)

        position = self.position
        velocity = self.velocity
        angle = self.angle

        for _ in range(steps):
            t_angle = phase(use_target - position)
            deviation = remainder(t_angle - angle, 2 * pi)
            angle += clamp(deviation, -pi / 10, pi / 10)
            movement = velocity + rect(thrust, angle)
            position += movement
            velocity = 0.85 * movement

        return position, angle

    def pick_drift_thrust(self):

        cp_reach = dict()
        for acc in range(0, 101, 10):
            pos, _ = self.projected_position(self.next_cp, acc)
            cp_dist = int(abs(pos - self.cp))
            cp_reach[acc] = cp_dist

        start = False
        for acc, dist in cp_reach.items():
            if dist < (CP_RADIUS - CP_GRAVITY):
                # start drifting at highest acc
                start = True
                thrust = acc
                self.drift_count = 3
                # print(f"{self.name} drifts >> {acc} => {dist}", file=sys.stderr)
                # print(f"{to_coords(self.projected_position(self.next_cp, acc))}", file=sys.stderr)
                break

        else:
            # print("no drift needed", file=sys.stderr)
            thrust = 100

        return start, thrust

    def drift_towards_checkpoint(self):
        thrust = 100
        target = self.cp

        if self.drift_count:
            target = self.next_cp
            thrust = self.drift_thrust
            self.drift_count -= 1
        else:
            should_drift, drift_thrust = self.pick_drift_thrust()
            if should_drift:
                target = self.next_cp
                self.drift_thrust = thrust = drift_thrust
                self.drift_count = 3
            else:
                t_angle = phase(self.cp - self.position)
                deviation = abs(remainder(t_angle - self.v_angle, 2 * pi))
                print(f"{self.name}> {humangle(deviation)}", file=sys.stderr)
                if deviation > 2 * pi / 3:
                    thrust = 25
                if deviation > pi / 2:
                    thrust = 50

        self.target = self.touch(target)
        self.thrust = thrust

    def evaluate(self):
        # tactics: full_throtle, fine_throtle, drift, break
        cp_reach = dict()

        for acc in range(0, 101, 10):
            pos, angle = self.projected_position(self.cp, acc)
            cp_dist = int(abs(pos - self.cp))
            cp_reach[acc] = cp_dist, angle

        print(cp_reach, file=sys.stderr)
        towards_cp = min(cp_reach, key=cp_reach.get)

        print(self.name, "towards cp", towards_cp, file=sys.stderr)

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
            f"TD:{int(round(abs(self.cp - self.position))):4} m "
            f"V:{int(round(abs(self.velocity))):4} m/s O:{self.thrust:4} "
            f"<):{self.facing}° "
            f"drift: {self.drift_count} "
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
        me1.oversteer_towards_target()

        me2.drift_towards_checkpoint()
        me2.oversteer_towards_target()

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

        me1.evaluate()

        print(me1)
        print(me2)


# ---- cut here ----


def alt_main():
    from pod_utils import SAMPLE5

    brake_ref = [
        (-504, 96),
        (-428, 81),
        (-363, 68),
        (-308, 57),
        (-261, 48),
        (-221, 40),
        (-187, 34),
        (-158, 28),
        (-134, 23),
        (-113, 19),
        (-96, 16),
        (-81, 13),
        (-68, 11),
        (-57, 9),
        (-48, 7),
        (-40, 5),
        (-34, 4),
        (-28, 3),
        (-23, 2),
        (-19, 1),
        (-16, 0),
        (-13, 0),
        (-11, 0),
        (-9, 0),
        (-7, 0),
        (-5, 0),
        (-4, 0),
        (-3, 0),
        (-2, 0),
        (-1, 0),
        (0, 0),
    ]

    shield_ref = [
        (-504, 96),
        (-428, 81),
        (-363, 68),
        (-308, 57),
        (-261, 48),
        (-221, 40),
        (-187, 34),
        (-158, 28),
        (-134, 23),
        (-113, 19),
        (-96, 16),
        (-81, 13),
        (-68, 11),
        (-57, 9),
        (-48, 7),
        (-40, 5),
        (-34, 4),
        (-28, 3),
        (-23, 2),
        (-19, 1),
        (-16, 0),
        (-13, 0),
        (-11, 0),
        (-9, 0),
        (-7, 0),
        (-5, 0),
        (-4, 0),
        (-3, 0),
        (-2, 0),
        (-1, 0),
        (0, 0),
    ]

    layout = SAMPLE5
    pc = Pod(x=0, y=0, vx=404, vy=0, angle=0, cpid=1)
    pod = PodRacer("me", pc, layout["checkpoints"])

    pod.target = complex(16000, 0)
    pod.thrust = 100

    pod.velocity = 504
    limiter = 0
    while abs(pod.velocity) > 1 and limiter < 20:
        pod.thrust = 50
        print(to_coords(pod.position), ">>", to_coords(pod.velocity))
        print("\t", to_coords(pod.projected_position(pod.target, pod.thrust)))
        new_position = pod.next_position
        pod.velocity = (pod.next_position - pod.position) * 0.85
        pod.position = new_position
        limiter += 1


if __name__ == "__main__":
    alt_main()
