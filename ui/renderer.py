"""
Отвечает за отрисовку узлов графа, рёбёр, обходчиков и их путей.
"""

import pygame

from models import GraphNode, Traverser
from core import Camera
from config import (
    NODE_SIZE,
    NODE_IMG,
    HIGHLIGHTED_IMG,
    EDGE_COLOR,
)
from utils import get_scaled_image, image_cache, scaled_cache


class Renderer:
    """
    Отвечает за отрисовку узлов графа, рёбёр, обходчиков и их путей.
    """

    @staticmethod
    def draw_edges(screen: pygame.Surface, nodes: list, camera: Camera) -> None:
        """Отрисовывает рёбра графа."""

        drawn_edges = set()
        for node in nodes:
            for connected in node.connected_nodes:

                edge_id = (id(node), id(connected))
                reverse_id = (id(connected), id(node))

                start = camera.apply((node.x, node.y))
                end = camera.apply((connected.x, connected.y))

                if edge_id not in drawn_edges and reverse_id not in drawn_edges:
                    pygame.draw.line(screen, EDGE_COLOR, start, end, width=5)
                    drawn_edges.add(edge_id)

    @staticmethod
    def draw_node(screen: pygame.Surface, node: GraphNode, camera: Camera) -> None:
        """Отрисовывает узел графа."""
        screen_pos = camera.apply((node.x, node.y))
        size = int(NODE_SIZE * camera.zoom)

        if node.selected:
            img_path = HIGHLIGHTED_IMG
            draw_size = int(size * 1.3)
        else:
            img_path = NODE_IMG
            draw_size = size

        scaled_image = get_scaled_image(scaled_cache, image_cache, img_path, draw_size)

        draw_x = screen_pos[0] - draw_size // 2
        draw_y = screen_pos[1] - draw_size // 2
        screen.blit(scaled_image, (draw_x, draw_y))

    @staticmethod
    def draw_all_nodes(screen: pygame.Surface, nodes: list, camera: Camera) -> None:
        """Отрисовывает все узлы графа."""
        for node in nodes:
            Renderer.draw_node(screen, node, camera)

    @staticmethod
    def draw_traverser_paths(
        screen: pygame.Surface, traversers: list, camera: Camera
    ) -> None:
        """Отрисовывает пути всех обходчиков."""
        for t in traversers:
            path_nodes = t.path_nodes
            for i in range(len(path_nodes) - 1):
                node_a = path_nodes[i]
                node_b = path_nodes[i + 1]
                if node_b in node_a.connected_nodes:
                    start = camera.apply((node_a.x, node_a.y))
                    end = camera.apply((node_b.x, node_b.y))
                    pygame.draw.line(screen, t.color, start, end, width=3)

    @staticmethod
    def draw_traverser_nodes(
        screen: pygame.Surface, traversers: list, camera: Camera
    ) -> None:
        """Отрисовывает текущие позиции обходчиков."""
        for t in traversers:
            if t.current_node:
                screen_pos = camera.apply((t.current_node.x, t.current_node.y))
                size = int(20 * camera.zoom)
                pygame.draw.circle(screen, t.color, screen_pos, size, width=3)
                pygame.draw.circle(screen, t.color, screen_pos, int(5 * camera.zoom))
