"""Коллбэки для кнопок тулбара."""

from typing import Optional

from config import NODE_SPAWN_RADIUS, DELETE_NODE_PRICE
from utils.helpers import get_new_coords


def _find_closest_node(nodes: list, target_node, exclude=None):
    """Находит ближайший узел к target_node по евклидову расстоянию.

    Args:
        nodes: Полный список узлов графа.
        target_node: Узел, для которого ищем ближайшего соседа.
        exclude: Узел, который нужно исключить из поиска (например, удаляемый).

    Returns:
        Ближайший узел или None, если подходящих узлов нет.
    """
    closest = None
    min_dist = float("inf")
    for n in nodes:
        if n is target_node or n is exclude:
            continue
        dx = n.x - target_node.x
        dy = n.y - target_node.y
        dist = dx * dx + dy * dy
        if dist < min_dist:
            min_dist = dist
            closest = n
    return closest


def callback1(nodes, node, node_class, balance, price, **kwargs):
    """Добавляет новый узел с уровнем 1.

    Returns:
        Новый узел или None при ошибке.
    """
    if price is None or balance.balance < price:
        return None
    balance.balance -= price
    coords = get_new_coords(nodes, node, NODE_SPAWN_RADIUS)
    new_node = node_class(coords)
    sound_manager = kwargs.get("sound_manager")
    if sound_manager is not None:
        sound_manager.play_upgrade()
    return new_node


def callback2(node, balance, price, **kwargs):
    """Увеличивает уровень выбранного узла на 1.

    Returns:
        Узел или None при ошибке.
    """
    if price is None or balance.balance < price:
        return None
    balance.balance -= price
    node.level += 1
    sound_manager = kwargs.get("sound_manager")
    if sound_manager is not None:
        sound_manager.play_upgrade()
    return node


def callback3(nodes, node, balance, price, traverser_manager, toolbar, **kwargs):
    """Удаляет выбранный узел.

    Returns:
        True при успешном удалении, None при ошибке.
    """
    if price is None or balance.balance < price:
        return None

    if node is nodes[0]:
        return None

    balance.balance -= price

    former_neighbors = node.connected_nodes[:]

    for connected in node.connected_nodes[:]:
        if node in connected.connected_nodes:
            connected.connected_nodes.remove(node)

    for neighbor in former_neighbors:
        if not neighbor.connected_nodes:
            closest = _find_closest_node(nodes, neighbor, exclude=node)
            if closest is not None:
                neighbor.connected_nodes.append(closest)
                closest.connected_nodes.append(neighbor)

    for t in traverser_manager.traversers:
        if t.current_node is node:
            t.reset(nodes[0])
        else:
            t.path_nodes = [n for n in t.path_nodes if n is not node]
            if not t.path_nodes:
                t.path_nodes = [nodes[0]]
            t._move_queue = [n for n in t._move_queue if n is not node]
        t._invalidate_path_cache()

    if toolbar.target_node is node:
        toolbar.target_node.selected = False
        toolbar.target_node = None
        toolbar.is_triggered = False

    nodes.remove(node)
    return True
