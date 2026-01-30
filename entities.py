from __future__ import annotations
from dataclasses import dataclass, field
import random
import pygame

from settings import TILE


# =====================
# Player (the chick)
# =====================
@dataclass
class Player:
    gx: int
    gy: int
    alive: bool = True
    score: int = 0

    def rect_world(self) -> pygame.Rect:
        return pygame.Rect(self.gx * TILE, self.gy * TILE, TILE, TILE)

    def draw(self, screen: pygame.Surface, camera_y_px: float) -> None:
        x = self.gx * TILE
        y = self.gy * TILE
        sy = screen.get_height() - (y - camera_y_px) - TILE

        cx = x + TILE // 2
        cy = sy + TILE // 2

        # Body
        body = pygame.Rect(0, 0, int(TILE * 0.78), int(TILE * 0.68))
        body.center = (cx, cy + 2)
        pygame.draw.ellipse(screen, (250, 225, 110), body)

        # Head
        head_r = int(TILE * 0.22)
        head_center = (cx + int(TILE * 0.18), cy - int(TILE * 0.12))
        pygame.draw.circle(screen, (255, 235, 140), head_center, head_r)

        # Beak
        beak = [
            (head_center[0] + head_r - 1, head_center[1]),
            (head_center[0] + head_r + int(TILE * 0.16), head_center[1] - int(TILE * 0.06)),
            (head_center[0] + head_r + int(TILE * 0.16), head_center[1] + int(TILE * 0.06)),
        ]
        pygame.draw.polygon(screen, (245, 150, 60), beak)

        # Eye
        pygame.draw.circle(
            screen,
            (30, 30, 30),
            (head_center[0] + int(TILE * 0.06), head_center[1] - int(TILE * 0.04)),
            max(2, TILE // 18),
        )

        # Wing
        wing = pygame.Rect(0, 0, int(TILE * 0.34), int(TILE * 0.22))
        wing.center = (cx - int(TILE * 0.10), cy + int(TILE * 0.05))
        pygame.draw.ellipse(screen, (240, 205, 95), wing)

        # Feet
        foot_y = sy + int(TILE * 0.80)
        pygame.draw.line(
            screen, (200, 120, 40),
            (cx - int(TILE * 0.12), foot_y),
            (cx - int(TILE * 0.12), foot_y + int(TILE * 0.12)), 3
        )
        pygame.draw.line(
            screen, (200, 120, 40),
            (cx + int(TILE * 0.02), foot_y),
            (cx + int(TILE * 0.02), foot_y + int(TILE * 0.12)), 3
        )


# =====================
# Base moving entity
# =====================
@dataclass
class MovingEntity:
    x_px: float
    gy: int
    w_tiles: int
    speed_px: float
    direction: int  # +1 right, -1 left
    base_speed_px: float = 0.0  # NEW: lane base speed for scaling

    def rect_world(self) -> pygame.Rect:
        return pygame.Rect(int(self.x_px), self.gy * TILE, self.w_tiles * TILE, TILE)

    def update(self, dt: float) -> None:
        self.x_px += self.speed_px * dt * self.direction

    def _screen_y(self, screen: pygame.Surface, camera_y_px: float) -> int:
        y = self.gy * TILE
        return screen.get_height() - (y - camera_y_px) - TILE


# =====================
# Car (sedan or bus)
# =====================
def _rand_car_color() -> tuple[int, int, int]:
    palette = [
        (230, 80, 80),   (80, 160, 230), (240, 200, 70),
        (120, 210, 120), (200, 120, 230), (235, 235, 235),
        (40, 40, 45),    (210, 140, 70)
    ]
    return random.choice(palette)

@dataclass
class Car(MovingEntity):
    body_color: tuple[int, int, int] = field(default_factory=_rand_car_color)

    def draw(self, screen: pygame.Surface, camera_y_px: float) -> None:
        sy = self._screen_y(screen, camera_y_px)
        x = int(self.x_px)
        w = self.w_tiles * TILE
        h = TILE

        if self.w_tiles == 1:
            self._draw_sedan(screen, x, sy, w, h)
        else:
            self._draw_bus(screen, x, sy, w, h)

    def _draw_sedan(self, screen: pygame.Surface, x: int, y: int, w: int, h: int) -> None:
        body = pygame.Rect(x + 2, y + h//3, w - 4, h - h//3 - 2)
        pygame.draw.rect(screen, self.body_color, body, border_radius=7)

        roof = pygame.Rect(x + w//6, y + h//5, w - 2*(w//6), h//3)
        pygame.draw.rect(screen, tuple(max(0, c - 25) for c in self.body_color), roof, border_radius=7)

        win = pygame.Rect(roof.x + 3, roof.y + 3, roof.w - 6, roof.h - 6)
        pygame.draw.rect(screen, (190, 220, 255), win, border_radius=6)

        wheel_r = max(3, h // 7)
        pygame.draw.circle(screen, (25, 25, 28), (x + w//4, y + h - 4), wheel_r)
        pygame.draw.circle(screen, (25, 25, 28), (x + 3*w//4, y + h - 4), wheel_r)

        if self.direction == 1:
            pygame.draw.rect(screen, (255, 235, 170), (x + w - 6, y + h//2, 4, 5), border_radius=2)
        else:
            pygame.draw.rect(screen, (255, 90, 90), (x + 2, y + h//2, 4, 5), border_radius=2)

    def _draw_bus(self, screen: pygame.Surface, x: int, y: int, w: int, h: int) -> None:
        body = pygame.Rect(x + 2, y + h//5, w - 4, h - h//5 - 2)
        pygame.draw.rect(screen, self.body_color, body, border_radius=6)

        stripe = pygame.Rect(body.x + 2, body.y + body.h//2, body.w - 4, 4)
        pygame.draw.rect(screen, tuple(max(0, c - 35) for c in self.body_color), stripe, border_radius=2)

        n = 3 if w <= 2*TILE else 4
        pad = 4
        win_w = (body.w - (n+1)*pad) // n
        win_h = body.h // 3
        wy = body.y + pad
        for i in range(n):
            wx = body.x + pad + i*(win_w + pad)
            pygame.draw.rect(screen, (190, 220, 255), (wx, wy, win_w, win_h), border_radius=4)

        wheel_r = max(3, h // 7)
        wheel_y = y + h - 4
        pygame.draw.circle(screen, (25, 25, 28), (x + w//5, wheel_y), wheel_r)
        pygame.draw.circle(screen, (25, 25, 28), (x + w//2, wheel_y), wheel_r)
        pygame.draw.circle(screen, (25, 25, 28), (x + 4*w//5, wheel_y), wheel_r)

        door = pygame.Rect(body.x + body.w//10, body.y + body.h//3, body.w//8, body.h//2)
        pygame.draw.rect(screen, tuple(max(0, c - 45) for c in self.body_color), door, border_radius=4)

        if self.direction == 1:
            pygame.draw.rect(screen, (255, 235, 170), (x + w - 6, y + h//2, 4, 7), border_radius=2)
        else:
            pygame.draw.rect(screen, (255, 90, 90), (x + 2, y + h//2, 4, 7), border_radius=2)


# =====================
# Log (wood plank)
# =====================
@dataclass
class Log(MovingEntity):
    def draw(self, screen: pygame.Surface, camera_y_px: float) -> None:
        sy = self._screen_y(screen, camera_y_px)
        x = int(self.x_px)
        w = self.w_tiles * TILE
        h = TILE

        base = pygame.Rect(x + 1, sy + h//3, w - 2, h - h//3 - 2)
        pygame.draw.rect(screen, (150, 110, 60), base, border_radius=8)

        pygame.draw.rect(screen, (175, 130, 75),
                         pygame.Rect(base.x, base.y, base.w, 4), border_radius=6)
        pygame.draw.rect(screen, (120, 85, 45),
                         pygame.Rect(base.x, base.bottom - 4, base.w, 4), border_radius=6)

        for i in range(4):
            yy = base.y + 6 + i * (base.h - 12) // 3
            pygame.draw.line(screen, (130, 95, 55), (base.x + 6, yy), (base.right - 6, yy), 2)

        if base.w > TILE:
            kx1 = base.x + base.w // 3
            kx2 = base.x + 2 * base.w // 3
            ky = base.y + base.h // 2
            pygame.draw.circle(screen, (125, 90, 50), (kx1, ky), 6, 2)
            pygame.draw.circle(screen, (125, 90, 50), (kx2, ky), 6, 2)

        pygame.draw.circle(screen, (125, 90, 50), (base.left + 10, base.centery), 10, 2)
        pygame.draw.circle(screen, (125, 90, 50), (base.right - 10, base.centery), 10, 2)


# =====================
# Train
# =====================
@dataclass
class Train(MovingEntity):
    def draw(self, screen: pygame.Surface, camera_y_px: float) -> None:
        sy = self._screen_y(screen, camera_y_px)
        x = int(self.x_px)
        w = self.w_tiles * TILE
        h = TILE

        body = pygame.Rect(x + 1, sy + h//4, w - 2, h - h//4 - 2)
        pygame.draw.rect(screen, (210, 210, 215), body, border_radius=6)

        pygame.draw.rect(screen, (180, 40, 40), (body.x, body.y + 4, body.w, 5), border_radius=3)

        pad = 6
        win_h = body.h // 2
        win_y = body.y + body.h//2 - win_h//2
        n = max(2, min(6, body.w // (TILE//2)))
        win_w = max(10, (body.w - (n+1)*pad) // n)
        for i in range(n):
            wx = body.x + pad + i*(win_w + pad)
            pygame.draw.rect(screen, (190, 220, 255), (wx, win_y, win_w, win_h), border_radius=4)

        wheel_r = max(3, h // 8)
        wheel_y = sy + h - 4
        wheel_count = max(3, body.w // (TILE//2))
        for i in range(wheel_count):
            wx = x + 8 + i * (w - 16) // (wheel_count - 1)
            pygame.draw.circle(screen, (30, 30, 35), (wx, wheel_y), wheel_r)

        if self.direction == 1:
            cab = pygame.Rect(body.right - TILE//2, body.y - 2, TILE//2 - 2, body.h + 4)
            pygame.draw.rect(screen, (200, 200, 205), cab, border_radius=5)
            pygame.draw.circle(screen, (255, 245, 200), (body.right - 4, body.centery), 5)
        else:
            cab = pygame.Rect(body.x + 2, body.y - 2, TILE//2 - 2, body.h + 4)
            pygame.draw.rect(screen, (200, 200, 205), cab, border_radius=5)
            pygame.draw.circle(screen, (255, 245, 200), (body.x + 4, body.centery), 5)
