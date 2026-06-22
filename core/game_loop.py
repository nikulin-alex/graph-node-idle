"""Главный игровой цикл.
Объединяет состояние игры, обработку событий и отрисовку.
"""

import pygame
import logging

from core.game_state import GameState
from core.event_handler import EventHandler
from core.save_load import save_game, load_game
from ui import Renderer, BalanceDisplay
from config import WINDOW_WIDTH, WINDOW_HEIGHT, TOOLBAR_WIDTH
from utils import SoundManager

TIMER_EVENT = pygame.USEREVENT + 1
BG_COLOR = (0, 33, 55)


class GameLoop:
    """Главный игровой цикл с фазами handle_events, update, render.

    Attributes:
        screen: Поверхность для отрисовки.
        game_state: Состояние игры.
        event_handler: Обработчик событий.
        sound_manager: Менеджер звуков и музыки.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen: pygame.Surface = screen
        self._sound_manager: SoundManager = SoundManager()
        self._game_state: GameState = GameState(sound_manager=self._sound_manager)
        self._balance_display: BalanceDisplay = BalanceDisplay()
        self._event_handler: EventHandler = EventHandler(
            self._game_state, self._sound_manager
        )
        self._running: bool = True

        pygame.time.set_timer(TIMER_EVENT, 1000)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.StreamHandler()],
        )

        load_game(self._game_state)
        self._sound_manager.start_music()

    @property
    def game_state(self) -> GameState:
        """Состояние игры."""
        return self._game_state

    @property
    def sound_manager(self) -> SoundManager:
        """Менеджер звуков и музыки."""
        return self._sound_manager

    def run(self) -> None:
        """Запускает главный игровой цикл."""
        while self._running:
            self._handle_events()
            self._render()
            pygame.display.update()

        pygame.quit()

    def _handle_events(self) -> None:
        """Обрабатывает все события pygame."""
        for event in pygame.event.get():
            if self._sound_manager.handle_music_event(event):
                continue

            if event.type == pygame.QUIT:
                save_game(self._game_state)
                self._running = False
            else:
                self._event_handler.handle_event(event)

        cursor_type = self._event_handler.get_cursor_type()
        pygame.mouse.set_cursor(cursor_type)

    def _render(self) -> None:
        """Отрисовывает всё на экране."""
        screen = self._screen
        camera = self._game_state.camera
        nodes = self._game_state.nodes
        traversers = self._game_state.traverser_manager.traversers

        screen.fill(BG_COLOR)

        Renderer.draw_edges(screen, nodes, camera)
        Renderer.draw_traverser_paths(screen, traversers, camera)
        Renderer.draw_all_nodes(screen, nodes, camera)
        Renderer.draw_traverser_nodes(screen, traversers, camera)

        linking_node = self._game_state.left_panel.linking_node
        Renderer.draw_linking_guide(screen, linking_node, camera)

        left_panel = self._game_state.left_panel
        left_panel.update()
        left_panel.draw(
            screen,
            self._game_state.traverser_manager,
            self._game_state.balance,
        )
        left_panel.draw_toggle_button(screen)

        toolbar = self._game_state.toolbar
        toolbar.update(screen)
        toolbar.draw(screen, self._game_state.balance.balance)
        self._balance_display.draw(screen, self._game_state.balance)
