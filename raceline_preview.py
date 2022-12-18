from __future__ import annotations

import pygame

from picasso import PicassoEngine
from pod_utils import build_optimal_segments, build_bezier_path, pick_control_points, to_coords, cubic_bezier, Coord, BEZIER_DETAIL


BLACK = pygame.Color(0, 0, 0)
GRAY = pygame.Color(96, 96, 96)
RED = pygame.Color(255, 31, 31)
WHITE = pygame.Color(255, 255, 255)

SAMPLE_LAYOUT = {
    "lap_count": 3,
    "cp_count": 5,
    "checkpoints": [
        Coord(13050, 1919),
        Coord(6554, 7863),
        Coord(7490, 1379),
        Coord(12724, 7080),
        Coord(4053, 4660),
    ],
}


class RacelinePainter(PicassoEngine):
    def __init__(self):
        self.canvas_size = 16000, 9000
        self.window_size = 1600, 900
        super().__init__(self.window_size, "The beauty of Bezier Curve")
        self.window = pygame.Surface(self.window_size)

        self.layout = SAMPLE_LAYOUT["checkpoints"]
        self.curve = list()
        self.posi = 0

        self.live_curve = list()
        self.cp = self.layout[1]
        self.next_cp = self.layout[2]

    def on_paint(self):
        self.canvas = pygame.Surface(self.canvas_size)

        self.mark_points()
        # self.mark_segments()
        if len(self.curve) > 1:
            pygame.draw.lines(
                self.canvas, GRAY, closed=False, points=self.curve, width=13
            )
            position = self.curve[self.posi]
            pygame.draw.circle(self.canvas, WHITE, position, radius=100)

        if len(self.live_curve) > 1:
            pygame.draw.lines(
                self.canvas, RED, closed=False, points=self.live_curve, width=13
            )

        pygame.transform.scale(self.canvas, self.window_size, self.screen)

    def mark_points(self) -> None:
        for i, segment in enumerate(self.segments):
            a, b, c, d = segment
            pygame.draw.circle(self.canvas, WHITE, a, radius=55)
            labelSurface = self.font.render(str(i + 1), True, GRAY)
            aside = Coord(a.x + 89, a.y + 55)
            self.canvas.blit(labelSurface, aside)

    def mark_segments(self):
        for segment in self.segments:
            pygame.draw.lines(self.canvas, GRAY, False, segment, width=13)
            a, b, c, d = segment
            pygame.draw.circle(self.canvas, WHITE, a, radius=55)
            pygame.draw.circle(self.canvas, WHITE, b, radius=34)
            pygame.draw.circle(self.canvas, WHITE, c, radius=34)
            pygame.draw.circle(self.canvas, WHITE, d, radius=55)

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
            self.update_live_curve()
            print(f"--> {self.posi} / {len(self.curve)}")

        elif event.key == pygame.K_LEFT:
            self.posi -= 1
            self.update_live_curve()
            print(f"--> {self.posi} / {len(self.curve)}")

    def update_live_curve(self):
        self.posi %= len(self.curve)
        cpi = 1 + self.posi // (BEZIER_DETAIL - 1)
        self.live_curve = self.curve[self.posi:1 + cpi*(BEZIER_DETAIL - 1)]

    def post_init(self):
        self.font = pygame.font.SysFont("monospace", 168)
        self.segments = build_optimal_segments(self.layout)
        self.curve = build_bezier_path(self.segments)



def main():
    with RacelinePainter() as engine:
        engine.post_init()
        engine.run()


if __name__ == "__main__":
    main()
