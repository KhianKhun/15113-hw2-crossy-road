# ui.py
from __future__ import annotations
import pygame
from settings import COLOR_TEXT, make_font, WIDTH, HEIGHT

FONT_24 = None
FONT_40 = None

def init_fonts():
    global FONT_24, FONT_40
    FONT_24 = make_font(24)
    FONT_40 = make_font(40)

def draw_hud(screen: pygame.Surface, score: int, best: int) -> None:
    if FONT_24 is None:
        init_fonts()

    text = FONT_24.render(f"Score: {score}   Best: {best}", True, COLOR_TEXT)
    screen.blit(text, (12, 10))

def draw_game_over(screen: pygame.Surface, score: int) -> None:
    if FONT_40 is None:
        init_fonts()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    title = FONT_40.render("Game Over", True, COLOR_TEXT)
    hint  = FONT_24.render("Press R to restart", True, COLOR_TEXT)
    sc    = FONT_24.render(f"Score: {score}", True, COLOR_TEXT)

    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 70))
    screen.blit(sc,    (WIDTH//2 - sc.get_width()//2,    HEIGHT//2 - 25))
    screen.blit(hint,  (WIDTH//2 - hint.get_width()//2,  HEIGHT//2 + 15))

def draw_paused(screen: pygame.Surface) -> None:
    if FONT_40 is None:
        init_fonts()

    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    title = FONT_40.render("Paused", True, COLOR_TEXT)
    hint  = FONT_24.render("Press P to resume", True, COLOR_TEXT)

    screen.blit(title, (w//2 - title.get_width()//2, h//2 - 50))
    screen.blit(hint,  (w//2 - hint.get_width()//2,  h//2 + 5))
