import pygame
import math
from ast import literal_eval
import json

from board import Board
import minimax

import socket
import sys
from threading import Thread

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_address = "127.0.0.1"
port = 8081

server.connect((ip_address, port))

client_id = int(server.recv(2048).decode().split()[-1])
print("Connected to server with ID", client_id)

json_data = {
    "game": []
}

# Get initial game data from server
data = server.recv(2048).decode()
try:
    json_data = json.loads(data)
except ValueError as e:
    sys.stdout.write(data)

group_id = 0

def send_msg(sock, inp=-1):
    while True:
        if inp == -1:
            continue

        sock.send((str(client_id) + ":" + inp).encode())
        inp = -1

def recv_msg(sock):
    while True:
        data = sock.recv(2048).decode()

        try:
            global json_data
            json_data = json.loads(data)
        except ValueError as e:
            sys.stdout.write(data)


BOARD_WIDTH = 7
BOARD_HEIGHT = 6

WINDOW_SIZE = 800

TILE_SIZE = 100

BLUE = (20, 50, 150)
BLACK = (30, 30, 30)
RED = (193, 18, 31)
YELLOW = (255, 209, 102)


class Button:
    gameMode = 0

    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width * scale), int(height * scale))
        )
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

    def update(self, new_text, new_position):
        self.image = pygame.font.SysFont("Arial", 48, bold=True).render(new_text, True, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = new_position


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
                return slot
            else:
                print("Slot is full")

    def choice(self, player, board, depth, letter, slot=0):
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
                pygame.draw.rect(
                    self.screen,
                    BLUE,
                    (
                        r * self.tile_size,
                        c * self.tile_size + self.tile_size,
                        self.tile_size,
                        self.tile_size,
                    ),
                )
                pygame.draw.circle(
                    self.screen,
                    BLACK,
                    (
                        int(r * self.tile_size + self.tile_size / 2),
                        int(c * self.tile_size + self.tile_size + self.tile_size / 2),
                    ),
                    self.RADIUS,
                )

        for c in range(BOARD_HEIGHT):
            for r in range(BOARD_WIDTH):
                if board[r][c] == "X":
                    pygame.draw.circle(
                        self.screen,
                        RED,
                        (
                            int(r * self.tile_size + self.tile_size / 2),
                            self.height - int(c * self.tile_size + self.tile_size / 2),
                        ),
                        self.RADIUS,
                    )
                elif board[r][c] == "O":
                    pygame.draw.circle(
                        self.screen,
                        YELLOW,
                        (
                            int(r * self.tile_size + self.tile_size / 2),
                            self.height - int(c * self.tile_size + self.tile_size / 2),
                        ),
                        self.RADIUS,
                    )
        pygame.display.update()

    def draw_message(self, message, color):
        pygame.draw.rect(self.screen, BLACK, (0, 0, self.width, self.tile_size))
        text = self.textFont.render(message, True, color)
        text_rect = text.get_rect(center=(self.width / 2, self.tile_size / 2))
        self.screen.blit(text, text_rect)

    def run(self):
        if Game.gameMode == 2:
            turnMessage = "Computer turn"
        else:
            turnMessage = "Player 2 turn"

        gameBoard = Board()
        running = True
        turns = 0
        depth = 6

        # Load Button
        pvp = pygame.image.load("img/pvp.png").convert_alpha()
        pvc = pygame.image.load("img/pvc.png").convert_alpha()
        online = pygame.image.load("img/online.png").convert_alpha()
        play = pygame.image.load("img/play.png").convert_alpha()
        create = pygame.image.load("img/create.png").convert_alpha()
        join = pygame.image.load("img/join.png").convert_alpha()
        roomSelection = pygame.image.load("img/example room 0.png").convert_alpha()
        quit = pygame.image.load("img/quit.png").convert_alpha()
        back = pygame.image.load("img/back.png").convert_alpha()
        close = pygame.image.load("img/close.png").convert_alpha()

        # Setting the Button (x Position, y Postion, img, Scale)
        pvpButton = Button(100, 250, pvp, 0.8)
        pvcButton = Button(268.5, 250, pvc, 0.8)
        onlineButton = Button(437, 250, online, 0.8)
        playButton = Button(250, 250, play, 0.8)
        quitButton = Button(250, 350, quit, 0.8)
        backButton = Button(100, 100, back, 0.8)
        closeButton = Button(550, 100, close, 0.8)
        createButton = Button(250, 250, create, 0.8)
        joinButton = Button(250, 320, join, 0.8)

        roomSelectionButtons = []

        x_position = 260
        y_position = 250

        button_spacing = 80

        for i, room in enumerate(json_data["game"]):
            gid = room["room"]
            button_text = "Room " + str(gid)
            button_position = (x_position, y_position)
            roomSelectionButton = Button(button_position[0], button_position[1], roomSelection, 0.8)
            roomSelectionButton.update(button_text, button_position)
            roomSelectionButtons.append(roomSelectionButton)

            y_position += button_spacing

        # Screen State
        playScreen = False
        gameModeSet = False
        roomSet = False
        roomSelection = False

        sendMessage = -1

        global board
        board = gameBoard.getArray()

        global group_id

        while running:
            for event in pygame.event.get():
                if playScreen:
                    if gameModeSet and (
                        Game.gameMode != 3
                        or (Game.gameMode == 3 and roomSet and roomSelection)
                    ):
                        # Check if game is over
                        try:
                            game_over = json_data["game"][group_id]["game_over"]
                            waiting_player = True if json_data["game"][group_id]["player"]["yellow_id"] == -1 else False

                        except:
                            game_over = False
                            waiting_player = True

                        if Game.gameMode == 3 and game_over:
                            print("Game Over")

                            # Check if client is the winner
                            if client_id == json_data["game"][group_id]["winner_id"]:
                                message = "You Win!"
                            else:
                                message = "You Lose!"

                            # Check if red win
                            if json_data["game"][group_id]["winner_id"] == json_data["game"][group_id]["player"]["red_id"]:
                                self.draw_message(message, RED)
                            else:
                                self.draw_message(message, YELLOW)

                            running = False

                        elif Game.gameMode == 3 and waiting_player:
                            self.draw_message("Waiting for player...", RED)

                        if Game.gameMode == 3 and turns > 0:
                            self.draw_board(json_data["game"][group_id]["board"])
                        else:
                            self.draw_board(board)

                        if event.type == pygame.QUIT:
                            running = False
                            server.close()
                            pygame.display.quit()
                            pygame.quit()
                            sys.exit()
                            break

                        if Game.gameMode == 2 and turns % 2 == 1:
                            print(turnMessage)
                            gameBoard.dropLetter(
                                self.choice(2, gameBoard, depth, "O"), "O"
                            )

                            if gameBoard.detectWin() == "O" and Game.gameMode == 2:
                                message = "Computer Win!"
                                print(message + "\n")
                                self.draw_message(message, YELLOW)
                                running = False

                            board = gameBoard.getArray()
                            self.draw_board(board)

                            turns += 1

                            if turns == 50:
                                print("Draw!\n")
                                running = False

                        if event.type == pygame.MOUSEMOTION and (Game.gameMode != 3 or (Game.gameMode == 3 and not waiting_player)):
                            pygame.draw.rect(
                                self.screen, BLACK, (0, 0, self.width, self.tile_size)
                            )
                            posx = int(event.pos[0]//self.tile_size*self.tile_size + self.tile_size/2)
                            if turns % 2 == 0:
                                pygame.draw.circle(
                                    self.screen,
                                    RED,
                                    (posx, int(self.tile_size / 2)),
                                    self.RADIUS,
                                )
                            else:
                                pygame.draw.circle(
                                    self.screen,
                                    YELLOW,
                                    (posx, int(self.tile_size / 2)),
                                    self.RADIUS,
                                )
                            pygame.display.update()

                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pygame.draw.rect(
                                self.screen, BLACK, (0, 0, self.width, self.tile_size)
                            )

                            posx = event.pos[0]
                            col = int(math.floor(posx / self.tile_size))

                            if Game.gameMode == 3:
                                Thread(
                                    target=send_msg,
                                    args=(
                                        server,
                                        str(col + 1),
                                    ),
                                ).start()
                                turns += 2

                                self.draw_board(json_data["game"][group_id]["board"])

                            else:
                                if turns % 2 == 0:
                                    gameBoard.dropLetter(
                                        self.choice(1, gameBoard, depth, "X", col), "X"
                                    )

                                    if gameBoard.detectWin() == "X":
                                        message = "Player 1 Win!"
                                        print(message + "\n")
                                        self.draw_message(message, RED)
                                        running = False

                                else:
                                    gameBoard.dropLetter(
                                        self.choice(2, gameBoard, depth, "O", col), "O"
                                    )

                                    if (
                                        gameBoard.detectWin() == "O"
                                        and Game.gameMode == 1
                                    ):
                                        message = "Player 2 Win!"
                                        print(message + "\n")
                                        self.draw_message(message, YELLOW)
                                        running = False

                                board = gameBoard.getArray()
                                self.draw_board(board)

                                turns += 1

                            if turns == 50:
                                print("Draw!\n")
                                self.draw_message("Draw!", BLACK)
                                running = False

                        if not running:
                            pygame.time.wait(3000)

                    elif gameModeSet and Game.gameMode == 3 and not roomSet:
                        Thread(target=recv_msg, args=(server,)).start()

                        # Display Create or Join Room Screen
                        self.screen.fill((253, 240, 213))
                        if createButton.draw(self.screen):
                            server.send((str(client_id) + ":1").encode())
                            roomSet = True
                            roomSelection = True
                            group_id = len(json_data["game"])
                            print("Room Created")
                        if len(json_data["game"]) > 0 and joinButton.draw(self.screen):
                            server.send((str(client_id) + ":2").encode())
                            roomSet = True
                            print("Room Joining")
                        if backButton.draw(self.screen):
                            gameModeSet = False
                        if closeButton.draw(self.screen):
                            running = False
                            server.close()
                            pygame.display.quit()
                            pygame.quit()
                            sys.exit()
                            break
                        pygame.display.update()

                    elif (
                        gameModeSet
                        and Game.gameMode == 3
                        and not roomSelection
                        and roomSet
                    ):
                        # Display Room Selection Screen
                        self.screen.fill((253, 240, 213))

                        # TODO: Change the button text to room name and make the button position dynamic

                        for roomSelectionButton in roomSelectionButtons:
                            i = roomSelectionButtons.index(roomSelectionButton)
                            if roomSelectionButton.draw(self.screen):
                                group_id = i
                                server.send((str(client_id) + ":" + str(i)).encode())
                                roomSelection = True
                                turns += 1
                                self.screen.fill(BLACK)

                        if backButton.draw(self.screen):
                            roomSet = False
                        if closeButton.draw(self.screen):
                            running = False
                            server.close()
                            pygame.display.quit()
                            pygame.quit()
                            sys.exit()
                            break
                        pygame.display.update()

                    else:
                        # Display Game Mode Screen
                        pygame.time.wait(20)
                        self.screen.fill((253, 240, 213))
                        pygame.event.wait(10)
                        if pvpButton.draw(self.screen):
                            Game.gameMode = 1
                            print("Masuk mode 1")
                            gameModeSet = True
                            self.screen.fill(BLACK)
                        if pvcButton.draw(self.screen):
                            Game.gameMode = 2
                            print("Masuk mode 2")
                            gameModeSet = True
                            self.screen.fill(BLACK)
                        if onlineButton.draw(self.screen):
                            Game.gameMode = 3
                            print("Masuk mode 3")
                            gameModeSet = True
                        if backButton.draw(self.screen):
                            playScreen = False
                        if closeButton.draw(self.screen):
                            running = False
                            server.close()
                            pygame.display.quit()
                            pygame.quit()
                            sys.exit()
                            break
                        pygame.display.update()
                else:
                    # Display Home Page Screen
                    self.screen.fill((253, 240, 213))
                    if playButton.draw(self.screen):
                        playScreen = True
                        pygame.event.wait(10)
                    if quitButton.draw(self.screen):
                        running = False
                        server.close()
                        pygame.display.quit()
                        pygame.quit()
                        sys.exit()
                        break
                    pygame.display.update()


if __name__ == "__main__":
    game = Game(TILE_SIZE)
    game.init_pygame()

    game.run()

    pygame.display.quit()
    pygame.quit()
    Thread(target=send_msg, args=(server,)).join()
    Thread(target=recv_msg, args=(server,)).join()
    server.close()
    sys.exit()
