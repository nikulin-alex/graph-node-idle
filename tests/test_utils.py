"""Тесты для утилит из utils.py."""

import pytest
from utils import format_number, collision


class TestFormatNumber:
    """Тесты для format_number."""

    def test_less_than_thousand(self):
        """Числа меньше 1000 возвращаются как есть."""
        assert format_number(0) == "0"
        assert format_number(1) == "1"
        assert format_number(999) == "999"

    def test_thousands(self):
        """Числа в тысячах форматируются с суффиксом K."""
        result = format_number(1000)
        assert "K" in result
        assert result.endswith("K")

    def test_millions(self):
        """Числа в миллионах форматируются с суффиксом M."""
        result = format_number(1_000_000)
        assert "M" in result
        assert result.endswith("M")

    def test_billions(self):
        """Числа в миллиардах форматируются с суффиксом B."""
        result = format_number(1_000_000_000)
        assert "B" in result
        assert result.endswith("B")

    def test_trillions(self):
        """Числа в триллионах форматируются с суффиксом T."""
        result = format_number(1_000_000_000_000)
        assert "T" in result
        assert result.endswith("T")

    def test_large_number_format(self):
        """Очень большие числа форматируются без ошибок."""
        result = format_number(10**18)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_float_input(self):
        """Дробные числа корректно обрабатываются."""
        result = format_number(1234.56)
        assert isinstance(result, str)
        assert len(result) > 0


class TestCollision:
    """Тесты для collision."""

    def test_collision_detected(self):
        """Коллизия обнаруживается, когда точка внутри радиуса узла."""
        node = type("Node", (), {"x": 0, "y": 0})()
        assert collision((5, 5), node, 50) is True

    def test_no_collision(self):
        """Коллизия не обнаруживается, когда точка далеко от узла."""
        node = type("Node", (), {"x": 0, "y": 0})()
        assert collision((100, 100), node, 50) is False

    def test_collision_with_none_node(self):
        """Коллизия с None узлом возвращает False."""
        assert collision((0, 0), None, 50) is False

    def test_collision_at_edge(self):
        """Коллизия на границе радиуса."""
        node = type("Node", (), {"x": 0, "y": 0})()
        assert collision((24, 0), node, 50) is True
        assert collision((26, 0), node, 50) is False
