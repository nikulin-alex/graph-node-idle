"""
Модель обходчика графа.
Обходчики опционально используют DFS или BFS(по умолчанию).
"""

from typing import Optional

from models.graph_node import GraphNode
from config.constants import TRAVERSER_PATH_MAX_LENGTH


class Traverser:
    """
    Обходчик графа, перемещающийся по узлам.

    Attributes:
        current_node: Узел, на котором в данный момент стоит обходчик.
        mode: Режим обхода (DFS/BFS).
        speed: Количество шагов за один тик.
        color: Цвет для отрисовки.
        cycles_completed: Количество завершённых циклов обхода.
        income_multiplier: Множитель дохода.
    """

    def __init__(
        self,
        start_node: GraphNode,
        mode: str = "bfs",
        speed: int = 1,
        color: tuple[int, int, int] = (100, 255, 100),
    ) -> None:
        self._current_node: GraphNode = start_node
        self._mode: str = mode
        self._speed: int = speed
        self._visited: set = set()
        self._stack: list = [start_node]
        self._queue: list = [start_node]
        self._cycles_completed: int = 0
        self._income_multiplier: float = 1.0
        self._color: tuple[int, int, int] = color
        self._path_nodes: list = [start_node]
        self._waiting: bool = False
        self._move_queue: list = []
        self._path_cache: dict = {}

    @property
    def speed(self) -> int:
        """Скорость обходчика, т.е, количество шагов, совершаемых за единицу времени."""
        return self._speed

    @property
    def current_node(self) -> GraphNode:
        """Текущий узел, на котором находится обходчик."""
        return self._current_node

    @property
    def mode(self) -> str:
        """Режим обхода ('bfs' или 'dfs')."""
        return self._mode

    @property
    def color(self) -> tuple[int, int, int]:
        """Цвет обходчика для отрисовки."""
        return self._color

    @property
    def cycles_completed(self) -> int:
        """Количество завершённых циклов обхода."""
        return self._cycles_completed

    @property
    def path_nodes(self) -> list:
        """Список узлов, образующих путь обходчика (для отрисовки)."""
        return self._path_nodes

    @path_nodes.setter
    def path_nodes(self, value: list) -> None:
        """Устанавливает список узлов пути обходчика."""
        self._path_nodes = value

    @property
    def is_waiting(self) -> bool:
        """Ожидает ли обходчик появления новых узлов."""
        return self._waiting

    def _invalidate_path_cache(self) -> None:
        """Сбрасывает кэш путей при изменении графа."""
        self._path_cache.clear()

    def step(self, nodes: list) -> Optional[GraphNode]:
        """
        Выполняет шаг обхода.

        Args:
            nodes: Полный список узлов графа.

        Returns:
            Текущий узел после выполнения шага или None, если обходчик дошел до конца логики алгоритма поиска пути.
        """
        prev_node = self._current_node
        if self._move_queue:
            next_node = self._move_queue.pop(0)
            if next_node in self._current_node.connected_nodes:
                self._current_node = next_node
        else:
            if self._mode == "bfs":
                self._plan_bfs_move()
            else:
                self._plan_dfs_move()

            if not self._move_queue:
                return None

        if self._current_node is not prev_node:
            self._path_nodes.append(self._current_node)
            if len(self._path_nodes) > TRAVERSER_PATH_MAX_LENGTH:
                self._path_nodes.pop(0)

        return self._current_node

    def steps(self, nodes: list) -> GraphNode:
        """
        Функция, масштабирующая шаг обходчика на его скорость.

        Args:
            nodes: Полный список узлов графа.

        Returns:
            Текущий узел после выполнения шага.
        """
        for _ in range(self._speed):
            res = self.step(nodes)
            if res is None:
                break

        return self.current_node

    def _plan_dfs_move(self) -> None:
        """Планирует перемещение к следующему узлу согласно DFS."""
        if self._waiting:
            return None

        if not self._stack:
            if len(self._visited) > 1:
                self._finish_cycle()
            else:
                self._waiting = True
            return None

        target = None

        while self._stack and target is None:
            candidate = self._stack.pop(-1)
            if candidate not in self._visited:
                target = candidate

        if target is None:
            if len(self._visited) > 1:
                self._finish_cycle()
            else:
                self._waiting = True
            return None

        path = self._find_shortest_path(self._current_node, target)
        if path and len(path) > 1:
            self._move_queue = path[1:]
        self._visited.add(target)
        for neighbor in reversed(target.connected_nodes):
            if neighbor not in self._visited and neighbor not in self._stack:
                self._stack.append(neighbor)

    def _plan_bfs_move(self):
        """Планирует перемещение к следующему узлу согласно BFS."""
        if self._waiting:
            return

        if not self._queue:
            if len(self._visited) > 1:
                self._finish_cycle()
            else:
                self._waiting = True
            return

        target = None
        while self._queue and target is None:
            candidate = self._queue.pop(0)
            if candidate not in self._visited:
                target = candidate

        if target is None:
            if len(self._visited) > 1:
                self._finish_cycle()
            else:
                self._waiting = True
            return

        path = self._find_shortest_path(self._current_node, target)
        if path and len(path) > 1:
            self._move_queue = path[1:]
        self._visited.add(target)
        for neighbor in target.connected_nodes:
            if neighbor not in self._visited and neighbor not in self._queue:
                self._queue.append(neighbor)

    def _find_shortest_path(
        self, start: GraphNode, target: GraphNode
    ) -> Optional[list]:
        """
        Ищет кратчайший путь между двумя узлами графа(используя BFS).

        Args:
            start: Начальный узел.
            target: Целевой узел.

        Returns:
            Список узлов [start, ..., target] или None, если путь не найден.
        """

        if start is target:
            return [start]

        cache_key = (id(start), id(target))
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]

        visited = {start}
        queue = [[start]]

        while queue:
            path = queue.pop(0)
            node = path[-1]
            for neighbor in node.connected_nodes:
                if neighbor is target:
                    result = path + [neighbor]
                    self._path_cache[cache_key] = result
                    return result
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        self._path_cache.clear()
        return None

    def _finish_cycle(self) -> None:
        """Завершает текущий цикл обхода и сбрасывает состояние."""
        self._cycles_completed += 1
        self._visited = set()
        self._stack = [self._current_node]
        self._queue = [self._current_node]
        self._move_queue = list()
        self._path_nodes.clear()
        self._path_nodes.append(self._current_node)
        self._waiting = False

    def get_income(self) -> int:
        """
        Возвращает доход от обходчика.
        Рассчитывается как квадрат текущего узла.
        """
        income = int(self._current_node.level**2)
        return int(income * self._income_multiplier)

    def reset(self, start_node: GraphNode) -> None:
        """
        Сбрасывает обходчика на указанный узел.

        Args:
            start_node: Новый стартовый узел.
        """
        self._current_node = start_node
        self._visited = set()
        self._stack = [self._current_node]
        self._queue = [self._current_node]
        self._path_nodes = [start_node]
        self._move_queue = list()
        self._waiting = False

    def remove_node_from_paths(self, node: GraphNode) -> None:
        """
        Удаляет ссылки на узел из путей обходчика, вызывается при удалении узла из графа.
        """
        self._path_nodes = [n for n in self._path_nodes if n is not node]
        if not self._path_nodes:
            self._path_nodes = [self._current_node]
        self._move_queue = [n for n in self._move_queue if n is not node]
        self._invalidate_path_cache()

    def wake_up(self) -> None:
        """Пробуждает обходчика, заполняя очередь и стек соседями текущего узла."""
        current = self._current_node
        self.reset(current)
        for neighbor in current.connected_nodes:
            self._queue.append(neighbor)
            self._stack.append(neighbor)
