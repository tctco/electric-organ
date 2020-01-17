import pygame
from os import path

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

KEY_LIST = [pygame.K_TAB,
            pygame.K_q,
            pygame.K_w,
            pygame.K_e,
            pygame.K_r,
            pygame.K_t,
            pygame.K_y,
            pygame.K_u,
            pygame.K_i,
            pygame.K_o,
            pygame.K_p,
            pygame.K_LEFTBRACKET,
            pygame.K_RIGHTBRACKET,
            pygame.K_BACKSLASH]
WIDTH = 500
HEIGHT = 600
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BAR_SIZE = (200, 20)
BAR_POS = ((WIDTH - BAR_SIZE[0]) / 2, (HEIGHT - BAR_SIZE[1]) / 2)
BORDER_COLOR = (50, 50, 50)
BAR_COLOR = (0, 128, 0)
DEFAULT_PIECE_NAME = "script"
UI_FONT = "consolas"
UI_FONT_SIZE = 20
KEY_NUM = 14

sound_dir = path.join(path.dirname(__file__), "sound")
img_dir = path.join(path.dirname(__file__), "img")
scripts_dir = path.join(path.dirname(__file__), "scripts")
