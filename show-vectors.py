#!/usr/bin/env python3
import matplotlib.pyplot as plt
import cmath
from math import degrees


def real_of(numbers):
    return [c.real for c in numbers]


def imag_of(numbers):
    return [c.imag for c in numbers]


def coords(z):
    return z.real, z.imag


def main():
    origin = complex(0, 0)
    limit = complex(12, 12)
    pos = complex(10, 5)
    target = complex(8, 9)
    velocity = complex(8, 10)

    v1 = pos, target - pos
    v2 = pos, velocity - pos

    # current position is the origin
    ovelocity = velocity - pos
    otarget = target - pos
    velo_phase = cmath.phase(ovelocity)
    targ_phase = cmath.phase(otarget)
    shift = velo_phase - targ_phase

    correction = cmath.rect(1, -shift / 3)
    new_target = otarget * correction

    print(
        f"{degrees(velo_phase):.1f} - {degrees(targ_phase):.1f} = {degrees(shift):.1f}"
    )

    me_list = [origin, limit, pos, target, velocity, correction]
    names = ["O", "#", "pos", "target", "velocity", "corr"]

    fig, ax = plt.subplots()
    ax.axis("equal")

    for i, p in enumerate(me_list):
        x = p - pos
        plt.scatter((x.real,), (x.imag,))
        ax.annotate(names[i], coords(x))

    plt.quiver(*coords(target - pos), angles="xy", scale_units="xy", scale=1)
    plt.quiver(*coords(velocity - pos), angles="xy", scale_units="xy", scale=1)
    plt.quiver(*coords(new_target), angles="xy", scale_units="xy", scale=1)

    fig.tight_layout()

    plt.show()


if __name__ == "__main__":
    # To debug: print("Debug messages...", file=sys.stderr)
    main()
