from __future__ import annotations
from typing import Union
from math import degrees, radians, remainder
from cmath import rect, polar, phase, pi
from collections import namedtuple, deque
import sys

from pod_utils import Coord, Pod, clamp, humangle, to_coords, thrust_value


CP_RADIUS = 600
CP_GRAVITY = CP_RADIUS // 10
HOLD_DURATION = 7


# ---- PodRacer start ----
class PodRacer:
    def __init__(self, name, pod: Pod, checkpoints: list[Coord]) -> None:
        self.name = name
        self.has_boost = True
        self.speed_trace = deque(maxlen=4)
        self.cpid = int
        self.next_cp = self.cp = self.target = complex
        self.last_position = self.position = self.velocity = complex
        self.angle = float
        self.thrust = int
        self.update(pod, checkpoints)

    def update(self, pod: Pod, checkpoints: list[Coord]) -> None:
        self.last_position = self.position

        self.cpid = pod.cpid
        self.position = complex(pod.x, pod.y)
        self.angle = radians(pod.angle)
        self.velocity = complex(pod.vx, pod.vy)
        self.speed_trace.append(int(round(abs(self.velocity))))

        self.cp = complex(*checkpoints[pod.cpid])
        self.next_cp = complex(*checkpoints[(pod.cpid + 1) % len(checkpoints)])

        # set dummy target
        self.thrust = 100
        self.target = self.cp

    def __str__(self):
        return f"{int(round(self.target.real))} {int(round(self.target.imag))} {self.thrust}"

    def __repr__(self):
        return (
            f"TD:{int(round(abs(self.cp - self.position))):4}m, "
            f"V:{int(round(abs(self.velocity))):4} m/s, O:{self.thrust:3} "
            f"<):{humangle(self.angle):4}° boost: {int(self.has_boost)}"
        )

    def boost(self) -> None:
        if self.has_boost:
            self.thrust = "BOOST"
            self.has_boost = False

    @property
    def next_position(self) -> complex:
        """projected next position considering current target"""
        thrust = thrust_value(self.thrust)
        t_angle = phase(self.target - self.position)
        dev = t_angle - self.angle
        rot = clamp(dev, -pi / 10, pi / 10)

        acc = rect(thrust, self.angle + rot)
        movement = self.velocity + acc
        new_position = self.position + movement

        return new_position

    def projection(
        self,
        use_target: complex,
        use_thrust: int | str,
        max_steps: int = 5,
    ) -> tuple[int, complex, float]:
        """Will stop if target is reached sooner than max_steps"""

        thrust = thrust_value(use_thrust)
        position = self.position
        velocity = self.velocity
        angle = self.angle
        distance = int(round(abs(position - use_target)))

        step = 0
        while distance > (CP_RADIUS - CP_GRAVITY) and step < max_steps:
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

        return step, position, angle, velocity

    def drift_projection(
        self,
        use_target: complex,
        use_thrust: int | str,
        towards: complex,
        max_steps: int = 5,
    ) -> tuple[int | None, complex, float]:
        """Will stop if target is reached sooner than max_steps"""

        thrust = thrust_value(use_thrust)
        position = self.position
        velocity = self.velocity
        angle = self.angle
        distance = int(round(abs(position - use_target)))

        step = 0
        while distance > (CP_RADIUS - CP_GRAVITY) and step < max_steps:
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

        return step, position, angle, velocity
# ---- PodRacer end ----


def alt_main():
    from pod_utils import SAMPLE5

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
