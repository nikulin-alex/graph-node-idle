"""Панель инструментов для управления узлами.

Отображается при выборе узла. Содержит кнопки:
добавить узел, улучшить узел, удалить узел.
"""

import pygame
from typing import List, Optional

from models import GraphNode, Balance, TraverserManager
from ui.button import Button
from config import (
    FONT_PATH,
    TOOLBAR_IMG,
    TOOLBAR_WIDTH,
    FONT_SIZE_TOOLBAR_TEXT,
    DELETE_NODE_PRICE,
)
from utils import (
    get_image,
    image_cache,
    callback1,
    callback2,
    callback3,
    SoundManager,
)


class ToolBar:
    """Панель инструментов, привязанная к выбранному узлу.

    Attributes:
        target_node: Выбранный узел (None если не выбран).
        is_triggered: Открыта ли панель.
    """

    CLOSE_BUTTON_COORDS = (135, 1755, 120, 140)
    INFO_TEXT_COORDS = (280, 1900)  # (x, y) — левый верхний угол текста

    def __init__(self, sound_manager: SoundManager) -> None:
        self._target_node: Optional[GraphNode] = None
        self._image = get_image(image_cache, TOOLBAR_IMG)
        self._image_w: int = self._image.get_width()
        self._image_h: int = self._image.get_height()
        self._font: pygame.font.Font = pygame.font.Font(FONT_PATH, FONT_SIZE_TOOLBAR_TEXT)
        self._sound_manager: SoundManager = sound_manager

        self._target_x: float = 0
        self._current_x: float = 0
        self._smoothing: float = 0.05
        self._buttons: List[Button] = []
        self._is_triggered: bool = False
        self._bg_rect: Optional[pygame.Rect] = None
        self._cached_bg = None
        self._last_screen_h = None

    @property
    def target_node(self) -> Optional[GraphNode]:
        """Выбранный узел."""
        return self._target_node

    @target_node.setter
    def target_node(self, value: Optional[GraphNode]) -> None:
        """Устанавливает выбранный узел."""
        self._target_node = value

    @property
    def is_triggered(self) -> bool:
        """Открыта ли панель."""
        return self._is_triggered

    @is_triggered.setter
    def is_triggered(self, value: bool) -> None:
        """Устанавливает флаг открытия панели."""
        self._is_triggered = value

    @property
    def bg_rect(self) -> Optional[pygame.Rect]:
        """Прямоугольник фона тулбара."""
        return self._bg_rect

    def _get_scaled_bg(self, screen: pygame.Surface) -> pygame.Surface:
        """Возвращает масштабированный фон тулбара (с кэшированием)."""
        screen_h = screen.get_height()
        if self._cached_bg is None or self._last_screen_h != screen_h:
            self._cached_bg = pygame.transform.scale(
                self._image, (TOOLBAR_WIDTH, screen_h)
            )
            self._last_screen_h = screen_h
        return self._cached_bg

    def _update_bg_rect(self, screen: pygame.Surface) -> None:
        """Обновляет прямоугольник фона."""
        scaled_bg = self._get_scaled_bg(screen)
        self._bg_rect = scaled_bg.get_rect(topright=(self._current_x, 0))

    def _create_buttons(self) -> List[Button]:
        """Создаёт кнопки для текущего целевого узла."""
        buttons = []

        btn_delete_coords = (280, 2200, 1050, 250)
        btn_delete = Button(
            "Удалить узел",
            btn_delete_coords,
            callback3,
            lambda: DELETE_NODE_PRICE,
            simple=True,
        )
        buttons.append(btn_delete)

        btn1_coords = (280, 2500, 1050, 450)
        btn1 = Button(
            "Добавить узел",
            btn1_coords,
            callback1,
            lambda: self._target_node.add_node_price(),
            text_func=lambda: (
                f"Добавить узел\n"
                f"Связанных узлов: {len(self._target_node.connected_nodes)}"
            ),
        )
        buttons.append(btn1)

        btn2_coords = (280, 2950, 1050, 450)
        btn2 = Button(
            "Улучшить узел",
            btn2_coords,
            callback2,
            lambda: self._target_node.upgrade_price(),
            text_func=lambda: (
                f"Улучшить узел\n" f"Текущий уровень - {self._target_node.level}"
            ),
        )
        buttons.append(btn2)

        return buttons

    def set_target_node(self, node: GraphNode, screen: pygame.Surface) -> None:
        """Устанавливает целевой узел и открывает панель.

        Args:
            node: Выбранный узел.
            screen: Поверхность для расчёта размеров.
        """
        self._sound_manager.play_close_toolbar()
        if self._target_node is node:
            self._target_node.selected = False
            self._target_node = None
            self._is_triggered = False
            self._target_x = screen.get_width() + TOOLBAR_WIDTH
        else:
            if self._target_node is not None:
                self._target_node.selected = False
            self._target_node = node
            self._is_triggered = True
            node.selected = True
            if self._current_x == 0:
                self._current_x = screen.get_width() + TOOLBAR_WIDTH
            self._update_bg_rect(screen)
            self._buttons = self._create_buttons()
            self._update_target_position(screen)

    def _update_target_position(self, screen: pygame.Surface) -> None:
        """Обновляет целевую позицию панели."""
        if self._target_node is not None:
            self._target_x = screen.get_width()
        else:
            self._target_x = screen.get_width() + TOOLBAR_WIDTH

    def update(self, screen: pygame.Surface) -> None:
        """Обновляет целевую позицию и анимацию выезда панели.

        Args:
            screen: Поверхность для расчёта актуальной ширины окна.
        """
        self._update_target_position(screen)
        if abs(self._current_x - self._target_x) > 1:
            self._current_x += (self._target_x - self._current_x) * self._smoothing

    def draw(self, screen: pygame.Surface, balance: int) -> None:
        """Отрисовывает панель и кнопки.

        Args:
            screen: Поверхность для отрисовки.
            balance: Текущий баланс для определения доступности кнопок.
        """

        self._update_bg_rect(screen)
        scaled_bg = self._get_scaled_bg(screen)
        screen.blit(scaled_bg, self._bg_rect)
        if self._target_node is not None:
            node = self._target_node
            info_lines = [
                f"Узел (уровень {node.level})",
                f"Доход: {node.get_income()}/с",
            ]
            scale_x = self._bg_rect.width / self._image_w
            scale_y = self._bg_rect.height / self._image_h
            text_x = self._bg_rect.left + self.INFO_TEXT_COORDS[0] * scale_x
            text_y = self._bg_rect.top + self.INFO_TEXT_COORDS[1] * scale_y
            for line in info_lines:
                text_surface = self._font.render(line, True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                text_rect.topleft = (text_x, text_y)
                screen.blit(text_surface, text_rect)
                text_y += 35

            for btn in self._buttons:
                btn.draw(screen, self._bg_rect, balance, self._image_w, self._image_h)

    def handle_click(self, mouse_pos: tuple, screen: pygame.Surface) -> bool:
        """Обрабатывает клик по кнопке закрытия.

        Args:
            mouse_pos: Позиция мыши.
            screen: Поверхность для расчёта размеров.

        Returns:
            True если клик был по крестику, False иначе.
        """
        self._update_bg_rect(screen)
        scale_x = self._bg_rect.width / self._image_w
        scale_y = self._bg_rect.height / self._image_h

        close_x = self._bg_rect.left + self.CLOSE_BUTTON_COORDS[0] * scale_x
        close_y = self._bg_rect.top + self.CLOSE_BUTTON_COORDS[1] * scale_y
        close_w = self.CLOSE_BUTTON_COORDS[2] * scale_x
        close_h = self.CLOSE_BUTTON_COORDS[3] * scale_y

        close_rect = pygame.Rect(close_x, close_y, close_w, close_h)

        if close_rect.collidepoint(mouse_pos):
            self._sound_manager.play_close_toolbar()
            self._target_node.selected = False
            self._target_node = None
            self._is_triggered = False
            return True
        return False

    def handle_button_events(
        self,
        event: pygame.event.Event,
        nodes: list,
        balance: Balance,
        traverser_manager: TraverserManager,
        screen: pygame.Surface,
    ) -> bool:
        """Обрабатывает события кнопок тулбара.

        Args:
            event: Событие pygame.
            nodes: Список узлов.
            balance: Баланс.
            traverser_manager: Менеджер обходчиков.
            screen: Поверхность для расчёта размеров.

        Returns:
            True если событие обработано кнопкой.
        """
        if not self._is_triggered or self._target_node is None:
            return False

        for btn in self._buttons:
            result = btn.handle_event(
                event,
                nodes,
                self._target_node,
                self._bg_rect,
                balance,
                self._image_w,
                self._image_h,
                traverser_manager=traverser_manager,
                toolbar=self,
                sound_manager=self._sound_manager,
            )
            if result is not None:
                if isinstance(result, GraphNode) and result not in nodes:
                    nodes.append(result)
                    if self._target_node is not None:
                        self._target_node.connected_nodes.append(result)
                        result.connected_nodes.append(self._target_node)
                self._buttons = self._create_buttons()
                return True
        return False
