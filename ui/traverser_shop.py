"""Магазин обходчиков графа.

Позволяет покупать BFS и DFS обходчиков за игровую валюту.
Открывается по клавише T.
"""

import pygame
from typing import Optional

from config import (
    FONT_PATH,
    FONT_SIZE_SHOP,
    FONT_SIZE_SHOP_TITLE,
    FONT_SIZE_SHOP_PRICE,
)
from models import TraverserManager, Balance
from utils import format_number, SoundManager


class TraverserShop:
    """Модальное окно для покупки обходчиков графа.

    Attributes:
        is_open: Открыто ли окно магазина.
    """

    def __init__(self, soundmanager) -> None:
        self._is_open: bool = False
        self._font: pygame.font.Font = pygame.font.Font(FONT_PATH, FONT_SIZE_SHOP)
        self._title_font: pygame.font.Font = pygame.font.Font(FONT_PATH, FONT_SIZE_SHOP_TITLE)
        self._price_font: pygame.font.Font = pygame.font.Font(FONT_PATH, FONT_SIZE_SHOP_PRICE)
        self._panel_rect: Optional[pygame.Rect] = None
        self._buttons: list[dict] = []
        self._overlay_cache: dict = {}
        self._sound_manager: Optional[SoundManager] = soundmanager

    @property
    def is_open(self) -> bool:
        """Открыто ли окно магазина."""
        return self._is_open

    def toggle(self) -> None:
        """Переключает состояние окна (открыто/закрыто)."""
        self._is_open = not self._is_open

    def _get_overlay(self, screen_size: tuple) -> pygame.Surface:
        """Возвращает затемняющий overlay (с кэшированием).

        Args:
            screen_size: Размер экрана (ширина, высота).

        Returns:
            Полупрозрачная чёрная поверхность.
        """
        key = screen_size
        if key not in self._overlay_cache:
            overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self._overlay_cache[key] = overlay
        return self._overlay_cache[key]

    def _create_buttons(
        self, screen: pygame.Surface, manager: TraverserManager
    ) -> None:
        """Создаёт кнопки магазина на основе текущего размера экрана.

        Args:
            screen: Поверхность для расчёта размеров.
            manager: Менеджер обходчиков для получения цены.
        """
        self._buttons = []
        panel_w = int(screen.get_width() * 0.4)
        panel_h = int(screen.get_height() * 0.5)
        panel_x = (screen.get_width() - panel_w) // 2
        panel_y = (screen.get_height() - panel_h) // 2
        self._panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        price = manager.get_traverser_price()

        # Кнопка BFS
        bfs_btn_rect = pygame.Rect(
            panel_x + 50,
            panel_y + 120,
            panel_w - 100,
            80,
        )
        self._buttons.append(
            {
                "rect": bfs_btn_rect,
                "mode": "bfs",
                "text": "Купить BFS обходчика",
                "price": price,
            }
        )

        # Кнопка DFS
        dfs_btn_rect = pygame.Rect(
            panel_x + 50,
            panel_y + 230,
            panel_w - 100,
            80,
        )
        self._buttons.append(
            {
                "rect": dfs_btn_rect,
                "mode": "dfs",
                "text": "Купить DFS обходчика",
                "price": price,
            }
        )

        # Кнопка закрытия
        close_btn_rect = pygame.Rect(
            panel_x + panel_w - 60,
            panel_y + 10,
            50,
            50,
        )
        self._buttons.append(
            {
                "rect": close_btn_rect,
                "mode": "close",
                "text": "X",
                "price": None,
            }
        )

    def draw(
        self, screen: pygame.Surface, manager: TraverserManager, balance: Balance
    ) -> None:
        """Отрисовывает окно магазина как модальное (на весь экран)."""
        if not self._is_open:
            return

        screen_size = screen.get_size()
        overlay = self._get_overlay(screen_size)
        screen.blit(overlay, (0, 0))

        self._create_buttons(screen, manager)

        pygame.draw.rect(screen, (30, 30, 60), self._panel_rect, border_radius=15)
        pygame.draw.rect(
            screen, (100, 100, 200), self._panel_rect, width=3, border_radius=15
        )

        title_surf = self._title_font.render(
            "Магазин обходчиков", True, (255, 255, 255)
        )
        title_rect = title_surf.get_rect(
            center=(self._panel_rect.centerx, self._panel_rect.top + 50)
        )
        screen.blit(title_surf, title_rect)

        self._draw_shop_buttons(screen, balance)

    def draw_in_panel(
        self,
        screen: pygame.Surface,
        panel_rect: pygame.Rect,
        manager: TraverserManager,
        balance: Balance,
    ) -> None:
        """Отрисовывает содержимое магазина внутри заданного прямоугольника.

        Args:
            screen: Поверхность для отрисовки.
            panel_rect: Прямоугольник области, в которой рисовать магазин.
            manager: Менеджер обходчиков.
            balance: Баланс игрока.
        """
        self._create_buttons_in_rect(panel_rect, manager)
        self._draw_shop_buttons(screen, balance)

    def _draw_shop_buttons(self, screen: pygame.Surface, balance: Balance) -> None:
        """Отрисовывает кнопки магазина (общая логика для draw и draw_in_panel)."""
        for btn in self._buttons:
            if btn["mode"] == "close":
                color = (150, 50, 50)
            elif btn["price"] is not None and balance.balance >= btn["price"]:
                color = (50, 150, 50)
            elif btn["price"] is not None:
                color = (80, 80, 80)
            else:
                color = (60, 60, 100)

            pygame.draw.rect(screen, color, btn["rect"], border_radius=10)

            text_surf = self._font.render(btn["text"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=btn["rect"].center)
            screen.blit(text_surf, text_rect)

            if btn["price"] is not None:
                price_surf = self._price_font.render(
                    f'Цена: {format_number(btn["price"])}', True, (200, 200, 100)
                )
                price_rect = price_surf.get_rect(
                    midtop=(btn["rect"].centerx, btn["rect"].top + 45)
                )
                screen.blit(price_surf, price_rect)

    def _create_buttons_in_rect(
        self, panel_rect: pygame.Rect, manager: TraverserManager
    ) -> None:
        """Создаёт кнопки магазина внутри заданного прямоугольника."""
        self._buttons = []
        self._panel_rect = panel_rect

        price = manager.get_traverser_price()

        btn_margin = 20
        btn_height = 80
        btn_width = panel_rect.width - btn_margin * 2

        bfs_btn_rect = pygame.Rect(
            panel_rect.left + btn_margin,
            panel_rect.top + 20,
            btn_width,
            btn_height,
        )
        self._buttons.append(
            {
                "rect": bfs_btn_rect,
                "mode": "bfs",
                "text": "Купить BFS обходчика",
                "price": price,
            }
        )

        dfs_btn_rect = pygame.Rect(
            panel_rect.left + btn_margin,
            panel_rect.top + 20 + btn_height + 15,
            btn_width,
            btn_height,
        )
        self._buttons.append(
            {
                "rect": dfs_btn_rect,
                "mode": "dfs",
                "text": "Купить DFS обходчика",
                "price": price,
            }
        )

    def handle_click(
        self, mouse_pos: tuple, manager: TraverserManager, balance: Balance
    ) -> bool:
        """Обрабатывает клик по кнопкам магазина (модальный режим)."""
        if not self._is_open:
            return False
        return self._process_button_click(mouse_pos, manager, balance)

    def handle_click_in_panel(
        self,
        mouse_pos: tuple,
        panel_rect: pygame.Rect,
        manager: TraverserManager,
        balance: Balance,
    ) -> bool:
        """Обрабатывает клик по кнопкам магазина внутри панели.

        Args:
            mouse_pos: Позиция мыши.
            panel_rect: Прямоугольник области панели.
            manager: Менеджер обходчиков.
            balance: Баланс игрока.

        Returns:
            True если клик был обработан.
        """
        return self._process_button_click(mouse_pos, manager, balance)

    def _process_button_click(
        self,
        mouse_pos: tuple,
        manager: TraverserManager,
        balance: Balance,
    ) -> bool:
        """Общая логика обработки клика по кнопкам магазина."""
        for btn in self._buttons:
            if btn["rect"].collidepoint(mouse_pos):
                if btn["mode"] == "close":
                    self._is_open = False
                    return True
                elif btn["price"] is not None and balance.balance >= btn["price"]:
                    balance.balance -= btn["price"]
                    manager.add_traverser(btn["mode"])
                    self._sound_manager.play_upgrade()
                    return True
                elif btn["price"] is not None:
                    self._sound_manager.play_click_error()
                    return True
        return False
