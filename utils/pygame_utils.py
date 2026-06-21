"""Утилиты для работы с pygame: загрузка изображений, кэши, отрисовка текста."""

from pygame import Rect, image, transform

# Кэши для изображений и текста
image_cache: dict = {}
text_cache: dict = {}
scaled_cache: dict = {}


def get_image(image_cache: dict, path: str):
    """Кэширует загрузку изображения (оптимизация pygame.image.load()).

    Args:
        image_cache: Словарь кэша.
        path: Путь к загружаемому изображению.

    Returns:
        Загруженная поверхность pygame.
    """
    if path not in image_cache:
        image_cache[path] = image.load(path).convert_alpha()
    return image_cache[path]


def get_scaled_image(scaled_cache: dict, image_cache: dict, path: str, size: int):
    """Возвращает масштабированное изображение, кэшируя результат.

    Args:
        scaled_cache: Словарь кэша масштабированных изображений.
        image_cache: Словарь кэша исходных изображений.
        path: Путь к файлу.
        size: Размер (функция написана для отрисовки квадратов).

    Returns:
        Масштабированная поверхность pygame.
    """
    key = (path, size)
    if key not in scaled_cache:
        img = get_image(image_cache, path)
        scaled_cache[key] = transform.scale(img, (size, size))
    return scaled_cache[key]


def clear_scaled_cache(scaled_cache):
    """Очищает кэш масштабированных изображений (при смене размера окна)."""
    scaled_cache.clear()


def render_text(text_cache, font, text, antialias, color):
    """Кэширует результат font.render().

    Args:
        text_cache: Словарь кэша текста.
        font: Шрифт pygame.
        text: Текст для отрисовки.
        antialias: Сглаживание.
        color: Цвет текста.

    Returns:
        Поверхность с отрисованным текстом.
    """
    key = (id(font), text, antialias, color)
    if key not in text_cache:
        text_cache[key] = font.render(text, antialias, color)
    return text_cache[key]


def clear_text_cache(text_cache):
    """Очищает кэш текста."""
    text_cache.clear()


def rect(base_rect, coords_list, toolbar_object) -> Rect:
    """Вычисляет прямоугольник на основе базового rect и координат на спрайте.

    Args:
        base_rect: Прямоугольник фона тулбара.
        coords_list: (x, y, width, height) исходные координаты на спрайте.
        toolbar_object: Объект тулбара (нужен для _image_w, _image_h).

    Returns:
        Вычисленный Rect.
    """
    scale_x = base_rect.width / toolbar_object._image_w
    scale_y = base_rect.height / toolbar_object._image_h

    x = base_rect.left + coords_list[0] * scale_x
    y = base_rect.top + coords_list[1] * scale_y
    w = coords_list[2] * scale_x
    h = coords_list[3] * scale_y

    return Rect(x, y, w, h)
