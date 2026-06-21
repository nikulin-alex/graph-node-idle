"""
Менеджер обходчиков графа.
"""

from models.graph_node import GraphNode
from models.traverser import Traverser
from config.constants import (
    TRAVERSER_COLORS,
    TRAVERSER_BASE_PRICE,
    TRAVERSER_PRICE_GROWTH,
)


class TraverserManager:
    """
    Управляет всеми обходчиками графов

    Attributes:
        start_node: Стартовый узел для новых обходчиков.
    """

    def __init__(self, start_node: GraphNode):
        self._traversers = []
        self._start_node = start_node
        self.add_traverser(mode="bfs")

    @property
    def traversers(self) -> tuple:
        """Кортеж всех обходчиков (только для чтения)."""
        return tuple(self._traversers)

    @property
    def start_node(self) -> GraphNode:
        """Стартовый узел для новых обходчиков."""
        return self._start_node

    @start_node.setter
    def start_node(self, value: GraphNode) -> None:
        self._start_node = value

    def add_traverser(self, mode: str = "bfs") -> Traverser:
        """
        Создаёт и добавляет нового обходчика.
        Возвращает объект обходчика.
        """
        color = TRAVERSER_COLORS[len(self.traversers) % len(TRAVERSER_COLORS)]
        t = Traverser(self.start_node, mode=mode.lower(), speed=1, color=color)
        self._traversers.append(t)
        return t

    def get_traverser_price(self) -> int:
        return int(
            TRAVERSER_BASE_PRICE * (TRAVERSER_PRICE_GROWTH ** len(self.traversers))
        )

    def update_all(self, nodes: list) -> None:
        """
        Обновляет всех обходчиков на один тик вперед.

        Args:
            nodes: Полный список узлов графа.
        """
        for t in self.traversers:
            if t.is_waiting:
                t.wake_up()
            t.steps(nodes)
