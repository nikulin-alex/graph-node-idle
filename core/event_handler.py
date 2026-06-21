"""Обработчик событий pygame."""

import pygame
import logging

from models import GraphNode
from core.game_state import GameState
from config import NODE_SIZE, NODE_SPAWN_RADIUS, DELETE_NODE_PRICE
from utils import (
    collision,
    get_new_coords,
    clear_scaled_cache,
    clear_text_cache,
    scaled_cache,
    text_cache,
)


class EventHandler:
    """Обрабатывает события pygame и обновляет состояние игры.

    Attributes:
        game_state: Состояние игры.
    """

    def __init__(self, game_state: GameState, balance_display=None) -> None:
        self._game_state: GameState = game_state
        self._balance_display = balance_display
        self._node_dragging: bool = False
        self._dragged_node: GraphNode = None
        self._drag_offset_x: float = 0
        self._drag_offset_y: float = 0
        self._drag_start_pos: tuple = None
        self._is_dragging: bool = False
        self._mouse_pos: tuple = None

    @property
    def game_state(self) -> GameState:
        """Состояние игры."""
        return self._game_state

    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает одно событие pygame.

        Args:
            event: Событие pygame.
        """
        if event.type == pygame.USEREVENT + 1:
            self._game_state.update()

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self._game_state.camera.zoom_in()
            elif event.y < 0:
                self._game_state.camera.zoom_out()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_down(event)

        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._handle_mouse_up(event)

        elif event.type == pygame.VIDEORESIZE:
            clear_scaled_cache(scaled_cache)
            clear_text_cache(text_cache)
            screen = pygame.display.get_surface()
            self._game_state.toolbar.update(screen)

    def _handle_mouse_down(self, event: pygame.event.Event) -> None:
        """Обрабатывает нажатие кнопки мыши."""
        mouse_pos = pygame.mouse.get_pos()
        self._mouse_pos = mouse_pos

        shop = self._game_state.traverser_shop
        if shop.is_open:
            shop.handle_click(
                mouse_pos,
                self._game_state.traverser_manager,
                self._game_state.balance,
            )
            return None

        if (
            self._balance_display is not None
            and self._balance_display.shop_button_rect is not None
            and self._balance_display.shop_button_rect.collidepoint(mouse_pos)
        ):
            shop.toggle()
            return None

        toolbar = self._game_state.toolbar
        if toolbar.is_triggered:
            if toolbar.handle_button_events(
                event,
                self._game_state.nodes,
                self._game_state.balance,
                self._game_state.traverser_manager,
                pygame.display.get_surface(),
            ):
                return None

            if toolbar.handle_click(mouse_pos, pygame.display.get_surface()):
                return None

        click_pos = self._game_state.camera.unapply(mouse_pos)

        clicked_node = None
        for node in self._game_state.nodes:
            if collision(click_pos, node, NODE_SIZE):
                clicked_node = node
                break

        if clicked_node is not None:
            self._node_dragging = True
            self._dragged_node = clicked_node
            self._drag_offset_x = clicked_node.x - click_pos[0]
            self._drag_offset_y = clicked_node.y - click_pos[1]
            self._drag_start_pos = mouse_pos
        else:
            self._is_dragging = True

    def _handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Обрабатывает движение мыши."""
        if self._node_dragging and self._dragged_node is not None:
            current_pos = pygame.mouse.get_pos()
            world_pos = self._game_state.camera.unapply(current_pos)
            self._dragged_node.x = world_pos[0] + self._drag_offset_x
            self._dragged_node.y = world_pos[1] + self._drag_offset_y
        elif self._is_dragging and self._mouse_pos is not None:
            current_pos = pygame.mouse.get_pos()
            dx = self._mouse_pos[0] - current_pos[0]
            dy = self._mouse_pos[1] - current_pos[1]
            self._game_state.camera.move(dx, dy)
            self._mouse_pos = current_pos

    def _handle_mouse_up(self, event: pygame.event.Event) -> None:
        """Обрабатывает отпускание кнопки мыши."""
        if self._node_dragging and self._dragged_node is not None:
            if self._drag_start_pos is not None:
                dx = abs(pygame.mouse.get_pos()[0] - self._drag_start_pos[0])
                dy = abs(pygame.mouse.get_pos()[1] - self._drag_start_pos[1])
                if dx < 5 and dy < 5:
                    toolbar = self._game_state.toolbar
                    toolbar.set_target_node(
                        self._dragged_node, pygame.display.get_surface()
                    )
                    pass

            self._node_dragging = False
            self._dragged_node = None
            self._drag_start_pos = None
        else:
            self._is_dragging = False
            self._mouse_pos = None

    def get_cursor_type(self) -> int:
        """Возвращает тип курсора в зависимости от текущего состояния.

        Returns:
            Константа pygame.SYSTEM_CURSOR_*.
        """
        if self._node_dragging:
            return pygame.SYSTEM_CURSOR_HAND
        elif self._is_dragging:
            return pygame.SYSTEM_CURSOR_SIZEALL
        else:
            return pygame.SYSTEM_CURSOR_ARROW
