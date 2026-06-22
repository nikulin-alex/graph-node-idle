"""Левая выезжающая панель с вертикальным меню вкладок.

В исходном состоянии показывает вертикальный список вкладок.
При нажатии на вкладку переключается на её содержимое.
Кнопка «← Назад» в левом верхнем углу возвращает к списку вкладок.
"""

import pygame
from typing import Optional

from utils import SoundManager
from models import GraphNode, TraverserManager, Balance
from ui import TraverserShop
from config import (
    FONT_PATH,
    LEFT_PANEL_WIDTH,
    LEFT_PANEL_BG_COLOR,
    LEFT_PANEL_BORDER_COLOR,
    LEFT_PANEL_TAB_ACTIVE_COLOR,
    LEFT_PANEL_TOGGLE_BTN_SIZE,
    BALANCE_FONT,
    FONT_SIZE_TAB,
    FONT_SIZE_BUTTON,
    FONT_SIZE_BACK,
)


class LeftPanel:
    """Выезжающая панель слева с вертикальным меню вкладок."""

    TAB_HEIGHT = 50
    TAB_WIDTH = 125
    PADDING = 15
    TOGGLE_MARGIN = 10
    BACK_BTN_SIZE = 40

    LINK_PRICE = 50
    """Цена создания одной связи между узлами."""

    TABS = [
        ("shop", "Магазин", "🛒"),
        ("links", "Связи", "🔗"),
        ("settings", "Настройки", "⚙️"),
    ]

    def __init__(self, soundmanager) -> None:
        self._is_open: bool = False
        self._panel_width: int = LEFT_PANEL_WIDTH
        self._current_x: float = -self._panel_width
        self._target_x: float = -self._panel_width
        self._smoothing: float = 0.05

        self._view: str = "menu"
        self._active_tab: str = "shop"

        self._font: pygame.font.Font = pygame.font.Font(FONT_PATH, BALANCE_FONT)
        self._tab_font: pygame.font.Font = pygame.font.Font(FONT_PATH, FONT_SIZE_TAB)
        self._btn_font: pygame.font.Font = pygame.font.Font(FONT_PATH, FONT_SIZE_BUTTON)
        self._back_font: pygame.font.Font = pygame.font.Font(FONT_PATH, FONT_SIZE_BACK)

        self._traverser_shop: TraverserShop = TraverserShop(soundmanager)

        self._toggle_btn_rect: Optional[pygame.Rect] = None
        self._panel_rect: Optional[pygame.Rect] = None
        self._sound_manager: SoundManager = soundmanager

        self._linking_node: Optional[GraphNode] = None

        self._tab_rects: list[tuple[pygame.Rect, str]] = []
        self._back_btn_rect: Optional[pygame.Rect] = None

    @property
    def is_open(self) -> bool:
        """Открыта ли панель."""
        return self._is_open

    @property
    def toggle_btn_rect(self) -> Optional[pygame.Rect]:
        """Прямоугольник кнопки-стрелочки."""
        return self._toggle_btn_rect

    @property
    def traverser_shop(self) -> TraverserShop:
        """Магазин обходчиков (для доступа из EventHandler)."""
        return self._traverser_shop

    @property
    def linking_node(self) -> Optional[GraphNode]:
        """Первый узел, выбранный для связи (None если не в режиме связывания)."""
        return self._linking_node

    @linking_node.setter
    def linking_node(self, value: Optional[GraphNode]) -> None:
        self._linking_node = value

    def toggle(self) -> None:
        """Переключает открытие/закрытие панели."""
        self._sound_manager.play_close_toolbar()
        self._is_open = not self._is_open
        if not self._is_open:
            self._view = "menu"

    def _go_back(self) -> None:
        """Возвращает к главному меню вкладок."""
        self._sound_manager.play_close_toolbar()
        self._view = "menu"

    def update(self) -> None:
        """Обновляет целевую позицию и анимацию выезда панели."""
        if self._is_open:
            self._target_x = 0
        else:
            self._target_x = -self._panel_width - self.TOGGLE_MARGIN

        if abs(self._current_x - self._target_x) > 1:
            self._current_x += (self._target_x - self._current_x) * self._smoothing

    def draw(
        self,
        screen: pygame.Surface,
        traverser_manager: TraverserManager,
        balance: Balance,
    ) -> None:
        """Отрисовывает панель, меню вкладок или контент активной вкладки."""
        screen_h = screen.get_height()
        panel_rect = pygame.Rect(int(self._current_x), 0, self._panel_width, screen_h)
        self._panel_rect = panel_rect

        pygame.draw.rect(screen, LEFT_PANEL_BG_COLOR, panel_rect, border_radius=0)
        pygame.draw.rect(
            screen, LEFT_PANEL_BORDER_COLOR, panel_rect, width=2, border_radius=0
        )

        if self._view == "menu":
            self._draw_menu(screen, panel_rect)
        else:
            self._draw_tab_content(screen, panel_rect, traverser_manager, balance)
            self._draw_back_button(screen, panel_rect)

    def _draw_menu(self, screen: pygame.Surface, panel_rect: pygame.Rect) -> None:
        """Рисует вертикальный список вкладок (главное меню)."""
        self._tab_rects = []
        tab_height = 70
        tab_margin = 10
        start_y = panel_rect.top + 30

        for tab_key, tab_label, tab_icon in self.TABS:
            tab_rect = pygame.Rect(
                panel_rect.left + tab_margin,
                start_y,
                panel_rect.width - tab_margin * 2,
                tab_height,
            )

            color = LEFT_PANEL_TAB_ACTIVE_COLOR
            pygame.draw.rect(screen, color, tab_rect, border_radius=10)


            label_surf = self._tab_font.render(tab_label, True, (255, 255, 255))
            label_rect = label_surf.get_rect(
                center=(tab_rect.centerx, tab_rect.centery)
            )
            screen.blit(label_surf, label_rect)

            arrow_surf = self._tab_font.render("->", True, (180, 180, 220))
            arrow_rect = arrow_surf.get_rect(midright=(tab_rect.right - 15, tab_rect.centery))
            screen.blit(arrow_surf, arrow_rect)

            self._tab_rects.append((tab_rect, tab_key))
            start_y += tab_height + tab_margin

    def _draw_back_button(
        self, screen: pygame.Surface, panel_rect: pygame.Rect
    ) -> None:
        """Рисует кнопку «← Назад» в левом верхнем углу панели."""
        back_rect = pygame.Rect(
            panel_rect.left + 10,
            panel_rect.top + 10,
            50,
            self.BACK_BTN_SIZE,
        )
        self._back_btn_rect = back_rect

        pygame.draw.rect(screen, (50, 50, 90), back_rect, border_radius=8)

        back_surf = self._back_font.render("<<", True, (200, 200, 255))
        back_text_rect = back_surf.get_rect(midleft=(back_rect.left + 10, back_rect.centery))
        screen.blit(back_surf, back_text_rect)

    def _draw_tab_content(
        self,
        screen: pygame.Surface,
        panel_rect: pygame.Rect,
        traverser_manager: TraverserManager,
        balance: Balance,
    ) -> None:
        """Рисует содержимое активной вкладки."""
        content_rect = pygame.Rect(
            panel_rect.left + self.PADDING,
            panel_rect.top + self.BACK_BTN_SIZE + self.PADDING + 10,
            panel_rect.width - self.PADDING * 2,
            panel_rect.height - self.BACK_BTN_SIZE - self.PADDING * 2 - 10,
        )

        if self._active_tab == "shop":
            self._traverser_shop.draw_in_panel(
                screen, content_rect, traverser_manager, balance
            )
        elif self._active_tab == "links":
            self._draw_links_tab(screen, content_rect, balance)
        elif self._active_tab == "settings":
            self._draw_settings_tab(screen, content_rect)

    def _draw_links_tab(
        self, screen: pygame.Surface, content_rect: pygame.Rect, balance: Balance
    ) -> None:
        """Рисует содержимое вкладки 'Связи'."""
        if self._linking_node is not None:
            status_lines = [
                "Выбран узел 1.",
                "Кликните на второй",
                "узел на графе.",
            ]
            status_color = (100, 255, 100)
        else:
            status_lines = [
                "Нажмите 'Соединить узлы',",
                "затем кликните на два",
                "узла на графе.",
            ]
            status_color = (200, 200, 200)

        y_offset = content_rect.top + 10
        for line in status_lines:
            text_surf = self._btn_font.render(line, True, status_color)
            text_rect = text_surf.get_rect(
                midtop=(content_rect.centerx, y_offset)
            )
            screen.blit(text_surf, text_rect)
            y_offset += 30

        btn_rect = pygame.Rect(
            content_rect.left + 20,
            y_offset + 20,
            content_rect.width - 40,
            60,
        )

        can_afford = balance.balance >= self.LINK_PRICE
        is_active = self._linking_node is None and can_afford

        if is_active:
            btn_color = (60, 120, 60)
        else:
            btn_color = (60, 60, 60)

        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)

        if self._linking_node is not None:
            btn_label = "Режим активен..."
        else:
            btn_label = f"Соединить узлы [{self.LINK_PRICE}]"

        text_surf = self._btn_font.render(btn_label, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=btn_rect.center)
        screen.blit(text_surf, text_rect)

        if self._linking_node is not None:
            cancel_rect = pygame.Rect(
                content_rect.left + 20,
                btn_rect.bottom + 10,
                content_rect.width - 40,
                50,
            )
            pygame.draw.rect(screen, (120, 60, 60), cancel_rect, border_radius=8)
            cancel_text = self._btn_font.render(
                "Отмена (Esc)", True, (255, 255, 255)
            )
            cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
            screen.blit(cancel_text, cancel_text_rect)

        price_lines = [
            f"Цена: {self.LINK_PRICE} за связь.",
            f"Макс. связей у узла: {GraphNode.ADD_NODE_CAPACITY * 2}.",
        ]
        py = btn_rect.bottom + 60
        for pline in price_lines:
            price_surf = self._btn_font.render(pline, True, (150, 150, 150))
            price_rect = price_surf.get_rect(
                midtop=(content_rect.centerx, py)
            )
            screen.blit(price_surf, price_rect)
            py += 25

    def _draw_settings_tab(
        self, screen: pygame.Surface, content_rect: pygame.Rect
    ) -> None:
        """Рисует содержимое вкладки 'Настройки' (заглушка)."""
        text_surf = self._font.render("Настройки (скоро)", True, (150, 150, 150))
        text_rect = text_surf.get_rect(center=content_rect.center)
        screen.blit(text_surf, text_rect)

    def draw_toggle_button(self, screen: pygame.Surface) -> None:
        """Рисует кнопку-стрелочку в левом верхнем углу экрана."""
        button_height = LEFT_PANEL_TOGGLE_BTN_SIZE
        button_width = button_height * 2
        x = self._current_x + LEFT_PANEL_WIDTH + self.TOGGLE_MARGIN * 2
        y = self.TOGGLE_MARGIN
        self._toggle_btn_rect = pygame.Rect(x, y, button_width, button_height)

        pygame.draw.rect(screen, (50, 50, 80), self._toggle_btn_rect, border_radius=8)

        text = "Инструменты" if not self._is_open else "Закрыть"
        text_surf = self._btn_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self._toggle_btn_rect.center)
        screen.blit(text_surf, text_rect)

    # ─────────────────────── ОБРАБОТКА КЛИКОВ ───────────────────────

    def handle_click(
        self, mouse_pos: tuple, traverser_manager: TraverserManager, balance: Balance
    ) -> bool:
        """Обрабатывает клик внутри панели (меню, назад, контент вкладки)."""
        if self._panel_rect is None:
            return False

        if self._view == "menu":
            return self._handle_menu_click(mouse_pos)
        else:
            return self._handle_tab_view_click(
                mouse_pos, traverser_manager, balance
            )

    def _handle_menu_click(self, mouse_pos: tuple) -> bool:
        """Обрабатывает клик по вертикальному меню вкладок."""
        for tab_rect, tab_key in self._tab_rects:
            if tab_rect.collidepoint(mouse_pos):
                self._sound_manager.play_close_toolbar()
                self._active_tab = tab_key
                self._view = tab_key
                return True
        return False

    def _handle_tab_view_click(
        self,
        mouse_pos: tuple,
        traverser_manager: TraverserManager,
        balance: Balance,
    ) -> bool:
        """Обрабатывает клик внутри просмотра вкладки (кнопка назад или контент)."""
        # Кнопка "Назад"
        if self._back_btn_rect is not None and self._back_btn_rect.collidepoint(mouse_pos):
            self._go_back()
            return True

        # Контент вкладки
        if self._panel_rect is None:
            return False

        content_rect = pygame.Rect(
            self._panel_rect.left + self.PADDING,
            self._panel_rect.top + self.BACK_BTN_SIZE + self.PADDING + 10,
            self._panel_rect.width - self.PADDING * 2,
            self._panel_rect.height - self.BACK_BTN_SIZE - self.PADDING * 2 - 10,
        )

        if self._active_tab == "shop":
            return self._traverser_shop.handle_click_in_panel(
                mouse_pos, content_rect, traverser_manager, balance
            )

        if self._active_tab == "links":
            return self._handle_links_tab_click(mouse_pos, balance)

        return False

    def _handle_links_tab_click(
        self, mouse_pos: tuple, balance: Balance
    ) -> bool:
        """Обрабатывает клик на вкладке 'Связи'."""
        if self._panel_rect is None:
            return False

        content_rect = pygame.Rect(
            self._panel_rect.left + self.PADDING,
            self._panel_rect.top + self.BACK_BTN_SIZE + self.PADDING + 10,
            self._panel_rect.width - self.PADDING * 2,
            self._panel_rect.height - self.BACK_BTN_SIZE - self.PADDING * 2 - 10,
        )

        y_offset = content_rect.top + 10
        for _ in range(3):
            y_offset += 30

        btn_rect = pygame.Rect(
            content_rect.left + 20,
            y_offset + 20,
            content_rect.width - 40,
            60,
        )

        if btn_rect.collidepoint(mouse_pos):
            if self._linking_node is None and balance.balance >= self.LINK_PRICE:
                self._sound_manager.play_upgrade()
                balance.balance -= self.LINK_PRICE
                self._linking_node = "pending"
                return True
            return True

        if self._linking_node is not None:
            cancel_rect = pygame.Rect(
                content_rect.left + 20,
                btn_rect.bottom + 10,
                content_rect.width - 40,
                50,
            )
            if cancel_rect.collidepoint(mouse_pos):
                self._sound_manager.play_close_toolbar()
                self._linking_node = None
                return True

        return False