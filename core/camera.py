"""Отвечает за перемещение и масштабирование игрового мира."""

from config.constants import WINDOW_WIDTH, WINDOW_HEIGHT


class Camera:
    """
    Класс камеры, отвечающий за перемещение и масштабирование.

    Attributes:
        x: Координата X центра камеры.
        y: Координата Y центра камеры.
        zoom: Текущий коэффициент масштабирования.
    """

    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        self._x: int = width // 2
        self._y: int = height // 2
        self._zoom: float = 1.0
        self._min_zoom: float = 0.2
        self._max_zoom: float = 7.0
        self._half_w: float = WINDOW_WIDTH / 2
        self._half_h: float = WINDOW_HEIGHT / 2

    @property
    def x(self) -> float:
        """Координата X центра камеры."""
        return self._x

    @property
    def y(self) -> float:
        """Координата Y центра камеры."""
        return self._y

    @property
    def zoom(self) -> float:
        """Текущий коэффициент масштабирования."""
        return self._zoom

    def apply(self, pos: tuple[float, float]) -> tuple[float, float]:
        """Преобразует мировые координаты в экранные.

        Args:
            pos: Мировые координаты (x, y).
        """
        x, y = pos
        screen_x = (x - self._x) * self._zoom + self._half_w
        screen_y = (y - self._y) * self._zoom + self._half_h
        return (screen_x, screen_y)

    def unapply(self, screen_pos: tuple[float, float]) -> tuple[float, float]:
        """Преобразует экранные координаты в мировые.

        Args:
            screen_pos: Экранные координаты (x, y).

        Returns:
            Мировые координаты (x, y).
        """
        sx, sy = screen_pos
        world_x = (sx - self._half_w) / self._zoom + self._x
        world_y = (sy - self._half_h) / self._zoom + self._y
        return (world_x, world_y)

    def move(self, dx: float, dy: float) -> None:
        """Перемещает камеру на указанное смещение.

        Args:
            dx: Смещение по X в экранных координатах.
            dy: Смещение по Y в экранных координатах.
        """
        self._x += dx / self._zoom
        self._y += dy / self._zoom

    def zoom_in(self) -> None:
        """Увеличивает масштаб на 0.2 (до максимального)."""
        new_zoom = self._zoom + 0.2
        if new_zoom <= self._max_zoom:
            self._zoom = new_zoom

    def zoom_out(self) -> None:
        """Уменьшает масштаб на 0.2 (до минимального)."""
        new_zoom = self._zoom - 0.2
        if new_zoom >= self._min_zoom:
            self._zoom = new_zoom
