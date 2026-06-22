"""
Сохранение и загрузка состояния игры в JSON.
Сериализует баланс, список узлов, обходчиков и настройки звука.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.game_state import GameState

from config.constants import SAVE_KEY_MUSIC_VOLUME, SAVE_KEY_SFX_VOLUME

SAVE_DIR = Path("saves")
SAVE_FILE = SAVE_DIR / "progress.json"

logger = logging.getLogger(__name__)


def _serialize_nodes(game_state: GameState) -> list[dict[str, Any]]:
    """Превращает список узлов в список словарей для JSON."""
    nodes = game_state.nodes
    node_to_idx = {id(n): i for i, n in enumerate(nodes)}

    result: list[dict[str, Any]] = []
    for node in nodes:
        result.append(
            {
                "x": node.x,
                "y": node.y,
                "level": node.level,
                "connected": [node_to_idx[id(c)] for c in node.connected_nodes],
            }
        )
    return result


def _serialize_traversers(game_state: GameState) -> list[dict[str, Any]]:
    """Превращает список обходчиков в список словарей для JSON."""
    nodes = game_state.nodes
    node_to_idx = {id(n): i for i, n in enumerate(nodes)}
    traversers = game_state.traverser_manager.traversers

    result: list[dict[str, Any]] = []
    for t in traversers:
        result.append(
            {
                "mode": t.mode,
                "speed": t.speed,
                "color": list(t.color),
                "current_node": node_to_idx.get(id(t.current_node), 0),
                "cycles_completed": t.cycles_completed,
                "visited": [
                    node_to_idx[id(n)] for n in t._visited if id(n) in node_to_idx
                ],
                "stack": [node_to_idx[id(n)] for n in t._stack if id(n) in node_to_idx],
                "queue": [node_to_idx[id(n)] for n in t._queue if id(n) in node_to_idx],
                "move_queue": [
                    node_to_idx[id(n)] for n in t._move_queue if id(n) in node_to_idx
                ],
                "path_nodes": [
                    node_to_idx[id(n)] for n in t._path_nodes if id(n) in node_to_idx
                ],
                "waiting": t.is_waiting,
            }
        )
    return result


def save_game(game_state: GameState) -> None:
    """
    Сохраняет текущее состояние игры в JSON-файл.

    Args:
        game_state: Текущее состояние игры.
    """
    data = {
        "balance": game_state.balance.balance,
        "nodes": _serialize_nodes(game_state),
        "traversers": _serialize_traversers(game_state),
        SAVE_KEY_MUSIC_VOLUME: game_state.sound_manager.music_volume,
        SAVE_KEY_SFX_VOLUME: game_state.sound_manager.sound_volume,
    }

    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Игра сохранена в %s", SAVE_FILE)
    except OSError as e:
        logger.error("Не удалось сохранить игру: %s", e)


def _restore_nodes(game_state: GameState, nodes_data: list[dict[str, Any]]) -> None:
    """Восстанавливает узлы из данных JSON."""
    from models.graph_node import GraphNode

    # Сначала создаём все узлы без связей
    nodes: list[GraphNode] = []
    for nd in nodes_data:
        node = GraphNode((nd["x"], nd["y"]))
        node.level = nd["level"]
        nodes.append(node)

    # Затем восстанавливаем связи по индексам
    for i, nd in enumerate(nodes_data):
        nodes[i].connected_nodes = [nodes[j] for j in nd["connected"]]

    # Заменяем список узлов в game_state
    game_state._nodes = nodes


def _restore_traversers(
    game_state: GameState, traversers_data: list[dict[str, Any]]
) -> None:
    """Восстанавливает обходчиков из данных JSON."""
    from models.traverser import Traverser

    nodes = game_state.nodes
    manager = game_state.traverser_manager

    manager._traversers.clear()

    for td in traversers_data:
        start_node = nodes[td["current_node"]]
        t = Traverser(
            start_node=start_node,
            mode=td["mode"],
            speed=td["speed"],
            color=tuple(td["color"]),
        )
        t._cycles_completed = td["cycles_completed"]
        t._visited = {nodes[i] for i in td["visited"]}
        t._stack = [nodes[i] for i in td["stack"]]
        t._queue = [nodes[i] for i in td["queue"]]
        t._move_queue = [nodes[i] for i in td["move_queue"]]
        t._path_nodes = [nodes[i] for i in td["path_nodes"]]
        t._waiting = td["waiting"]

        manager._traversers.append(t)


def load_game(game_state: GameState) -> bool:
    """
    Загружает состояние игры из JSON-файла (если он существует).

    Args:
        game_state: Объект состояния, в который будут загружены данные.

    Returns:
        True, если сохранение найдено и загружено, иначе False.
    """
    if not SAVE_FILE.exists():
        logger.info("Сохранение не найдено, начинаем новую игру.")
        return False

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
    except Exception as e:
        logger.error("Ошибка чтения сохранения: %s", e)
        return False

    try:
        _restore_nodes(game_state, data["nodes"])

        game_state.balance._balance = data["balance"]

        _restore_traversers(game_state, data["traversers"])

        # Восстановление громкости звука
        sound_manager = game_state.sound_manager
        if sound_manager is not None:
            music_volume = data.get(SAVE_KEY_MUSIC_VOLUME)
            sfx_volume = data.get(SAVE_KEY_SFX_VOLUME)
            if music_volume is not None:
                sound_manager.music_volume = music_volume
            if sfx_volume is not None:
                sound_manager.sound_volume = sfx_volume

        if game_state.nodes:
            game_state.traverser_manager._start_node = game_state.nodes[0]

        logger.info("Игра загружена из %s", SAVE_FILE)
        return True
    except Exception as e:
        logger.error("Ошибка:", e)
