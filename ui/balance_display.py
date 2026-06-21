"""Отображение баланса игрока на экране и кнопка магазина обходчиков."""

import pygame
from typing import Optional

from models import Balance
from config import (
    BALANCE_FONT,
    BALANCE_HEIGHT,
    BALANCE_WIDTH,
    BALANCE_IMG,
    BALANCE_COLOR,
)
from utils import format_number, get_image, image_cache


class BalanceDisplay:
    """Отрисовывает баланс, доход и кнопку магазина обходчиков.

    Attributes:
        shop_button_rect: Прямоугольник кнопки магазина (для проверки кликов).
    """

    def __init__(self) -> None:
        self._font: pygame.font.Font = pygame.font.Font(None, BALANCE_FONT)
        self._shop_font: pygame.font.Font = pygame.font.Font(None, 24)
        self._image = get_image(image_cache, BALANCE_IMG)
        self._cached_bg = None
        self._cached_balance_text = None
        self._cached_income_text = None
        self._last_balance = None
        self._last_income = None
        self._last_screen_w = None
        self._last_screen_h = None
        self._shop_button_rect: Optional[pygame.Rect] = None

    @property
    def shop_button_rect(self) -> Optional[pygame.Rect]:
        """Прямоугольник кнопки магазина обходчиков."""
        return self._shop_button_rect

    def draw(self, screen: pygame.Surface, balance: Balance) -> None:
        """Отрисовывает баланс, доход и кнопку магазина.

        Args:
            screen: Поверхность для отрисовки.
            balance: Объект баланса с данными.
        """
        screen_w, screen_h = screen.get_size()

        if (
            self._cached_bg is None
            or self._last_screen_w != screen_w
            or self._last_screen_h != screen_h
        ):
            self._cached_bg = pygame.transform.scale(
                self._image, (BALANCE_WIDTH, BALANCE_HEIGHT)
            )
            self._last_screen_w = screen_w
            self._last_screen_h = screen_h

        bg_rect = self._cached_bg.get_rect(topright=(screen_w * 0.98, 20))

        balance_str = format_number(balance.balance)
        if self._cached_balance_text is None or self._last_balance != balance_str:
            self._cached_balance_text = self._font.render(
                balance_str, True, (255, 255, 255)
            )
            self._last_balance = balance_str

        income_str = f"+{format_number(balance.income)}/s"
        if self._cached_income_text is None or self._last_income != income_str:
            self._cached_income_text = self._font.render(
                income_str, True, (100, 255, 100)
            )
            self._last_income = income_str

        balance_rect = self._cached_balance_text.get_rect()
        balance_rect.center = (bg_rect.centerx * 1.04, bg_rect.centery - 14)

        income_rect = self._cached_income_text.get_rect()
        income_rect.center = (bg_rect.centerx * 1.04, bg_rect.centery + 14)

        screen.blit(self._cached_bg, bg_rect)
        screen.blit(self._cached_balance_text, balance_rect)
        screen.blit(self._cached_income_text, income_rect)

        btn_w, btn_h = 160, 40
        btn_x = bg_rect.left - btn_w - 10
        btn_y = bg_rect.centery - btn_h // 2
        self._shop_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        pygame.draw.rect(screen, (50, 120, 50), self._shop_button_rect, border_radius=8)
        btn_text = self._shop_font.render("Магазин обходч.", True, (255, 255, 255))
        btn_text_rect = btn_text.get_rect(center=self._shop_button_rect.center)
        screen.blit(btn_text, btn_text_rect)
