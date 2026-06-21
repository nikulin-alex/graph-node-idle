"""
Содержит все константы, используемые в проекте.
"""

import pygame

pygame.init()
desktop_size = pygame.display.get_desktop_sizes()[0]

WINDOW_WIDTH = desktop_size[0] * 0.9
WINDOW_HEIGHT = desktop_size[1] * 0.9

NODE_IMG = "media/node.png"
HIGHLIGHTED_IMG = "media/highlighted_node.png"
NODE_SIZE = 50
NODE_SPAWN_RADIUS = 300

BALANCE_IMG = "media/balance.png"
BALANCE_FONT = 40
BALANCE_HEIGHT = 100
BALANCE_WIDTH = BALANCE_HEIGHT * 3
BALANCE_COLOR = (200, 200, 200)
INITIAL_BALANCE = 0

TOOLBAR_IMG = "media/toolbar.png"
TOOLBAR_WIDTH = 400

UPGRADE_BTN_IMG = "media/upgrade_button.png"
UPGRADE_BTN_DISABLED_IMG = "media/upgrade_button_disabled.png"
MAX_UPGRADED_BTN_IMG = "media/max_upgraded_button.png"

EDGE_COLOR = (60, 60, 60)

DELETE_NODE_PRICE = 100

# Обходчики
TRAVERSER_BASE_PRICE = 500
TRAVERSER_PRICE_GROWTH = 1.8
TRAVERSER_PATH_MAX_LENGTH = 100
TRAVERSER_COLORS = [
    (255, 100, 100),  # красный
    (100, 255, 100),  # зелёный
    (100, 100, 255),  # синий
    (255, 255, 100),  # жёлтый
    (255, 100, 255),  # пурпурный
    (100, 255, 255),  # голубой
]
