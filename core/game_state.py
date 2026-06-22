"""
Единый источник истины для всех текущих игровых данных.
"""

from typing import Optional
from ui import ToolBar, TraverserShop, LeftPanel
from models import GraphNode, Balance, TraverserManager
from core import Camera
from config import INITIAL_BALANCE
from utils import SoundManager


class GameState:
    """
    Состояние игры: узлы, баланс, камера, обходчики, магазин, панели.

    Attributes:
        nodes: Список всех узлов графа.
        balance: Баланс игрока.
        camera: Камера для преобразования координат.
        traverser_manager: Менеджер обходчиков.
        toolbar: Правая панель инструментов для работы с узлами.
        traverser_shop: Магазин обходчиков.
        left_panel: Левая выезжающая панель с вкладками.
    """

    def __init__(self, sound_manager: Optional[SoundManager] = None) -> None:
        self._sound_manager: Optional[SoundManager] = sound_manager
        start_node: GraphNode = GraphNode((100, 100))
        self._nodes: list[GraphNode] = [start_node]
        self._balance: Balance = Balance(initial_balance=INITIAL_BALANCE)
        self._camera: Camera = Camera()
        self._traverser_manager: TraverserManager = TraverserManager(start_node)
        self._toolbar: ToolBar = ToolBar(sound_manager=sound_manager)
        self._left_panel: LeftPanel = LeftPanel(sound_manager)

    @property
    def toolbar(self) -> ToolBar:
        """Правая панель инструментов."""
        return self._toolbar

    @property
    def traverser_shop(self) -> TraverserShop:
        """Магазин обходчиков."""
        return self._left_panel._traverser_shop

    @property
    def left_panel(self) -> LeftPanel:
        """Левая выезжающая панель."""
        return self._left_panel

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

    @property
    def sound_manager(self) -> Optional[SoundManager]:
        """Менеджер звуков и музыки."""
        return self._sound_manager

    def update(self) -> None:
        """Обновляет состояние игры на один тик."""
        self._traverser_manager.update_all(self._nodes)
        self._balance.update(self._nodes, self._traverser_manager.traversers)
