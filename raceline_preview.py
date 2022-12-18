import pygame

from picasso import PicassoEngine
from pod_utils import find_control_points, to_coords, cubic_bezier, Coord, BEZIER_DETAIL


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

        self.mark_points(self.layout)
        pygame.draw.lines(self.canvas, GRAY, closed=False, points=self.curve, width=13)

        if len(self.live_curve) > 1:
            pygame.draw.lines(self.canvas, RED, closed=False, points=self.live_curve, width=13)

        position = self.curve[self.posi]
        pygame.draw.circle(self.canvas, WHITE, position, radius=100)

        pygame.transform.scale(self.canvas, self.window_size, self.screen)

    def mark_points(self, points: list[Coord]) -> None:
        for i, point in enumerate(points):
            pygame.draw.circle(self.canvas, WHITE, point, radius=55)
            labelSurface = self.font.render(str(i + 1), True, GRAY)
            aside = Coord(point.x + 89, point.y + 55)
            self.canvas.blit(labelSurface, aside)

    def on_click(self, event):
        pass

    def on_mouse_motion(self, event):
        pass

    def on_key(self, event):
        if event.key == pygame.K_ESCAPE:
            bye = pygame.event.Event(pygame.QUIT)
            pygame.event.post(bye)
        elif event.key == pygame.K_RIGHT:
            self.posi = (self.posi + 1) % len(self.curve)
            cpi = self.posi // (BEZIER_DETAIL - 2)
            self.cp = self.layout[cpi]
            self.cp = self.layout[(cpi + 1) % len(self.layout)]
            self.renew_curve(self.curve[self.posi], self.cp, self.next_cp)
            print(f"--> {self.posi} / {len(self.curve)}")
        elif event.key == pygame.K_LEFT:
            self.posi = (self.posi - 1) % len(self.curve)
            self.renew_curve(self.curve[self.posi], self.cp, self.next_cp)
            print(f"<-- {self.posi} / {len(self.curve)}")

    def post_init(self):
        self.font = pygame.font.SysFont("monospace", 168)
        last_mirror_cp = self.layout[0]

        for left, right, tow in zip(
            self.layout, self.layout[1:] + self.layout[:1], self.layout[2:] + self.layout[:2]
        ):
            position = complex(*left)
            target = complex(*right)
            towards = complex(*tow)
            zcp, mirror_zcp = find_control_points(position, target, towards)
            cp, mirror_cp = Coord(*to_coords(zcp)), Coord(*to_coords(mirror_zcp))

            curve = cubic_bezier(left, last_mirror_cp, cp, right)
            self.curve.extend(curve)
            last_mirror_cp = mirror_cp
        
    def renew_curve(self, position, target, towards):
        pos = complex(*position)
        tar = complex(*target)
        tow = complex(*towards)
        zcp, mirror_zcp = find_control_points(pos, tar, tow)
        cp, mirror_cp = Coord(*to_coords(zcp)), Coord(*to_coords(mirror_zcp))
        self.live_curve = cubic_bezier(position, position, cp, target)


def main():
    with RacelinePainter() as engine:
        engine.post_init()
        engine.run()


if __name__ == "__main__":
    main()
