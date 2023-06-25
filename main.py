import pygame
import math

from board import Board
import minimax

BOARD_WIDTH = 7
BOARD_HEIGHT = 6

WINDOW_SIZE = 800

BLUE = (20, 50, 150)
BLACK = (30, 30, 30)
RED = (193, 18, 31)
YELLOW = (255, 209, 102)


class Button:
    gameMode = 0
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    
    def draw(self, surface):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action
        

class Game:
    gameMode = 0
    def __init__(self, tile_size):
        self.tile_size = tile_size

    def init_pygame(self):
        pygame.init()
        self.width = BOARD_WIDTH * self.tile_size
        self.height = (BOARD_HEIGHT + 1) * self.tile_size
        self.size = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.size)
        self.RADIUS = int(self.tile_size / 2 - 5)

        pygame.display.update()

        self.textFont = pygame.font.SysFont("Helvetica", 48, bold=True)

    # Human turn
    def humanChoice(self, board, slot):
       
        # Pick slot/column
        while True:
            if board.checkOpen(slot) == 1:
                print(board.checkOpen(slot))
                return slot
            else:
                print("Slot is full")

    def choice(self, player, board, depth, letter, slot=0):
        print(Game.gameMode)
        if Game.gameMode == 1 or player == 1:
            return self.humanChoice(board, slot)
        else:
            boardArray = board.getArray()
            output = minimax.minimaxChoice(boardArray, depth, letter)
            print("%s Pick slot %d" % (letter, output + 1))
            return output

    def draw_board(self, board):
        for c in range(BOARD_HEIGHT):
            for r in range(BOARD_WIDTH):
                pygame.draw.rect(self.screen, BLUE, (
                    r * self.tile_size, c * self.tile_size + self.tile_size, self.tile_size, self.tile_size))
                pygame.draw.circle(self.screen, BLACK, (int(
                    r * self.tile_size + self.tile_size / 2),
                                                        int(c * self.tile_size + self.tile_size + self.tile_size / 2)),
                                   self.RADIUS)

        for c in range(BOARD_HEIGHT):
            for r in range(BOARD_WIDTH):
                if board[r][c] == "X":
                    pygame.draw.circle(self.screen, RED, (int(
                        r * self.tile_size + self.tile_size / 2),
                                                          self.height - int(c * self.tile_size + self.tile_size / 2)),
                                       self.RADIUS)
                elif board[r][c] == "O":
                    pygame.draw.circle(self.screen, YELLOW, (int(
                        r * self.tile_size + self.tile_size / 2), self.height - int(
                        c * self.tile_size + self.tile_size / 2)), self.RADIUS)
        pygame.display.update()

    def draw_message(self, message, color):
        pygame.draw.rect(self.screen, BLACK, (0, 0, self.width, self.tile_size))
        text = self.textFont.render(message, True, color)
        text_rect = text.get_rect(center=(self.width / 2, self.tile_size / 2))
        self.screen.blit(text, text_rect)

    def run(self):
        
        # Game.gameMode = 1
        if Game.gameMode == 2:
            turnMessage = "Computer turn"
        else:
            turnMessage = "Player 2 turn"

        gameBoard = Board()
        running = True
        turns = 0
        depth = 6

        #Load Button
        pvp = pygame.image.load('img/pvp.png').convert_alpha()
        pvc = pygame.image.load('img/pvc.png').convert_alpha()
        play = pygame.image.load('img/play.png').convert_alpha()
        quit = pygame.image.load('img/quit.png').convert_alpha()
        back = pygame.image.load('img/back.png').convert_alpha()
        close = pygame.image.load('img/close.png').convert_alpha()
        
        
        # Setting the Button (x Position, y Postion, img, Scale)
        pvpButton = Button(100, 250, pvp, 0.8)
        pvcButton = Button(300, 250, pvc, 0.8)
        playButton = Button(250, 250, play, 0.8)
        quitButton = Button(250, 350, quit, 0.8)
        backButton = Button(100, 100, back, 0.8)
        closeButton = Button(550, 100, close, 0.8)
        
        #Screen State
        playScreen = False 
        setGameMode = False 

        board = gameBoard.getArray()
        while running:
            for event in pygame.event.get():
                if playScreen:
                    if setGameMode:
                        self.draw_board(board)
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.MOUSEMOTION:
                            pygame.draw.rect(self.screen, BLACK, (0, 0, self.width, self.tile_size))
                            posx = event.pos[0]
                            if turns % 2 == 0:
                                pygame.draw.circle(
                                    self.screen, RED, (posx, int(self.tile_size / 2)), self.RADIUS)
                            else:
                                pygame.draw.circle(
                                    self.screen, YELLOW, (posx, int(self.tile_size / 2)), self.RADIUS)
                        pygame.display.update()

                        if Game.gameMode == 2 and turns % 2 == 1:
                            print(turnMessage)
                            gameBoard.dropLetter(self.choice(
                                2, gameBoard, depth, "O"), "O")

                            if gameBoard.detectWin() == "O" and Game.gameMode == 2:
                                message = "Computer Win!"
                                print(message + "\n")
                                self.draw_message(message, YELLOW)
                                running = False

                            gameBoard.showBoard()
                            board = gameBoard.getArray()
                            self.draw_board(board)

                            turns += 1

                            if turns == 50:
                                print("Draw!\n")
                                running = False
                                pygame.time.wait(3000)

                            if not running:
                                pygame.time.wait(3000)

                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pygame.draw.rect(self.screen, BLACK, (0, 0, self.width, self.tile_size))
                            if turns % 2 == 0:
                                posx = event.pos[0]
                                col = int(math.floor(posx / self.tile_size))
                                print("Player 1 turn")
                                gameBoard.dropLetter(self.choice(
                                    1, gameBoard, depth, "X", col), "X")

                                if gameBoard.detectWin() == "X":
                                    message = "Player 1 Win!"
                                    print(message + "\n")
                                    self.draw_message(message, RED)
                                    running = False

                            else:
                                posx = event.pos[0]
                                col = int(math.floor(posx / self.tile_size))
                                print(turnMessage)
                                gameBoard.dropLetter(self.choice(
                                    2, gameBoard, depth, "O", col), "O")

                                if gameBoard.detectWin() == "O" and Game.gameMode == 1:
                                    message = "Player 2 Win!"
                                    print(message + "\n")
                                    self.draw_message(message, YELLOW)
                                    running = False


                            gameBoard.showBoard()
                            board = gameBoard.getArray()
                            self.draw_board(board)

                            turns += 1

                            if turns == 50:
                                print("Draw!\n")
                                running = False
                                pygame.time.wait(3000)

                            if not running:
                                pygame.time.wait(3000)
                    else:
                        #Display Game Mode Screen
                        self.screen.fill((253, 240, 213))
                        if pvpButton.draw(self.screen):
                            Game.gameMode = 1
                            print('masuk')
                            setGameMode = True
                        if pvcButton.draw(self.screen):
                            Game.gameMode = 2
                            print('masuk')
                            setGameMode = True
                        if backButton.draw(self.screen):
                            playScreen = False
                        if closeButton.draw(self.screen):
                            running = False
                        pygame.display.update()
                else:
                    #Display Home Page Screen
                    self.screen.fill((253, 240, 213))
                    if playButton.draw(self.screen):
                        playScreen = True
                    if quitButton.draw(self.screen):
                        running = False
                    pygame.display.update() 



if __name__ == "__main__":
    game = Game(100)
    game.init_pygame()

    game.run()

    pygame.display.quit()
    pygame.quit()
