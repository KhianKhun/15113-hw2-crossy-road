# main.py
from __future__ import annotations
import pygame
import time

from settings import (
    WIDTH, HEIGHT, FPS, TITLE, TILE, COLS,
    COLOR_BG, MOVE_COOLDOWN, CAMERA_MARGIN_TILES,
)
from entities import Player
from world import World
from ui import draw_hud, draw_game_over, init_fonts

def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    init_fonts()

    def new_game():
        world = World()
        player = Player(gx=COLS // 2, gy=2, alive=True, score=0)
        camera_y_px = 0.0
        best = 0
        return world, player, camera_y_px, best

    world, player, camera_y_px, best_score = new_game()
    paused = False
    last_move_time = 0.0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()

        for event in pygame.event.get():
            # Pause toggle
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p and player.alive:
                paused = not paused
                
            if event.type == pygame.QUIT:
                running = False

            # Restart (only when game over)
            if event.type == pygame.KEYDOWN and (not player.alive):
                if event.key == pygame.K_r:
                    world, player, camera_y_px, best_score = new_game()
                    paused = False
                    last_move_time = 0.0

            # Movement (discrete stepping)
            if event.type == pygame.KEYDOWN and player.alive and (not paused):
                if now - last_move_time >= MOVE_COOLDOWN:
                    dx, dy = 0, 0
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        dx = -1
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        dx = 1
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        dy = 1
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        dy = -1

                    if dx != 0 or dy != 0:
                        ngX = player.gx + dx
                        ngY = player.gy + dy
                        if world.can_step_to(ngX, ngY):
                            player.gx, player.gy = ngX, ngY
                            last_move_time = now

                            # scoring: max forward progress (gy)
                            player.score = max(player.score, player.gy)
                            best_score = max(best_score, player.score)

        if player.alive and (not paused):
            # Camera follows upward progress
            target_camera = max(0.0, (player.gy - CAMERA_MARGIN_TILES) * TILE)
            camera_y_px = max(camera_y_px, target_camera)

            # Update world
            world.update(dt, camera_y_px, player.score)

            # Collision + water logic
            world.check_collisions_and_water(player, dt)


        # Draw
        screen.fill(COLOR_BG)
        world.draw(screen, camera_y_px)
        player.draw(screen, camera_y_px)
        draw_hud(screen, player.score, best_score)

        if paused and player.alive:
            from ui import draw_paused
            draw_paused(screen)


        if not player.alive:
            draw_game_over(screen, player.score)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
