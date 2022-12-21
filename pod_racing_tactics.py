from __future__ import annotations

from enum import Enum
from math import degrees, radians, remainder
from cmath import rect, polar, phase, pi
from collections import namedtuple, deque
from operator import itemgetter
import sys

from pod_utils import Coord, clamp, humangle, to_coords, thrust_value


CP_RADIUS = 600
CP_GRAVITY = CP_RADIUS // 10
TURN_SPEED = 400
HOLD_DURATION = 7


Pod = namedtuple("Pod", ["x", "y", "vx", "vy", "angle", "cpid"])


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


# ---- PodRacer start ----
RacerMood = Enum(
    "RacerMood", ["FULL_THROTTLE", "FINE_THROTTLE", "DRIFT", "BRAKE", "SHIELD"]
)


class PodRacer:
    def __init__(self, name, pod: Pod, checkpoints: list[Coord]) -> None:
        self.name = name
        self.has_boost = True
        self.speed_trace = deque(maxlen=4)
        self.mood = RacerMood.FULL_THROTTLE
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

        # dummy set target
        self.thrust = 100
        self.target = self.cp

    def __str__(self):
        return (
            f"{int(round(self.target.real))} "
            f"{int(round(self.target.imag))} "
            f"{self.thrust}"
        )

    def __repr__(self):
        return (
            f"TD:{int(round(abs(self.cp - self.position))):4} m "
            f"V:{int(round(abs(self.velocity))):4} m/s O:{self.thrust:3} "
            f"mood: {str(self.mood)} "
            f"<):{self.facing:4}° "
            f"has boost: {self.has_boost}"
        )

    def boost(self) -> None:
        if self.has_boost:
            self.thrust = "BOOST"
            self.has_boost = False

    @property
    def next_position(self):
        """projected next position considering current target"""
        thrust = thrust_value(self.thrust)
        t_angle = phase(self.target - self.position)
        dev = t_angle - self.angle
        rot = clamp(dev, -pi / 10, pi / 10)

        acc = rect(thrust, self.angle + rot)
        movement = self.velocity + acc
        new_position = self.position + movement

        return new_position

    def target_reach(
        self, use_target: complex, use_thrust: int | str
    ) -> tuple[int, complex, float]:
        thrust = thrust_value(use_thrust)

        position = self.position
        velocity = self.velocity
        angle = self.angle
        distance = int(round(abs(position - use_target)))

        step = 0
        while distance > (CP_RADIUS - CP_GRAVITY):
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

        return step, position, angle

    def target_drift_reach(
        self, use_target: complex, use_thrust: int | str, towards: complex
    ) -> tuple[int | None, complex, float]:
        thrust = thrust_value(use_thrust)

        position = self.position
        velocity = self.velocity
        angle = self.angle
        distance = int(round(abs(position - use_target)))

        step = 0
        while distance > (CP_RADIUS - CP_GRAVITY):
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

        return step, position, angle

    def evaluate(self):
        # how many steps to reach target
        steps, position, angle = self.target_reach(self.cp, 100)
        if steps > 4:
            self.mood = RacerMood.FULL_THROTTLE
            # maybe add over steering ?
            return self.cp, 100

        # we are closing in, evaluate drift
        drift_projections = dict()
        for acc in range(0, 101, 10):
            drift_steps, pos, angle = self.target_drift_reach(
                self.cp, acc, self.next_cp
            )
            if drift_steps is not None and drift_steps <= 4:
                dev = remainder(phase(self.next_cp - pos) - angle, 2 * pi)
                drift_projections[acc] = drift_steps, dev

        if drift_projections:
            best_acc = min(drift_projections, key=drift_projections.get)
            drift_steps, dev = drift_projections[best_acc]
            print(
                "reach by drift, in ",
                drift_steps,
                "steps",
                best_acc,
                "% facing",
                humangle(dev),
            )
            self.mood = RacerMood.DRIFT
            return self.next_cp, best_acc
        else:
            print("\tno drift needed")

        return self.cp, 100


# ---- PodRacer end ----


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

    # position is 0, 0
    pod.cp = complex(2_500, 0)
    pod.next_cp = complex(5_000, 3_000)
    pod.target = pod.cp
    pod.thrust = 100

    print(to_coords(pod.position), repr(pod))
    # step 1
    pod.target, pod.thrust = pod.evaluate()
    # move forward
    new_position = pod.next_position
    pod.velocity = (pod.next_position - pod.position) * 0.85
    pod.position = new_position

    print(to_coords(pod.position), repr(pod))

    # step 2
    pod.target, pod.thrust = pod.evaluate()
    # move forward
    new_position = pod.next_position
    pod.velocity = (pod.next_position - pod.position) * 0.85
    pod.position = new_position

    print(to_coords(pod.position), repr(pod))

    # step 3
    pod.target, pod.thrust = pod.evaluate()
    # move forward
    new_position = pod.next_position
    pod.velocity = (pod.next_position - pod.position) * 0.85
    pod.position = new_position

    print(to_coords(pod.position), repr(pod))

    # step 4
    pod.target, pod.thrust = pod.evaluate()
    # move forward
    new_position = pod.next_position
    pod.velocity = (pod.next_position - pod.position) * 0.85
    pod.position = new_position

    print(to_coords(pod.position), repr(pod))

    print("done")


if __name__ == "__main__":
    alt_main()
