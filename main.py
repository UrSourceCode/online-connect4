import numpy as np
import pygame


BOARD_WIDTH = 700
BOARD_HEIGHT = 600

class Game:
    def __init__(self, size):
        self.board = np.zeros((size, size))
        self.size = size

    def init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
        self.screen = screen

if __name__ == "__main__":
    g = Game(size=10)
    g.init_pygame()