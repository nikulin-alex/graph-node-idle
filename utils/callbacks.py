"""Коллбэки для кнопок тулбара."""

from config import NODE_SPAWN_RADIUS, DELETE_NODE_PRICE
from utils.helpers import get_new_coords


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

    for connected in node.connected_nodes[:]:
        if node in connected.connected_nodes:
            connected.connected_nodes.remove(node)

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
