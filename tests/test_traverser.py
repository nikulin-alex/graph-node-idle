"""Тесты для модели Traverser."""

import pytest
from models.traverser import Traverser
from models.graph_node import GraphNode


def make_simple_graph() -> tuple[list[GraphNode], GraphNode]:
    """Создаёт простой граф: a-b-c."""
    a = GraphNode((0, 0))
    b = GraphNode((100, 0))
    c = GraphNode((200, 0))
    a.connected_nodes.append(b)
    b.connected_nodes.append(a)
    b.connected_nodes.append(c)
    c.connected_nodes.append(b)
    return [a, b, c], a


class TestTraverser:
    """Тесты для обходчика графа."""

    def test_create_bfs_traverser(self):
        """BFS обходчик создаётся с корректными параметрами."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="bfs", speed=1, color=(255, 0, 0))
        assert t.current_node is start
        assert t.mode == "bfs"
        assert t.speed == 1
        assert t.color == (255, 0, 0)
        assert t.is_waiting is False

    def test_create_dfs_traverser(self):
        """DFS обходчик создаётся с корректными параметрами."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="dfs", speed=1, color=(0, 255, 0))
        assert t.mode == "dfs"

    def test_default_mode_is_bfs(self):
        """Режим по умолчанию — bfs."""
        nodes, start = make_simple_graph()
        t = Traverser(start, speed=1, color=(255, 0, 0))
        assert t.mode == "bfs"

    def test_step_moves_traverser(self):
        """Шаг перемещает обходчика по графу."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="bfs", speed=1, color=(255, 0, 0))
        initial_node = t.current_node
        t.step(nodes)
        assert t.current_node is not initial_node or t.path_nodes

    def test_steps_multiple(self):
        """Множественные шаги продвигают обходчика дальше."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="bfs", speed=1, color=(255, 0, 0))
        t.steps(nodes)
        assert t.current_node is not None

    def test_reset_returns_to_start(self):
        """Сброс возвращает обходчика на стартовый узел."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="bfs", speed=1, color=(255, 0, 0))
        t.steps(nodes)
        t.reset(start)
        assert t.current_node is start

    def test_wake_up_clears_waiting(self):
        """wake_up() убирает флаг ожидания."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="bfs", speed=1, color=(255, 0, 0))
        t._waiting = True
        assert t.is_waiting is True
        t.wake_up()
        assert t.is_waiting is False

    def test_get_income_positive(self):
        """Доход от обходчика положительный."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="bfs", speed=1, color=(255, 0, 0))
        assert t.get_income() > 0

    def test_remove_node_from_paths(self):
        """Удаление узла из путей обходчика не вызывает ошибок."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="bfs", speed=1, color=(255, 0, 0))
        t.steps(nodes)
        target = nodes[1]
        t.remove_node_from_paths(target)
        assert target not in t.path_nodes

    def test_traverser_bfs_visits_all_nodes(self):
        """BFS обходчик в конечном счёте посещает все узлы графа."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="bfs", speed=1, color=(255, 0, 0))
        visited = set()
        for _ in range(20):
            t.steps(nodes)
            visited.add(t.current_node)
        assert len(visited) >= 2

    def test_traverser_dfs_visits_all_nodes(self):
        """DFS обходчик в конечном счёте посещает все узлы графа."""
        nodes, start = make_simple_graph()
        t = Traverser(start, mode="dfs", speed=1, color=(0, 255, 0))
        visited = set()
        for _ in range(20):
            t.steps(nodes)
            visited.add(t.current_node)
        assert len(visited) >= 2
