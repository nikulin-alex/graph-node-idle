"""
Модель узла графа.
"""

from typing import Optional

from utils import cost_sigmoid


class GraphNode:
    """
    Узел графа. Может быть соединён с другими узлами.

    Attributes:
        x: Координата Х.
        y: Координата Y.
        level: Уровень узла.
        selected: Состояние (выделен или нет).
        connected_nodes: Список соединённых узлов.
    """

    ADD_NODE_CAPACITY = 5
    """
    Количество соединений, после которого цена критически возрастёт.
    Максимальное количество соединений - этот параметр, умноженный на 2.
    """
    UPGRADE_CAPACITY = 10
    """
    Количество улучшений уровня, после которого цена критически возрастёт.
    Максимальное количество улучшений - этот параметр, умноженный на 2.
    """

    def __init__(self, coords: tuple[float, float]) -> None:
        self._x: float = coords[0]
        self._y: float = coords[1]
        self._selected: bool = False
        self._connected_nodes: list[GraphNode] = list()
        self._level: int = 1

    def toggle_selected(self) -> None:
        """Переключает состояние выделения узла."""
        self._selected = not self._selected

    @property
    def x(self) -> float:
        """Координата X данного узла."""
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = value

    @property
    def y(self) -> float:
        """Координата Y данного узла."""
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = value

    @property
    def level(self) -> int:
        """Уровень узла."""
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        self._level = value

    @property
    def selected(self) -> bool:
        """Выбран ли узел."""
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value

    @property
    def max_connections(self) -> int:
        """Возвращает максимальное количество соединений узла."""
        return self.ADD_NODE_CAPACITY * 2

    @property
    def max_level(self) -> int:
        """Возвращает максимальный уровень узла."""
        return self.UPGRADE_CAPACITY * 2

    @property
    def connected_nodes(self) -> list["GraphNode"]:
        """Список узлов, соединённых с данным."""
        return self._connected_nodes

    @connected_nodes.setter
    def connected_nodes(self, value: list["GraphNode"]) -> None:
        self._connected_nodes = value

    def add_node_price(self) -> Optional[int]:
        """
        Возвращает цену добавления нового узла к текущему.

        Returns:
            Цена или None, если достигнут лимит соединений.
        """
        if len(self.connected_nodes) >= self.max_connections:
            return None
        cost = int(
            cost_sigmoid(
                x=len(self.connected_nodes),
                capacity=self.ADD_NODE_CAPACITY,
                steepness=2.5,
                max_cost=5000,
            )
        )
        return cost

    def upgrade_price(self) -> Optional[int]:
        """
        Возвращает цену улучшения узла до следующего уровня.

        Returns:
            Цена или None, если достигнут лимит улучшений.
        """
        if self._level >= self.max_level:
            return None
        return int(10 * (1.5**self.level))

    def get_income(self) -> int:
        """
        Доход, который узел приносит в секунду.
        Рассчитывается как квадрат текущего уровня.
        """
        return self._level**2
