"""Тесты для модели GraphNode."""

import pytest
from models.graph_node import GraphNode


class TestGraphNode:
    """Тесты для создания и базовых операций с узлами графа."""

    def test_create_node(self):
        """Узел создаётся с заданными координатами и уровнем 1."""
        node = GraphNode((100, 200))
        assert node.x == 100
        assert node.y == 200
        assert node.level == 1
        assert node.connected_nodes == []
        assert node.selected is False

    def test_node_level_property(self):
        """Уровень узла можно изменять через property."""
        node = GraphNode((0, 0))
        node.level = 10
        assert node.level == 10

    def test_node_selected_property(self):
        """Флаг selected можно устанавливать."""
        node = GraphNode((0, 0))
        assert node.selected is False
        node.selected = True
        assert node.selected is True

    def test_connected_nodes_mutability(self):
        """connected_nodes возвращает изменяемый список."""
        node1 = GraphNode((0, 0))
        node2 = GraphNode((100, 100))
        node1.connected_nodes.append(node2)
        assert node2 in node1.connected_nodes

    def test_get_income_scales_with_level(self):
        """Доход узла растёт с уровнем."""
        node = GraphNode((0, 0))
        income_low = node.get_income()
        node.level = 5
        income_high = node.get_income()
        assert income_high > income_low

    def test_get_income_positive(self):
        """Доход узла всегда положительный."""
        node = GraphNode((0, 0))
        for level in range(1, 20):
            node.level = level
            assert node.get_income() > 0

    def test_add_node_price_none_at_max_connections(self):
        """Цена добавления узла возвращает None при достижении лимита соединений."""
        node = GraphNode((0, 0))
        max_conn = node.max_connections
        for i in range(max_conn):
            node.connected_nodes.append(GraphNode((100 * i, 0)))
        assert node.add_node_price() is None

    def test_add_node_price_returns_int(self):
        """Цена добавления узла возвращает int."""
        node = GraphNode((0, 0))
        price = node.add_node_price()
        assert isinstance(price, int)
        assert price > 0

    def test_upgrade_price_none_at_max_level(self):
        """Цена улучшения возвращает None на максимальном уровне."""
        node = GraphNode((0, 0))
        node.level = node.max_level
        assert node.upgrade_price() is None

    def test_upgrade_price_increases_with_level(self):
        """Цена улучшения растёт с уровнем узла."""
        node = GraphNode((0, 0))
        price_low = node.upgrade_price()
        node.level = 5
        price_high = node.upgrade_price()
        assert price_high > price_low

    def test_upgrade_price_returns_int(self):
        """Цена улучшения возвращает int."""
        node = GraphNode((0, 0))
        price = node.upgrade_price()
        assert isinstance(price, int)
        assert price > 0

    def test_multiple_nodes_independent(self):
        """Разные узлы не влияют на уровни друг друга."""
        node1 = GraphNode((0, 0))
        node2 = GraphNode((100, 100))
        node1.level = 10
        assert node2.level == 1

    def test_max_connections_property(self):
        """max_connections возвращает корректное значение."""
        node = GraphNode((0, 0))
        assert node.max_connections == 10

    def test_max_level_property(self):
        """max_level возвращает корректное значение."""
        node = GraphNode((0, 0))
        assert node.max_level == 20
