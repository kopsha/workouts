from __future__ import annotations

from cmath import phase, pi
from math import remainder
from random import randint

import pygame

from picasso import PicassoEngine
from pod_utils import (BEZIER_DETAIL, Coord, build_bezier_path,
                       build_optimal_segments)

BLACK = pygame.Color(0, 0, 0)
GRAY = pygame.Color(96, 96, 96)
LIGHTBLUE = pygame.Color(63, 63, 255)
RED = pygame.Color(255, 31, 31)
GREEN = pygame.Color(31, 255, 31)
YELLOW = pygame.Color(255, 255, 63)
WHITE = pygame.Color(255, 255, 255)


class RacelinePainter(PicassoEngine):
    def __init__(self, layout):
        self.canvas_size = 16000, 9000
        self.window_size = 1600, 900
        super().__init__(self.window_size, "The beauty of Bezier Curve")
        self.window = pygame.Surface(self.window_size)

        self.layout = layout
        self.curve = list()
        self.live_curve = list()

    def post_init(self):
        self.font = pygame.font.SysFont("sans-serif", 200)

        self.cpid = 1
        self.cp = self.layout[self.cpid]
        self.next_cp = self.layout[self.cpid + 1]

        self.segments = build_optimal_segments(self.layout)
        self.curve = build_bezier_path(self.segments)
        # self.curve.append(self.layout[0])

        self.last_position = self.curve[0]
        self.posi = 0
        self.position = self.pick_position_around()
        self.find_nearest_entry()

    def on_paint(self):
        self.canvas = pygame.Surface(self.canvas_size)

        self.mark_points()
        # self.mark_segments()
        if len(self.curve) > 1:
            pygame.draw.lines(
                self.canvas, GRAY, closed=False, points=self.curve, width=13
            )
            pygame.draw.line(
                self.canvas, GRAY, self.last_position, self.position, width=10
            )
            pygame.draw.circle(self.canvas, GRAY, self.last_position, radius=72)
            pygame.draw.circle(self.canvas, YELLOW, self.position, radius=100)

        if len(self.live_curve) > 1:
            pygame.draw.lines(
                self.canvas, RED, closed=False, points=self.live_curve, width=13
            )

        if self.target is not None:
            pygame.draw.circle(self.canvas, WHITE, self.target, radius=89)

        pygame.transform.scale(self.canvas, self.window_size, self.screen)

    def mark_points(self) -> None:
        for i, segment in enumerate(self.segments):
            a, b, c, d = segment
            pygame.draw.circle(
                self.canvas, RED if i == self.cpid else GREEN, a, radius=55
            )
            labelSurface = self.font.render(str(i + 1), True, LIGHTBLUE)
            aside = Coord(a.x + 89, a.y + 55)
            self.canvas.blit(labelSurface, aside)

    def mark_segments(self):
        for segment in self.segments:
            pygame.draw.lines(self.canvas, GRAY, False, segment, width=13)
            a, b, c, d = segment
            pygame.draw.circle(self.canvas, GREEN, a, radius=55)
            pygame.draw.circle(self.canvas, WHITE, b, radius=34)
            pygame.draw.circle(self.canvas, WHITE, c, radius=34)
            pygame.draw.circle(self.canvas, GREEN, d, radius=55)

    def on_click(self, event):
        pass

    def on_mouse_motion(self, event):
        pass

    def on_key(self, event):
        if event.key == pygame.K_ESCAPE:
            bye = pygame.event.Event(pygame.QUIT)
            pygame.event.post(bye)
        elif event.key == pygame.K_RIGHT:
            self.posi += 1
            self.last_position = self.position
            self.position = self.pick_position_around()
            self.find_nearest_entry()
            print(f"--> {self.posi} / {len(self.curve)}")

        elif event.key == pygame.K_LEFT:
            self.posi -= 1
            self.position = self.pick_position_around()
            self.last_position = self.curve[self.posi]  # hack
            self.find_nearest_entry()
            print(f"--> {self.posi} / {len(self.curve)}")

    def pick_position_around(self):
        self.posi %= len(self.curve)
        dx, dy = randint(5, 233), randint(5, 233)
        on_path = self.curve[self.posi]

        if self.posi == self.cpid * (BEZIER_DETAIL - 1):
            self.cpid = (self.cpid + 1) % len(self.segments)
            self.cp = self.layout[self.cpid]
            self.next_cp = self.layout[(self.cpid + 1) % len(self.segments)]

        return Coord(on_path.x + dx, on_path.y + dy)

    def find_nearest_entry(self):
        """
        Given current position and existing bezier curve, finds the best
        point to re-enter the path
        """
        self.target = self.curve[self.cpid * (BEZIER_DETAIL - 1)]

        position = complex(*self.position)
        last_position = complex(*self.last_position)
        facing = phase(position - last_position)

        seg_count = len(self.segments)
        seg_len = BEZIER_DETAIL - 1
        start = self.cpid * seg_len
        stop = ((self.cpid - 1) % seg_count) * seg_len

        nearest = start
        point = complex(*self.curve[start])
        dist = abs(point - position)
        delta = remainder(facing - phase(point - position), 2 * pi)
        best = dist * delta**2

        if start == 0:
            start = len(self.curve) - 1

        # print(start, int(dist), int(degrees(delta)), int(best), "stopping at", stop)

        for i in range(start - 1, stop, -1):
            point = complex(*self.curve[i])
            dist = abs(point - position)
            delta = remainder(facing - phase(point - position), 2 * pi)
            kf = dist * delta**2
            # print(i, int(dist), int(degrees(delta)), int(kf))
            if kf < best:
                best = kf
                nearest = i

        self.target = self.curve[nearest]


def main():
    from pod_utils import SAMPLE2 as SAMPLE

    with RacelinePainter(layout=SAMPLE["checkpoints"]) as engine:
        engine.post_init()
        engine.run()


if __name__ == "__main__":
    main()
