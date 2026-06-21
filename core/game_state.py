"""
Единый источник истины для всех текущих игровых данных.
"""

from models import GraphNode, Balance, TraverserManager
from core import Camera
from ui import ToolBar, TraverserShop
from config import INITIAL_BALANCE


class GameState:
    """
    Состояние игры: узлы, баланс, камера, обходчики, магазин.

    Attributes:
        nodes: Список всех узлов графа.
        balance: Баланс игрока.
        camera: Камера для преобразования координат.
        traverser_manager: Менеджер обходчиков.
        toolbar: Панель инструментов для работы с узлами.
        traverser_shop: Магазин обходчиков.
    """

    def __init__(self) -> None:
        start_node: GraphNode = GraphNode((100, 100))
        self._nodes: list[GraphNode] = [start_node]
        self._balance: Balance = Balance(initial_balance=INITIAL_BALANCE)
        self._camera: Camera = Camera()
        self._traverser_manager: TraverserManager = TraverserManager(start_node)
        self._toolbar: ToolBar = ToolBar()
        self._traverser_shop: TraverserShop = TraverserShop()

    @property
    def toolbar(self) -> ToolBar:
        """Панель инструментов."""
        return self._toolbar

    @property
    def traverser_shop(self) -> TraverserShop:
        """Магазин обходчиков."""
        return self._traverser_shop

    @property
    def nodes(self) -> list[GraphNode]:
        """Список всех узлов графа."""
        return self._nodes

    @property
    def balance(self) -> Balance:
        """Баланс игрока."""
        return self._balance

    @property
    def camera(self) -> Camera:
        """Камера."""
        return self._camera

    @property
    def traverser_manager(self) -> TraverserManager:
        """Менеджер обходчиков."""
        return self._traverser_manager

    def update(self) -> None:
        """Обновляет состояние игры на один тик."""
        self._traverser_manager.update_all(self._nodes)
        self._balance.update(self._nodes, self._traverser_manager.traversers)
