"""Тесты для модели Balance."""

import pytest
from models.balance import Balance
from models.graph_node import GraphNode


class TestBalance:
    """Тесты для баланса игрока."""

    def test_initial_balance(self):
        """Баланс инициализируется с заданным значением."""
        b = Balance(initial_balance=1000)
        assert b.balance == 1000

    def test_default_initial_balance(self):
        """Баланс по умолчанию равен 0."""
        b = Balance()
        assert b.balance == 0

    def test_initial_income_zero(self):
        """Начальный доход равен 0."""
        b = Balance()
        assert b.income == 0

    def test_balance_setter(self):
        """Баланс можно изменять через setter."""
        b = Balance(initial_balance=500)
        b.balance = 1000
        assert b.balance == 1000

    def test_balance_cannot_go_negative(self):
        """Баланс не может уходить в отрицательные значения (setter защищает)."""
        b = Balance(initial_balance=100)
        b.balance = -50
        assert b.balance == 0

    def test_update_with_no_nodes(self):
        """Обновление с пустым списком узлов не меняет баланс."""
        b = Balance(initial_balance=1000)
        b.update([], [])
        assert b.balance == 1000

    def test_update_adds_node_income(self):
        """Обновление добавляет доход от узлов к балансу."""
        b = Balance(initial_balance=0)
        node = GraphNode((0, 0))
        node.level = 1
        b.update([node], [])
        expected_income = node.get_income()
        assert b.balance == expected_income

    def test_income_calculated_from_nodes(self):
        """Доход рассчитывается как сумма доходов всех узлов."""
        b = Balance(initial_balance=0)
        node1 = GraphNode((0, 0))
        node2 = GraphNode((100, 0))
        node1.level = 1
        node2.level = 2
        b.update([node1, node2], [])
        expected = node1.get_income() + node2.get_income()
        assert b.income == expected

    def test_balance_accumulates_over_multiple_updates(self):
        """Баланс накапливается при нескольких обновлениях."""
        b = Balance(initial_balance=0)
        node = GraphNode((0, 0))
        for _ in range(5):
            b.update([node], [])
        expected = node.get_income() * 5
        assert b.balance == expected

    def test_update_with_traversers(self):
        """Обновление с обходчиками не ломается."""
        b = Balance(initial_balance=100)
        node = GraphNode((0, 0))
        from models.traverser import Traverser

        t = Traverser(node, mode="bfs", speed=1, color=(255, 0, 0))
        b.update([node], [t])
        assert b.balance >= 100
