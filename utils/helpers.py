"""Вспомогательные функции, не зависящие от pygame."""

from math import sin, cos, radians, exp
from random import randint

from config import NODE_SPAWN_RADIUS, NODE_SIZE


def collision(world_pos, node, col_radius):
    """Проверяет, попадает ли точка в радиус узла."""
    if node is None:
        return False
    dx = world_pos[0] - node.x
    dy = world_pos[1] - node.y
    distance = dx**2 + dy**2

    click_radius = (col_radius / 2) ** 2
    if distance <= click_radius:
        return True
    return False


def get_new_coords(nodes, node, spawn_rad):
    """Генерирует новые координаты для узла без рекурсии.
    Делает до 50 попыток, после чего возвращает координаты без проверки коллизий."""
    x0, y0 = node.x, node.y
    for _ in range(50):
        angle = radians(randint(0, 360))
        x = x0 + spawn_rad * cos(angle)
        y = y0 + spawn_rad * sin(angle)

        collision_found = False
        for nd in nodes:
            if nd is node:
                continue
            if collision((x, y), nd, NODE_SIZE * 2.5):
                collision_found = True
                break

        if not collision_found:
            return (x, y)

    angle = radians(randint(0, 360))
    return (x0 + spawn_rad * cos(angle), y0 + spawn_rad * sin(angle))


def cost_sigmoid(x, capacity, steepness, max_cost):
    """Сигмоида для расчёта стоимости."""
    return round(max_cost / (1 + exp(-(x - capacity / 2) / steepness)), 2)


_format_cache = {}


def format_number(n: float) -> str:
    """Форматирует число с суффиксом (K, M, B, T, Qa, Qi)."""
    if n < 1000:
        return str(int(n))

    if n in _format_cache:
        return _format_cache[n]

    exp = 0
    temp = n
    while temp >= 1000:
        temp /= 1000
        exp += 1
    suffixes = ["", "K", "M", "B", "T", "Qa", "Qi"]
    if exp < len(suffixes):
        result = f"{temp:.2f}{suffixes[exp]}"
    else:
        result = f"{temp:.2f}e{exp * 3}"

    _format_cache[n] = result
    return result
