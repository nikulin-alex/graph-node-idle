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
    SLIDER_TRACK_COLOR,
    SLIDER_FILL_COLOR,
    SLIDER_HANDLE_COLOR,
    SLIDER_HANDLE_RADIUS,
    SLIDER_TRACK_HEIGHT,
    SLIDER_LABEL_COLOR,
    SLIDER_VALUE_COLOR,
    PADDING,
    MANUAL_BG_COLOR,
    MANUAL_TITLE_COLOR,
    MANUAL_TEXT_COLOR,
    MANUAL_HIGHLIGHT_COLOR,
    MANUAL_SECTION_COLOR,
    MANUAL_NAV_BTN_COLOR,
    MANUAL_NAV_BTN_HOVER_COLOR,
    MANUAL_NAV_BTN_TEXT_COLOR,
    MANUAL_PAGE_INDICATOR_COLOR,
    MANUAL_SCROLLBAR_COLOR,
    MANUAL_SCROLLBAR_HANDLE_COLOR,
    MANUAL_FONT_SIZE_TITLE,
    MANUAL_FONT_SIZE_TEXT,
    MANUAL_FONT_SIZE_SECTION,
    MANUAL_FONT_SIZE_NAV,
    MANUAL_LINE_SPACING,
    MANUAL_SECTION_SPACING,
    MANUAL_CONTENT_PADDING,
)


class Slider:
    """Ползунок для регулировки значения (громкость и т.п.)."""

    def __init__(
        self,
        label: str,
        get_value,
        set_value,
        x: int,
        y: int,
        width: int,
    ) -> None:
        self.label: str = label
        self.get_value = get_value
        self.set_value = set_value
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.dragging: bool = False

    @property
    def track_rect(self) -> pygame.Rect:
        """Прямоугольник трека ползунка."""
        return pygame.Rect(self.x, self.y, self.width-20, SLIDER_TRACK_HEIGHT)

    @property
    def handle_x(self) -> int:
        """X-позиция ручки ползунка на основе текущего значения."""
        value = self.get_value()
        return int(self.x + value * (self.width - SLIDER_HANDLE_RADIUS * 2)) + SLIDER_HANDLE_RADIUS

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовывает ползунок: трек, заливку, ручку, подпись."""
        value = self.get_value()
        track = self.track_rect
        handle_cx = self.handle_x
        handle_cy = track.centery

        pygame.draw.rect(screen, SLIDER_TRACK_COLOR, track, border_radius=SLIDER_TRACK_HEIGHT // 2)

        if value > 0:
            fill_width = int((handle_cx - SLIDER_HANDLE_RADIUS) - track.left)
            if fill_width > 0:
                fill_rect = pygame.Rect(track.left, track.top, fill_width, track.height)
                pygame.draw.rect(screen, SLIDER_FILL_COLOR, fill_rect, border_radius=SLIDER_TRACK_HEIGHT // 2)

        pygame.draw.circle(screen, SLIDER_HANDLE_COLOR, (handle_cx-20, handle_cy), SLIDER_HANDLE_RADIUS)

        label_surf = self._make_label_surf()
        label_rect = label_surf.get_rect(midbottom=(track.centerx, track.top - 6))
        screen.blit(label_surf, label_rect)

    def _make_label_surf(self) -> pygame.Surface:
        """Создаёт поверхность с подписью и значением."""
        value = self.get_value()
        pct = int(round(value * 100))
        text = f"{self.label}: {pct}%"
        font = pygame.font.Font(FONT_PATH, FONT_SIZE_BUTTON)
        return font.render(text, True, SLIDER_LABEL_COLOR)

    def handle_click(self, mouse_pos: tuple) -> bool:
        """Обрабатывает клик по ползунку. Возвращает True, если клик был по треку."""
        track = self.track_rect
        if track.collidepoint(mouse_pos):
            self._update_from_mouse(mouse_pos[0])
            self.dragging = True
            return True
        return False

    def handle_motion(self, mouse_pos: tuple) -> None:
        """Обрабатывает движение мыши при перетаскивании."""
        if self.dragging:
            self._update_from_mouse(mouse_pos[0])

    def handle_release(self) -> None:
        """Завершает перетаскивание."""
        self.dragging = False

    def _update_from_mouse(self, mouse_x: int) -> None:
        """Обновляет значение ползунка по X-координате мыши."""
        track = self.track_rect
        new_value = (mouse_x - track.left - SLIDER_HANDLE_RADIUS) / (track.width - SLIDER_HANDLE_RADIUS * 2)
        new_value = max(0.0, min(1.0, new_value))
        self.set_value(new_value)


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
        ("manual", "Мануал", "📖"),
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

        self._sliders: list[Slider] = []
        self._sliders_initialized: bool = False

        # Manual tab attributes
        self._manual_pages = self._build_manual_pages()
        self._manual_current_page = 0
        self._manual_scroll_offset = 0
        self._manual_max_scroll = 0
        self._manual_nav_left_rect = pygame.Rect(0, 0, 0, 0)
        self._manual_nav_right_rect = pygame.Rect(0, 0, 0, 0)
        self._manual_title_font = pygame.font.Font(FONT_PATH, MANUAL_FONT_SIZE_TITLE)
        self._manual_text_font = pygame.font.Font(FONT_PATH, MANUAL_FONT_SIZE_TEXT)
        self._manual_section_font = pygame.font.Font(FONT_PATH, MANUAL_FONT_SIZE_SECTION)
        self._manual_nav_font = pygame.font.Font(FONT_PATH, MANUAL_FONT_SIZE_NAV)

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
        elif self._active_tab == "manual":
            self._draw_manual_tab(screen, content_rect)

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

    def _init_sliders(self, content_rect: pygame.Rect) -> None:
        """Создаёт ползунки громкости на основе content_rect."""
        if self._sliders_initialized:
            return

        slider_width = int(content_rect.width * 0.85)
        slider_x = content_rect.topleft[0] + PADDING * 2
        start_y = content_rect.top + PADDING * 2
        gap = PADDING * 5

        self._sliders = [
            Slider(
                label="Музыка",
                get_value=lambda: self._sound_manager.music_volume,
                set_value=lambda v: setattr(self._sound_manager, 'music_volume', v),
                x=slider_x,
                y=start_y,
                width=slider_width,
            ),
            Slider(
                label="SFX",
                get_value=lambda: self._sound_manager.sound_volume,
                set_value=lambda v: setattr(self._sound_manager, 'sound_volume', v),
                x=slider_x,
                y=start_y + gap,
                width=slider_width,
            ),
        ]
        self._sliders_initialized = True

    def _draw_settings_tab(
        self, screen: pygame.Surface, content_rect: pygame.Rect
    ) -> None:
        """Рисует содержимое вкладки 'Настройки' с ползунками громкости."""
        self._init_sliders(content_rect)

        # Ползунки
        for slider in self._sliders:
            slider.draw(screen)

    # ─────────────────────── МАНУАЛ ───────────────────────

    def _build_manual_pages(self) -> list:
        """Создаёт страницы мануала. Каждая страница — список словарей с type и content."""
        return [
            # Страница 1 — Управление
            [
                {"type": "title", "content": "Управление"},
                {"type": "text", "content": "Левая кнопка мыши — выделить узел или открыть панель"},
                {"type": "text", "content": "Перетаскивание — переместить узел по полю"},
                {"type": "text", "content": "Колесико мыши — приближение/отдаление камеры"},
                {"type": "text", "content": "Кнопка в левом верхнем углу — открыть/закрыть боковую панель"},
                {"type": "text", "content": "Ctrl+ЛКМ - выделить несколько узлов для множественного перетаскивания"},
           
            ],
            # Страница 2 — Улучшение узлов
            [
                {"type": "title", "content": "Улучшение узлов"},
                {"type": "text", "content": "Каждый узел можно улучшать, повышая его уровень."},
                {"type": "text", "content": "Уровень узла влияет на его доход."},
                {"type": "section", "content": "Формула цены улучшения:"},
                {"type": "highlight", "content": "Цена = 10 × 1.5^level"},
                {"type": "text", "content": "Где level — текущий уровень узла."},
                {"type": "text", "content": "Примеры: уровень 1 >> 15, уровень 5 >> 76, уровень 10 >> 576"},
                {"type": "section", "content": "Максимальный уровень:"},
                {"type": "highlight", "content": "Максимальный уровень узла — 20"},
                {"type": "section", "content": "Доход узла:"},
                {"type": "highlight", "content": "Доход = level²"},
                {"type": "text", "content": "Примеры: уровень 1 >> 1/сек, уровень 5 >> 25/сек, уровень 10 >> 100/сек"},
            ],
            # Страница 3 — Формула дохода
            [
                {"type": "title", "content": "Формула дохода"},
                {"type": "text", "content": "Общий доход складывается из двух частей:"},
                {"type": "section", "content": "1. Доход от узлов:"},
                {"type": "highlight", "content": "Сумма(level²) для всех узлов"},
                {"type": "text", "content": "Каждый узел приносит income = level² в секунду."},
                {"type": "section", "content": "2. Доход от обходчиков:"},
                {"type": "highlight", "content": "Сумма(level² текущего узла × множитель дохода)"},
                {"type": "text", "content": "Каждый обходчик приносит доход, равный квадрату уровня узла, на котором он находится, умноженный на его множитель дохода."},
                {"type": "section", "content": "Итоговая формула:"},
                {"type": "highlight", "content": "Общий доход/сек = Σ(level² узлов) + Σ(level² узла × множитель обходчика)"},
            ],
            # Страница 4 — Обходчики BFS/DFS
            [
                {"type": "title", "content": "Обходчики BFS и DFS"},
                {"type": "text", "content": "Обходчики автоматически перемещаются по узлам графа и приносят доход."},
                {"type": "section", "content": "Покупка обходчика:"},
                {"type": "highlight", "content": "Цена = 500 × 1.8^количество_обходчиков"},
                {"type": "text", "content": "Первый обходчик — 500, второй — 900, третий — 1620 и т.д."},
                {"type": "section", "content": "Режимы обхода:"},
                {"type": "text", "content": "BFS (поиск в ширину) — обходит граф по уровням, используя очередь. Посещает все соседние узлы, затем переходит на следующий уровень."},
                {"type": "text", "content": "DFS (поиск в глубину) — уходит вглубь графа, используя стек. Идёт по одному пути до конца, затем возвращается."},
                {"type": "section", "content": "Доход обходчика:"},
                {"type": "highlight", "content": "Доход = level² текущего узла × множитель дохода"},
            ],
            # Страница 5 — Множественное перемещение
            [
                {"type": "title", "content": "Множественное перемещение"},
                {"type": "text", "content": "Вы можете перемещать несколько узлов одновременно."},
                {"type": "section", "content": "Как это работает:"},
                {"type": "text", "content": "1. Зажмите Ctrl и кликайте по узлам, чтобы выделить несколько"},
                {"type": "text", "content": "2. Перетащите любой из выделенных узлов — все выделенные узлы перемещатся вместе с ним"},
                {"type": "text", "content": "3. Кликните по пустому месту, чтобы снять выделение"},
                {"type": "section", "content": "Применение:"},
                {"type": "text", "content": "Удобно для организации графа: можно выровнять узлы, сгруппировать их по уровням или разнести для наглядности."},
            ],
            # Страница 6 — Связи между узлами
            [
                {"type": "title", "content": "Связи между узлами"},
                {"type": "text", "content": "Связи соединяют узлы, образуя граф. Обходчики перемещаются только по связанным узлам."},
                {"type": "section", "content": "Создание связи:"},
                {"type": "text", "content": "1. Выделите первый узел (клик ЛКМ)"},
                {"type": "text", "content": "2. Зажмите Shift и кликните на второй узел"},
                {"type": "text", "content": "3. Связь будет создана, если у вас достаточно средств"},
            ],
        ]

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        """Разбивает текст на строки, чтобы он помещался в заданную ширину."""
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def _draw_manual_tab(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        """Рисует содержимое вкладки 'Мануал'."""
        # 1. Заливка фона
        pygame.draw.rect(screen, MANUAL_BG_COLOR, content_rect)

        # Устанавливаем clipping rect, чтобы контент не выходил за границы панели
        old_clip = screen.get_clip()
        screen.set_clip(content_rect)

        try:
            page = self._manual_pages[self._manual_current_page]

            # 2. Заголовок страницы (первый элемент с type="title")
            title_item = page[0]
            title_surf = self._manual_title_font.render(title_item["content"], True, MANUAL_TITLE_COLOR)
            title_rect = title_surf.get_rect(midtop=(content_rect.centerx, content_rect.top + MANUAL_CONTENT_PADDING))
            screen.blit(title_surf, title_rect)

            # 3. Контент страницы (все элементы кроме заголовка)
            y = title_rect.bottom + MANUAL_SECTION_SPACING + MANUAL_CONTENT_PADDING
            content_left = content_rect.left + MANUAL_CONTENT_PADDING
            content_width = content_rect.width - MANUAL_CONTENT_PADDING * 2

            for item in page[1:]:
                item_y = y - self._manual_scroll_offset

                if item["type"] == "title":
                    # Заголовки только первый, но на всякий случай
                    lines = self._wrap_text(item["content"], self._manual_title_font, content_width)
                    for line in lines:
                        surf = self._manual_title_font.render(line, True, MANUAL_TITLE_COLOR)
                        rect = surf.get_rect(midtop=(content_rect.centerx, item_y))
                        screen.blit(surf, rect)
                        item_y += rect.height + MANUAL_LINE_SPACING
                        y += rect.height + MANUAL_LINE_SPACING

                elif item["type"] == "section":
                    lines = self._wrap_text(item["content"], self._manual_section_font, content_width)
                    for line in lines:
                        surf = self._manual_section_font.render(line, True, MANUAL_SECTION_COLOR)
                        rect = surf.get_rect(topleft=(content_left, item_y))
                        screen.blit(surf, rect)
                        item_y += rect.height + MANUAL_LINE_SPACING
                        y += rect.height + MANUAL_LINE_SPACING
                    y += MANUAL_SECTION_SPACING - MANUAL_LINE_SPACING  # добавляем межсекционный отступ

                elif item["type"] == "highlight":
                    lines = self._wrap_text(item["content"], self._manual_text_font, content_width - 15)
                    for line in lines:
                        surf = self._manual_text_font.render(line, True, MANUAL_HIGHLIGHT_COLOR)
                        # Отступ слева для highlight
                        rect = surf.get_rect(topleft=(content_left + 15, item_y))
                        screen.blit(surf, rect)
                        item_y += rect.height + MANUAL_LINE_SPACING
                        y += rect.height + MANUAL_LINE_SPACING

                elif item["type"] == "text":
                    lines = self._wrap_text(item["content"], self._manual_text_font, content_width)
                    for line in lines:
                        surf = self._manual_text_font.render(line, True, MANUAL_TEXT_COLOR)
                        rect = surf.get_rect(topleft=(content_left, item_y))
                        screen.blit(surf, rect)
                        item_y += rect.height + MANUAL_LINE_SPACING
                        y += rect.height + MANUAL_LINE_SPACING

            # 4. Вычисление max_scroll
            total_content_height = y - (title_rect.bottom + MANUAL_SECTION_SPACING + MANUAL_CONTENT_PADDING)
            available_height = content_rect.height - 60  # резервируем место для навигации
            self._manual_max_scroll = max(0, total_content_height - available_height)

            # 5. Навигационные кнопки внизу
            nav_y = content_rect.bottom - 40
            btn_size = 40

            # Левая кнопка "←"
            left_btn_rect = pygame.Rect(
                content_rect.centerx - btn_size - 10,
                nav_y,
                btn_size,
                btn_size,
            )
            self._manual_nav_left_rect = left_btn_rect

            mouse_pos = pygame.mouse.get_pos()
            left_hover = left_btn_rect.collidepoint(mouse_pos)
            left_color = MANUAL_NAV_BTN_HOVER_COLOR if left_hover else MANUAL_NAV_BTN_COLOR
            pygame.draw.rect(screen, left_color, left_btn_rect, border_radius=6)

            left_surf = self._manual_nav_font.render("<", True, MANUAL_NAV_BTN_TEXT_COLOR)
            left_text_rect = left_surf.get_rect(center=left_btn_rect.center)
            screen.blit(left_surf, left_text_rect)

            # Правая кнопка "→"
            right_btn_rect = pygame.Rect(
                content_rect.centerx + 10,
                nav_y,
                btn_size,
                btn_size,
            )
            self._manual_nav_right_rect = right_btn_rect

            right_hover = right_btn_rect.collidepoint(mouse_pos)
            right_color = MANUAL_NAV_BTN_HOVER_COLOR if right_hover else MANUAL_NAV_BTN_COLOR
            pygame.draw.rect(screen, right_color, right_btn_rect, border_radius=6)

            right_surf = self._manual_nav_font.render(">", True, MANUAL_NAV_BTN_TEXT_COLOR)
            right_text_rect = right_surf.get_rect(center=right_btn_rect.center)
            screen.blit(right_surf, right_text_rect)

            # 7. Скроллбар (если есть что скроллить)
            if self._manual_max_scroll > 0:
                scrollbar_width = 8
                scrollbar_x = content_rect.right - scrollbar_width - 4
                scrollbar_top = content_rect.top + 10
                scrollbar_height = content_rect.height - 60  # не перекрывать навигацию

                # Трек
                scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_top, scrollbar_width, scrollbar_height)
                pygame.draw.rect(screen, MANUAL_SCROLLBAR_COLOR, scrollbar_rect, border_radius=4)

                # Ручка
                handle_height = max(20, int(scrollbar_height * (available_height / total_content_height)))
                handle_y = scrollbar_top + int((self._manual_scroll_offset / self._manual_max_scroll) * (scrollbar_height - handle_height))
                handle_rect = pygame.Rect(scrollbar_x, handle_y, scrollbar_width, handle_height)
                pygame.draw.rect(screen, MANUAL_SCROLLBAR_HANDLE_COLOR, handle_rect, border_radius=4)
        finally:
            # Восстанавливаем область отсечения
            screen.set_clip(old_clip)

    def _handle_manual_tab_click(self, mouse_pos: tuple) -> bool:
        """Обрабатывает клик на вкладке 'Мануал'."""
        if self._manual_nav_left_rect.collidepoint(mouse_pos):
            if self._manual_current_page > 0:
                self._manual_current_page -= 1
                self._manual_scroll_offset = 0
            return True

        if self._manual_nav_right_rect.collidepoint(mouse_pos):
            if self._manual_current_page < len(self._manual_pages) - 1:
                self._manual_current_page += 1
                self._manual_scroll_offset = 0
            return True

        return False

    def handle_mouse_wheel(self, y: int) -> bool:
        """Обрабатывает колесико мыши для скролла. Возвращает True, если скролл был применён."""
        if self._active_tab == "manual" and self._manual_max_scroll > 0:
            self._manual_scroll_offset -= y * 20
            self._manual_scroll_offset = max(0, min(self._manual_scroll_offset, self._manual_max_scroll))
            return True
        return False

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

        if self._active_tab == "settings":
            return self._handle_settings_tab_click(mouse_pos)

        if self._active_tab == "manual":
            return self._handle_manual_tab_click(mouse_pos)

        return False

    def _handle_settings_tab_click(self, mouse_pos: tuple) -> bool:
        """Обрабатывает клик на вкладке 'Настройки' (ползунки)."""
        for slider in self._sliders:
            if slider.handle_click(mouse_pos):
                return True
        return False

    def handle_mouse_motion(self, mouse_pos: tuple) -> None:
        """Обрабатывает движение мыши (для перетаскивания ползунков)."""
        for slider in self._sliders:
            slider.handle_motion(mouse_pos)

    def handle_mouse_up(self) -> None:
        """Обрабатывает отпускание кнопки мыши (завершение перетаскивания)."""
        for slider in self._sliders:
            slider.handle_release()

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