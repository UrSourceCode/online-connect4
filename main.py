import numpy as np
import pygame


BOARD_WIDTH = 7
BOARD_HEIGHT = 6

WINDOW_SIZE = 800

background_color = (0, 0, 255)
border_color = (255, 255, 255)
text_color = (0, 0, 0)
title_text = "Online Connect-4"

class Game:
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.board_width = BOARD_WIDTH
        self.board_height = BOARD_HEIGHT
        self.board = np.zeros((self.board_height, self.board_width))
        self.window_width = WINDOW_SIZE
        self.window_height = WINDOW_SIZE
        self.border_color = border_color

    def init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.screen = screen
        pygame.display.set_caption("Online Connect4")
        self.title_font = pygame.font.Font(None, 48)


    def draw_board(self):
        self.screen.fill(border_color)

        board_x = (self.window_width - (self.tile_size * self.board_width)) // 2
        board_y = (self.window_height - (self.tile_size * self.board_height)) // 2

        title_text_surface = self.title_font.render(title_text, True, text_color)
        title_text_x = (self.window_width - title_text_surface.get_width()) // 2
        title_text_y = board_y - title_text_surface.get_height() - 20
        self.screen.blit(title_text_surface, (title_text_x, title_text_y))

        for row in range(self.board_height):
            for col in range(self.board_width):
                tile_x = board_x + (col * self.tile_size)
                tile_y = board_y + (row * self.tile_size)

                pygame.draw.rect(self.screen, background_color, (tile_x + 1, tile_y + 1, self.tile_size - 2, self.tile_size - 2))


    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_board()

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game(100)
    game.init_pygame()

    game.run()