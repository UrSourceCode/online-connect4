from board import Board
import minimax

# Game mode
gameMode = int(
    input("Choose game mode\n1. Player vs Player\n2. Player vs Computer\n"))
if (gameMode == 2):
    turnMessage = "Computer turn"
else:
    turnMessage = "Player 2 turn"

# Human turn
def humanChoice(board):
    # Pick slot/column
    while True:
        slot = int(input("Pick a slot\n")) - 1
        if slot < 0 or slot > 6:
            print("Please pick from 1 to 7")
        elif board.checkOpen(slot) == 0:
            print("Slot is full, choose a different slot")
        else:
            print(board.checkOpen(slot))
            return slot

# Controller for the turn
def choice(player, board, depth, letter):
    if player == 1 or gameMode == 1:
        return humanChoice(board)
    else:
        boardArray = board.getArray()
        output = minimax.minimaxChoice(boardArray, depth, letter)
        print("%s Pick slot %d" % (letter, output + 1))
        return output

# Start game
gameBoard = Board() 
turns = 0
depth = 6
while turns < 50:
    gameBoard.showBoard()
    print("Player 1 turn")
    gameBoard.dropLetter(choice(1, gameBoard, depth, "X"), "X")
    if gameBoard.detectWin() != " ":
        break
    turns += 1
    gameBoard.showBoard()
    print(turnMessage)
    gameBoard.dropLetter(choice(2, gameBoard, depth, "O"), "O")
    if gameBoard.detectWin() != " ":
        break
    turns += 1

# End game condition
gameBoard.showBoard()
if turns == 50:
    print("Draw!\n")
else:
    if gameBoard.detectWin() == "X":
        print("Player 1 Win!\n")
    elif gameMode == 1:
        print("Player 2 Win!\n")
    else:
        print("Computer Win!\n")