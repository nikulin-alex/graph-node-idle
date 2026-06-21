"""Точка входа в приложение."""

import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from core import GameLoop


def main() -> None:
    """Инициализирует pygame и запускает игровой цикл."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Graph Idle Simulator")

    game = GameLoop(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
