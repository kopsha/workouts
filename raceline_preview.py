import pygame

from picasso import PicassoEngine
from pod_utils import find_control_points, to_coords, cubic_bezier, Coord


BLACK = pygame.Color(0, 0, 0)
GRAY = pygame.Color(96, 96, 96)
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
        self.canvas = pygame.Surface(self.canvas_size)
        self.window = pygame.Surface(self.window_size)

    def on_paint(self):
        pygame.transform.scale(self.canvas, self.window_size, self.window)
        self.screen.blit(self.window, (0, 0))

    def on_click(self, event):
        pass

    def on_mouse_motion(self, event):
        pass

    def on_key(self, event):
        if event.key == pygame.K_ESCAPE:
            bye = pygame.event.Event(pygame.QUIT)
            pygame.event.post(bye)

    def post_init(self):
        self.font = pygame.font.SysFont("monospace", 168)

        layout = SAMPLE_LAYOUT["checkpoints"]
        self.mark_points(layout)

        last_mirror_cp = layout[0]
        cps = list()
        fcps = list()

        for left, right, tow in zip(
            layout, layout[1:] + layout[:1], layout[2:] + layout[:2]
        ):

            print(
                layout.index(left), "->", layout.index(right), "->", layout.index(tow)
            )

            position = complex(*left)
            target = complex(*right)
            towards = complex(*tow)
            zcp, mirror_zcp = find_control_points(position, target, towards)
            cp, mirror_cp = Coord(*to_coords(zcp)), Coord(*to_coords(mirror_zcp))

            fcps.append(cp)
            cps.append(last_mirror_cp)

            curve = cubic_bezier(left, last_mirror_cp, cp, right)
            pygame.draw.lines(self.canvas, GRAY, closed=False, points=curve, width=13)
            last_mirror_cp = mirror_cp

        self.mark_control_points(fcps)
        self.mark_control_points(cps, prefix="__")

    def mark_points(self, points: list[Coord]) -> None:
        for i, point in enumerate(points):
            pygame.draw.circle(self.canvas, WHITE, point, radius=100)
            labelSurface = self.font.render(str(i + 1), True, GRAY)
            aside = Coord(point.x + 89, point.y + 55)
            self.canvas.blit(labelSurface, aside)

    def mark_control_points(self, points: list[Coord], prefix="") -> None:
        for i, point in enumerate(points):
            pygame.draw.circle(self.canvas, WHITE, point, radius=34)
            labelSurface = self.font.render(f"{prefix}z{i}", True, GRAY)
            aside = (point.x + 89, point.y - 144)
            self.canvas.blit(labelSurface, aside)


def main():
    with RacelinePainter() as engine:
        engine.post_init()
        engine.run()


if __name__ == "__main__":
    main()
