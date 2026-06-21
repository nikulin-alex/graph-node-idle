"""Ядро игры: камера, игровой цикл, обработка событий."""

from core.camera import Camera
from core.game_loop import GameLoop
from core.game_state import GameState
from core.event_handler import EventHandler

__all__ = [
    "Camera",
    "GameLoop",
    "GameState",
    "EventHandler",
]
