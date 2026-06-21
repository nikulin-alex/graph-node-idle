"""Тесты для модели TraverserManager."""

import pytest
from models.traverser_manager import TraverserManager
from models.graph_node import GraphNode


class TestTraverserManager:
    """Тесты для менеджера обходчиков."""

    def test_create_manager(self):
        """Менеджер создаётся со стартовым узлом и одним BFS обходчиком."""
        start = GraphNode((0, 0))
        manager = TraverserManager(start)
        assert manager.start_node is start
        assert len(manager.traversers) == 1

    def test_add_bfs_traverser(self):
        """Добавление BFS обходчика увеличивает список."""
        start = GraphNode((0, 0))
        manager = TraverserManager(start)
        t = manager.add_traverser(mode="bfs")
        assert t is not None
        assert len(manager.traversers) == 2
        assert t.mode == "bfs"

    def test_add_dfs_traverser(self):
        """Добавление DFS обходчика."""
        start = GraphNode((0, 0))
        manager = TraverserManager(start)
        t = manager.add_traverser(mode="dfs")
        assert t.mode == "dfs"
        assert len(manager.traversers) == 2

    def test_add_traverser_case_insensitive(self):
        """Регистр режима не важен (BFS/bfs/Bfs)."""
        start = GraphNode((0, 0))
        manager = TraverserManager(start)
        t = manager.add_traverser(mode="BFS")
        assert t.mode == "bfs"

    def test_traversers_tuple_immutable(self):
        """traversers возвращает кортеж (нельзя изменить извне)."""
        start = GraphNode((0, 0))
        manager = TraverserManager(start)
        with pytest.raises(AttributeError):
            manager.traversers.append("x")

    def test_get_traverser_price_increases(self):
        """Цена обходчика растёт с каждым купленным."""
        start = GraphNode((0, 0))
        manager = TraverserManager(start)
        price1 = manager.get_traverser_price()
        manager.add_traverser()
        price2 = manager.get_traverser_price()
        assert price2 > price1

    def test_get_traverser_price_positive(self):
        """Цена обходчика всегда положительная."""
        start = GraphNode((0, 0))
        manager = TraverserManager(start)
        for _ in range(5):
            assert manager.get_traverser_price() > 0
            manager.add_traverser()

    def test_update_all_no_crash(self):
        """update_all не вызывает ошибок с простым графом."""
        start = GraphNode((0, 0))
        b = GraphNode((100, 0))
        start.connected_nodes.append(b)
        b.connected_nodes.append(start)
        manager = TraverserManager(start)
        manager.update_all([start, b])
        assert True

    def test_start_node_setter(self):
        """Стартовый узел можно изменить через setter."""
        start = GraphNode((0, 0))
        new_start = GraphNode((200, 200))
        manager = TraverserManager(start)
        manager.start_node = new_start
        assert manager.start_node is new_start
