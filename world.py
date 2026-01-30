# world.py
from __future__ import annotations
from dataclasses import dataclass
import random
import pygame
import difficulty


from settings import (
    TILE, WIDTH, HEIGHT, COLS, ROWS,
    LANE_COLORS, COLOR_TREE,
    MAX_GEN_AHEAD,
)
from entities import Player, Car, Log, Train
from utils import clamp

@dataclass
class Lane:
    gy: int
    kind: str  # "grass" | "road" | "water" | "rail"

    # Moving objects
    movers: list = None

    # For grass obstacles
    blocked_x: set[int] = None

    # Spawning
    spawn_timer: float = 0.0
    spawn_interval: float = 1.0
    speed_px: float = 120.0
    direction: int = 1
    mover_min_w: int = 1
    mover_max_w: int = 2

    # rail special behavior
    rail_cooldown: float = 0.0

    def __post_init__(self):
        if self.movers is None:
            self.movers = []
        if self.blocked_x is None:
            self.blocked_x = set()

    def setup(self):
        # Choose parameters based on lane kind
        self.direction = random.choice([-1, 1])

        if self.kind == "grass":
            # Trees block movement; keep at least one path open
            density = random.randint(2, 5)
            xs = list(range(COLS))
            random.shuffle(xs)
            self.blocked_x = set(xs[:density])

        elif self.kind == "road":
            self.spawn_interval = random.uniform(0.7, 1.2)
            self.speed_px = random.uniform(140, 240)
            self.mover_min_w, self.mover_max_w = 1, 2

        elif self.kind == "water":
            self.spawn_interval = random.uniform(0.8, 1.3)
            self.speed_px = random.uniform(90, 170)
            self.mover_min_w, self.mover_max_w = 2, 3

        elif self.kind == "rail":
            # Trains are rarer but wide and dangerous
            self.spawn_interval = random.uniform(3.0, 5.0)
            self.speed_px = random.uniform(220, 320)
            self.mover_min_w, self.mover_max_w = 4, 6
            self.rail_cooldown = random.uniform(0.0, 1.5)

    def spawn_one(self, speed_mult: float):
        w = random.randint(self.mover_min_w, self.mover_max_w)
        w_px = w * TILE

        if self.direction == 1:
            x0 = -w_px - random.uniform(0, TILE * 2)
        else:
            x0 = WIDTH + random.uniform(0, TILE * 2)

        cur_speed = self.speed_px * speed_mult

        if self.kind == "road":
            self.movers.append(Car(x_px=x0, gy=self.gy, w_tiles=w, speed_px=cur_speed,
                                direction=self.direction, base_speed_px=self.speed_px))
        elif self.kind == "water":
            self.movers.append(Log(x_px=x0, gy=self.gy, w_tiles=w, speed_px=cur_speed,
                                direction=self.direction, base_speed_px=self.speed_px))
        elif self.kind == "rail":
            self.movers.append(Train(x_px=x0, gy=self.gy, w_tiles=w, speed_px=cur_speed,
                                    direction=self.direction, base_speed_px=self.speed_px))


    def update(self, dt: float, score: int) -> None:
        if self.kind not in ("road", "water", "rail"):
            return

        speed_mult = difficulty.lane_speed_multiplier(self.kind, score)

        # ✅ 核心：按速度缩放生成间隔，保持密度稳定
        # spawn_rate ∝ speed  =>  interval ∝ 1/speed
        # 额外加上下限避免极端情况
        safe_mult = max(0.20, speed_mult)  # 防止除以很小的数导致间隔爆大
        interval_eff = self.spawn_interval / safe_mult

        # 你可以调这两个阈值：
        interval_eff = max(0.35, min(interval_eff, 4.00))

        self.spawn_timer += dt

        # Rail: 保留冷却逻辑，但用 interval_eff 来刷车
        if self.kind == "rail" and self.rail_cooldown > 0:
            self.rail_cooldown -= dt
        else:
            while self.spawn_timer >= interval_eff:
                self.spawn_timer -= interval_eff
                self.spawn_one(speed_mult)

        # Update movers & cull offscreen
        keep = []
        for m in self.movers:
            base = m.base_speed_px if getattr(m, "base_speed_px", 0.0) > 0 else self.speed_px
            m.speed_px = base * speed_mult
            m.update(dt)

            rect = m.rect_world()
            if rect.right < -TILE * 8 or rect.left > WIDTH + TILE * 8:
                continue
            keep.append(m)
        self.movers = keep



    def draw(self, screen: pygame.Surface, camera_y_px: float):
        lane_color = LANE_COLORS[self.kind]
        y = self.gy * TILE
        screen_y = HEIGHT - (y - camera_y_px) - TILE

        # Base
        pygame.draw.rect(screen, lane_color, (0, screen_y, WIDTH, TILE))

        # Texture / details
        if self.kind == "grass":
            # dots/flowers
            for i in range(0, WIDTH, TILE // 2):
                pygame.draw.circle(screen, (70, 165, 80), (i + (self.gy * 7) % (TILE//2), screen_y + TILE//3), 2)
                pygame.draw.circle(screen, (55, 125, 65), (i + (self.gy * 11) % (TILE//2), screen_y + 2*TILE//3), 2)

            # Trees
            for gx in self.blocked_x:
                tx = gx * TILE
                trunk = pygame.Rect(tx + TILE//2 - 4, screen_y + TILE//2, 8, TILE//2 - 4)
                pygame.draw.rect(screen, (95, 70, 40), trunk, border_radius=3)
                pygame.draw.circle(screen, COLOR_TREE, (tx + TILE//2, screen_y + TILE//2), TILE//3)
                pygame.draw.circle(screen, (25, 75, 30), (tx + TILE//2 - 6, screen_y + TILE//2 + 2), TILE//4)

        elif self.kind == "road":
            # dashed center line
            dash_w = TILE // 2
            for x in range(0, WIDTH, dash_w * 2):
                pygame.draw.rect(screen, (220, 220, 220), (x + dash_w//2, screen_y + TILE//2 - 2, dash_w, 4))

            # subtle curb
            pygame.draw.line(screen, (30, 30, 35), (0, screen_y), (WIDTH, screen_y), 2)

            for m in self.movers:
                m.draw(screen, camera_y_px)

        elif self.kind == "water":
            # waves
            for x in range(0, WIDTH, TILE//2):
                pygame.draw.arc(
                    screen, (200, 230, 255),
                    pygame.Rect(x, screen_y + TILE//3, TILE//2, TILE//2),
                    0, 3.14159, 2
                )
            for m in self.movers:
                m.draw(screen, camera_y_px)

        elif self.kind == "rail":
            # sleepers
            for x in range(0, WIDTH, TILE//2):
                pygame.draw.rect(screen, (110, 85, 60), (x, screen_y + TILE//2 - 3, TILE//3, 6))
            # rails
            pygame.draw.line(screen, (190, 190, 190), (0, screen_y + TILE//3), (WIDTH, screen_y + TILE//3), 3)
            pygame.draw.line(screen, (190, 190, 190), (0, screen_y + 2*TILE//3), (WIDTH, screen_y + 2*TILE//3), 3)

            for m in self.movers:
                m.draw(screen, camera_y_px)


class World:
    def __init__(self):
        self.lanes: dict[int, Lane] = {}
        self.highest_gen_gy = -1
        self.last_safe_gap = 0  # count since last grass lane generated

        # Ensure starting area: a few grass lanes
        for gy in range(0, 6):
            lane = Lane(gy=gy, kind="grass")
            lane.setup()
            # Make first lane more open
            if gy <= 2:
                lane.blocked_x = set()
            self.lanes[gy] = lane
            self.highest_gen_gy = max(self.highest_gen_gy, gy)
            self.last_safe_gap = 0

    def lane_kind_sampler(self) -> str:
        # Force a grass lane if too many dangerous lanes in a row
        if self.last_safe_gap >= 3:
            return "grass"

        # Weighted random
        r = random.random()
        # more roads/grass, occasional water, rare rail
        if r < 0.42:
            return "grass"
        elif r < 0.80:
            return "road"
        elif r < 0.95:
            return "water"
        else:
            return "rail"

    def ensure_generated(self, min_gy: int, max_gy: int) -> None:
        # Generate missing lanes in [min_gy, max_gy]
        while self.highest_gen_gy < max_gy:
            gy = self.highest_gen_gy + 1
            kind = self.lane_kind_sampler()
            lane = Lane(gy=gy, kind=kind)
            lane.setup()

            # A little design constraint: water lane should not be the very first dangerous lane too early
            if gy < 6 and kind == "water":
                lane.kind = "road"
                lane.setup()

            self.lanes[gy] = lane
            self.highest_gen_gy = gy

            if lane.kind == "grass":
                self.last_safe_gap = 0
            else:
                self.last_safe_gap += 1

        # We keep old lanes too (simple); could prune if you want.

    def get_lane(self, gy: int) -> Lane:
        if gy not in self.lanes:
            # generate up to this gy
            self.ensure_generated(0, gy)
        return self.lanes[gy]

    def can_step_to(self, gx: int, gy: int) -> bool:
        if gx < 0 or gx >= COLS:
            return False
        if gy < 0:
            return False
        lane = self.get_lane(gy)
        if lane.kind == "grass" and gx in lane.blocked_x:
            return False
        return True

    def update(self, dt: float, camera_y_px: float, score: int) -> None:
        min_visible_gy = int(camera_y_px // TILE) - 4
        max_visible_gy = int(camera_y_px // TILE) + ROWS + 8

        max_visible_gy = max(max_visible_gy, 0)
        self.ensure_generated(0, max_visible_gy + MAX_GEN_AHEAD)

        for gy in range(max(0, min_visible_gy), max_visible_gy + 1):
            lane = self.get_lane(gy)
            lane.update(dt, score)


    def draw(self, screen: pygame.Surface, camera_y_px: float) -> None:
        min_visible_gy = int(camera_y_px // TILE) - 2
        max_visible_gy = int(camera_y_px // TILE) + ROWS + 2

        for gy in range(max(0, min_visible_gy), max_visible_gy + 1):
            self.get_lane(gy).draw(screen, camera_y_px)


    def check_collisions_and_water(self, player: Player, dt: float) -> None:
        lane = self.get_lane(player.gy)

        # Reset drift when not on water so it doesn't leak across lanes.
        if lane.kind != "water" and hasattr(player, "_drift_px"):
            player._drift_px = 0.0  # type: ignore[attr-defined]

        pr = player.rect_world()

        if lane.kind == "road":
            for m in lane.movers:
                if pr.colliderect(m.rect_world()):
                    player.alive = False
                    return

        elif lane.kind == "rail":
            for m in lane.movers:
                if pr.colliderect(m.rect_world()):
                    player.alive = False
                    return

        elif lane.kind == "water":
            # Continuous-ish contact: use leftover drift (< TILE) to build a more accurate
            # collision rect while logs slide within a tile. This prevents "falling off early".
            if not hasattr(player, "_drift_px"):
                player._drift_px = 0.0  # type: ignore[attr-defined]

            def player_rect_with_drift() -> pygame.Rect:
                x = player.gx * TILE + float(player._drift_px)  # type: ignore[attr-defined]
                return pygame.Rect(int(x), player.gy * TILE, TILE, TILE)

            def is_on_any_log() -> bool:
                pr2 = player_rect_with_drift()
                for mm in lane.movers:
                    if pr2.colliderect(mm.rect_world()):
                        return True
                return False

            # If you step/jump into water without a log under you -> immediate death.
            if not is_on_any_log():
                player.alive = False
                return

            # Find the log we're currently riding.
            on_log = None
            pr2 = player_rect_with_drift()
            for m in lane.movers:
                if pr2.colliderect(m.rect_world()):
                    on_log = m
                    break
            if on_log is None:
                player.alive = False
                return

            # Carry by the log movement this frame.
            player._drift_px += on_log.speed_px * dt * on_log.direction  # type: ignore[attr-defined]

            # --- Screen-edge blocking ---
            # Rule: if log would carry you out of bounds, you stop at the edge (no instant death).
            # You only die once there is no log under you (i.e., log floats away leaving water).
            while player._drift_px >= TILE:  # type: ignore[attr-defined]
                if player.gx >= COLS - 1:
                    player._drift_px = 0.0  # type: ignore[attr-defined]
                    break
                player._drift_px -= TILE  # type: ignore[attr-defined]
                player.gx += 1

            while player._drift_px <= -TILE:  # type: ignore[attr-defined]
                if player.gx <= 0:
                    player._drift_px = 0.0  # type: ignore[attr-defined]
                    break
                player._drift_px += TILE  # type: ignore[attr-defined]
                player.gx -= 1

            # Also block sub-tile drift into the wall.
            if player.gx <= 0 and player._drift_px < 0:  # type: ignore[attr-defined]
                player._drift_px = 0.0  # type: ignore[attr-defined]
            if player.gx >= COLS - 1 and player._drift_px > 0:  # type: ignore[attr-defined]
                player._drift_px = 0.0  # type: ignore[attr-defined]

            # After carry/blocking, if not on any log -> water -> death.
            if not is_on_any_log():
                player.alive = False
                return
