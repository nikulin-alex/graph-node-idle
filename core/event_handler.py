"""Обработчик событий pygame."""

import pygame
import logging
from typing import Optional

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
    SoundManager,
)


class EventHandler:
    """Обрабатывает события pygame и обновляет состояние игры.

    Attributes:
        game_state: Состояние игры.
        sound_manager: Менеджер звуков.
    """

    def __init__(self, game_state: GameState, sound_manager: SoundManager) -> None:
        self._game_state: GameState = game_state
        self._sound_manager: SoundManager = sound_manager
        self._node_dragging: bool = False
        self._dragged_node: GraphNode = None
        self._drag_offset_x: float = 0
        self._drag_offset_y: float = 0
        self._drag_start_pos: tuple = None
        self._is_dragging: bool = False
        self._mouse_pos: tuple = None

        # Состояние для множественного выделения и группового перетаскивания
        self._selected_nodes: set = set()
        self._group_dragging: bool = False
        self._group_drag_offsets: list = []  # [(node, offset_x, offset_y), ...]

    @property
    def game_state(self) -> GameState:
        """Состояние игры."""
        return self._game_state

    @property
    def selected_nodes(self) -> set:
        """Множество выделенных узлов (для групповых операций)."""
        return self._selected_nodes

    def _clear_selection(self) -> None:
        """Снимает выделение со всех узлов."""
        for node in self._selected_nodes:
            node.selected = False
        self._selected_nodes.clear()

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

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                left_panel = self._game_state.left_panel
                if left_panel.linking_node is not None:
                    left_panel.linking_node = None
                    self._sound_manager.play_close_toolbar()
                else:
                    # Escape снимает выделение со всех узлов
                    self._clear_selection()
                    toolbar = self._game_state.toolbar
                    if toolbar.target_node is not None:
                        toolbar.target_node.selected = False
                        toolbar.target_node = None
                        toolbar.is_triggered = False

        elif event.type == pygame.VIDEORESIZE:
            clear_scaled_cache(scaled_cache)
            clear_text_cache(text_cache)
            screen = pygame.display.get_surface()
            self._game_state.toolbar.update(screen)

    def _handle_mouse_down(self, event: pygame.event.Event) -> None:
        """Обрабатывает нажатие кнопки мыши."""
        mouse_pos = pygame.mouse.get_pos()
        self._mouse_pos = mouse_pos

        left_panel = self._game_state.left_panel

        if left_panel.toggle_btn_rect.collidepoint(mouse_pos):
            left_panel.toggle()
            return

        if left_panel.is_open:
            if left_panel.handle_click(
                mouse_pos,
                self._game_state.traverser_manager,
                self._game_state.balance,
            ):
                return

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

        linking_node = left_panel.linking_node
        if linking_node is not None and clicked_node is not None:
            if linking_node == "pending":
                left_panel.linking_node = clicked_node
                self._sound_manager.play_upgrade()
                return
            else:
                if clicked_node is not linking_node:
                    if clicked_node not in linking_node.connected_nodes:
                        if (len(linking_node.connected_nodes) < linking_node.max_connections
                                and len(clicked_node.connected_nodes) < clicked_node.max_connections):
                            linking_node.connected_nodes.append(clicked_node)
                            clicked_node.connected_nodes.append(linking_node)
                            self._sound_manager.play_upgrade()
                left_panel.linking_node = None
                return

        if clicked_node is not None:
            keys = pygame.key.get_mods()
            ctrl_held = keys & (pygame.KMOD_CTRL | pygame.KMOD_META)

            if ctrl_held:
                clicked_node.toggle_selected()
                if clicked_node.selected:
                    self._selected_nodes.add(clicked_node)
                else:
                    self._selected_nodes.discard(clicked_node)

                if self._selected_nodes:
                    if toolbar.target_node is not None:
                        toolbar.target_node.selected = False
                        toolbar.target_node = None
                        toolbar.is_triggered = False

                if clicked_node.selected:
                    self._group_dragging = True
                    self._group_drag_offsets = []
                    for node in self._selected_nodes:
                        off_x = node.x - click_pos[0]
                        off_y = node.y - click_pos[1]
                        self._group_drag_offsets.append((node, off_x, off_y))
                return

            if clicked_node in self._selected_nodes and len(self._selected_nodes) > 1:
                # ГРУППОВОЕ ПЕРЕТАСКИВАНИЕ
                self._group_dragging = True
                self._group_drag_offsets = []
                for node in self._selected_nodes:
                    off_x = node.x - click_pos[0]
                    off_y = node.y - click_pos[1]
                    self._group_drag_offsets.append((node, off_x, off_y))
                return

            if clicked_node not in self._selected_nodes:
                self._clear_selection()

            self._node_dragging = True
            self._dragged_node = clicked_node
            self._drag_offset_x = clicked_node.x - click_pos[0]
            self._drag_offset_y = clicked_node.y - click_pos[1]
            self._drag_start_pos = mouse_pos
        else:
            self._clear_selection()
            if toolbar.target_node is not None:
                toolbar.target_node.selected = False
                toolbar.target_node = None
                toolbar.is_triggered = False
            self._is_dragging = True

    def _handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Обрабатывает движение мыши."""
        if self._group_dragging and self._selected_nodes:
            current_pos = pygame.mouse.get_pos()
            world_pos = self._game_state.camera.unapply(current_pos)
            for node, off_x, off_y in self._group_drag_offsets:
                node.x = world_pos[0] + off_x
                node.y = world_pos[1] + off_y
        elif self._node_dragging and self._dragged_node is not None:
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
        if self._group_dragging:
            self._group_dragging = False
            self._group_drag_offsets = []
            return

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
        if self._node_dragging or self._group_dragging:
            return pygame.SYSTEM_CURSOR_HAND
        elif self._is_dragging:
            return pygame.SYSTEM_CURSOR_SIZEALL
        else:
            return pygame.SYSTEM_CURSOR_ARROW