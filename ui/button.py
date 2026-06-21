"""Кнопка для панели инструментов."""

import pygame
from typing import Callable, Optional

from models import GraphNode
from config import (
    UPGRADE_BTN_IMG,
    UPGRADE_BTN_DISABLED_IMG,
    MAX_UPGRADED_BTN_IMG,
)
from utils import format_number, get_image, image_cache


class Button:
    """Кнопка на панели инструментов.

    Attributes:
        text: Текст кнопки.
        state: Состояние ('normal', 'disabled', 'max').
    """

    SPRITE_SIZE = (64, 96)

    def __init__(
        self,
        text: str,
        coords_list: tuple,
        callback: Callable,
        price_func: Callable,
        text_func: Optional[Callable] = None,
        simple: bool = False,
    ) -> None:
        self._text: str = text
        self._text_func: Optional[Callable] = text_func
        self._font: pygame.font.Font = pygame.font.Font(None, 20 if simple else 24)
        self._rect: Optional[pygame.Rect] = None
        self._sprite_rect: Optional[pygame.Rect] = None
        self._coords_list: tuple = coords_list
        self._callback: Callable = callback
        self._price_func: Callable = price_func
        self._simple: bool = simple
        self._state: str = "normal"

        self._images = {
            "normal": get_image(image_cache, UPGRADE_BTN_IMG),
            "disabled": get_image(image_cache, UPGRADE_BTN_DISABLED_IMG),
            "max": get_image(image_cache, MAX_UPGRADED_BTN_IMG),
        }
        self._cached_sprites: dict = {}

    @property
    def state(self) -> str:
        """Состояние кнопки: 'normal', 'disabled', 'max'."""
        return self._state

    def get_sprite(self, state: str, size: tuple) -> pygame.Surface:
        """Возвращает масштабированный спрайт для кнопки (с кэшированием).

        Args:
            state: Состояние ('normal', 'disabled', 'max').
            size: Размер (ширина, высота).

        Returns:
            Масштабированная поверхность спрайта.
        """
        key = (state, size)
        if key not in self._cached_sprites:
            self._cached_sprites[key] = pygame.transform.scale(
                self._images[state], size
            )
        return self._cached_sprites[key]

    def update_rect(
        self, bg_rect: pygame.Rect, toolbar_image_w: int, toolbar_image_h: int
    ) -> None:
        """Обновляет позицию кнопки относительно фона тулбара.

        Args:
            bg_rect: Прямоугольник фона тулбара.
            toolbar_image_w: Ширина исходного изображения тулбара.
            toolbar_image_h: Высота исходного изображения тулбара.
        """
        scale_x = bg_rect.width / toolbar_image_w
        scale_y = bg_rect.height / toolbar_image_h

        x = bg_rect.left + self._coords_list[0] * scale_x
        y = bg_rect.top + self._coords_list[1] * scale_y
        w = self._coords_list[2] * scale_x
        h = self._coords_list[3] * scale_y

        self._rect = pygame.Rect(x, y, w, h)

        if not self._simple:
            sprite_w = int(
                self.SPRITE_SIZE[0] * (self._rect.width / self._coords_list[2]) * 3.5
            )
            sprite_h = int(
                self.SPRITE_SIZE[1] * (self._rect.height / self._coords_list[3]) * 3.5
            )
            self._sprite_rect = pygame.Rect(
                self._rect.right - sprite_w - 20,
                self._rect.centery - sprite_h // 2,
                sprite_w,
                sprite_h,
            )

    def handle_event(
        self,
        event: pygame.event.Event,
        nodes: list,
        node: GraphNode,
        bg_rect: pygame.Rect,
        balance: object,
        toolbar_image_w: int,
        toolbar_image_h: int,
        **kwargs,
    ) -> Optional[object]:
        """Обрабатывает событие клика по кнопке.

        Args:
            event: Событие pygame.
            nodes: Список узлов.
            node: Целевой узел.
            bg_rect: Прямоугольник фона тулбара.
            balance: Объект баланса.
            toolbar_image_w: Ширина изображения тулбара.
            toolbar_image_h: Высота изображения тулбара.
            **kwargs: Дополнительные аргументы для коллбэка.

        Returns:
            Результат коллбэка или None.
        """
        if self._state in ("disabled", "max"):
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.update_rect(bg_rect, toolbar_image_w, toolbar_image_h)
            target_rect = self._rect if self._simple else self._sprite_rect
            if target_rect and target_rect.collidepoint(event.pos):
                price = self._price_func()
                result = self._callback(
                    nodes=nodes,
                    node=node,
                    node_class=GraphNode,
                    balance=balance,
                    price=price,
                    **kwargs,
                )
                return result
        return None

    def draw(
        self,
        screen: pygame.Surface,
        bg_rect: pygame.Rect,
        balance: int,
        toolbar_image_w: int,
        toolbar_image_h: int,
    ) -> None:
        """Отрисовывает кнопку.

        Args:
            screen: Поверхность для отрисовки.
            bg_rect: Прямоугольник фона тулбара.
            balance: Текущий баланс для определения доступности.
            toolbar_image_w: Ширина изображения тулбара.
            toolbar_image_h: Высота изображения тулбара.
        """
        self.update_rect(bg_rect, toolbar_image_w, toolbar_image_h)

        if self._rect is None:
            return

        price = self._price_func()
        if price is None:
            self._state = "max"
        else:
            self._state = "disabled" if balance < price else "normal"

        if self._simple:
            color = (180, 50, 50) if self._state == "normal" else (80, 40, 40)
            pygame.draw.rect(screen, color, self._rect, border_radius=6)
            label = (
                f"{self._text}  [{format_number(price)}]"
                if price is not None
                else self._text
            )
            text_surf = self._font.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self._rect.center)
            screen.blit(text_surf, text_rect)
        else:
            display_text = self._text_func() if self._text_func else self._text
            if display_text:
                text_surf = self._font.render(display_text, True, (255, 255, 255))
                text_rect = text_surf.get_rect()
                text_rect.midleft = (self._rect.left + 10, self._rect.centery - 10)
                screen.blit(text_surf, text_rect)

                if self._state != "max" and price is not None:
                    price_surf = self._font.render(
                        format_number(price), True, (255, 255, 255)
                    )
                    price_rect = price_surf.get_rect()
                    price_rect.midleft = (self._rect.left + 10, self._rect.centery + 20)
                    screen.blit(price_surf, price_rect)

            img_key = "max" if self._state == "max" else self._state
            sprite = self.get_sprite(img_key, self._sprite_rect.size)
            screen.blit(sprite, self._sprite_rect)
