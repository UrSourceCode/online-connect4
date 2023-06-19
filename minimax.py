import random

# Board
global minimaxBoardArray
minimaxBoardArray = []
for i in range(7):
    minimaxBoardArray.append([" " for y in range(6)])

# Print board
def showBoard():
    for y in range(6):
        print("|", end = '')
        for x in range(7):
            print("[" + minimaxBoardArray[x][5 - y] + "]", end = '')
        print("|")
    print("| 1  2  3  4  5  6  7 |")

# Drop letter to fill stack
def dropLetter(insert, letter):
    for i in range(6):
        if minimaxBoardArray[insert][i] == " ":
            minimaxBoardArray[insert][i] = letter
            break

# Pick letter (when trying possibilities)
def pickLetter(insert):
    for i in range(6):
        if minimaxBoardArray[insert][5 - i] != " ":
            minimaxBoardArray[insert][5 - i] = " "
            break

# Check matrix stack
def checkOpen(slot):
    if not 0 <= slot <= 6:
        return 0
    if minimaxBoardArray[slot][5] == " ":
        return 1
    else:
        return 0

# Detect win condition (4 connect)
def detectWin():
    # Vertical
    for x in range(7):
        for y in range(3):
            if minimaxBoardArray[x][y] != " " and minimaxBoardArray[x][y] == minimaxBoardArray[x][y + 1] == minimaxBoardArray[x][y + 2] == minimaxBoardArray[x][y + 3]:
                return minimaxBoardArray[x][y]
    # Horizontal
    for x in range(4):
        for y in range(6):
            if minimaxBoardArray[x][y] != " " and minimaxBoardArray[x][y] == minimaxBoardArray[x + 1][y] == minimaxBoardArray[x + 2][y] == minimaxBoardArray[x + 3][y]:
                return minimaxBoardArray[x][y]
    # Diagonal
    for x in range(4):
        for y in range(3):
            if minimaxBoardArray[x][y] != " " and minimaxBoardArray[x][y] == minimaxBoardArray[x + 1][y + 1] == minimaxBoardArray[x + 2][y + 2] == minimaxBoardArray[x + 3][y + 3]:
                return minimaxBoardArray[x][y]

    for x in range(3, 7):
        for y in range(3):
            if minimaxBoardArray[x][y] != " " and minimaxBoardArray[x][y] == minimaxBoardArray[x - 1][y + 1] == minimaxBoardArray[x - 2][y + 2] == minimaxBoardArray[x - 3][y + 3]:
                return minimaxBoardArray[x][y]
    return " "

# Set up board, create possibilities, and choose best way choice
def minimaxChoice(inputArray, depth, letter):  
    print("Calculating %d possibilities" % (2 ** depth))
    global minimaxBoardArray
    minimaxBoardArray = inputArray
    choices = ["null", "null", "null", "null", "null", "null", "null"]  
    if letter == "O":  
        humanLetter = "X"
    else:
        humanLetter = "O"

    for x in range(7):  
        if checkOpen(x) == 1:
            choices[x] = minimaxLoop(x, letter, humanLetter, depth)
    print("Computer completed")

    # Best choice
    best = 0 
    for i in range(7):
        if choices[i] != "null" and (choices[i] == letter or (choices[best] == humanLetter and choices[i] == " ")):
            best = i

    if choices[best] == "null":  
        for i in range(7):
            if choices[i] == " ":
                best = i
                break

    humanizer = [] 
    for i in range(7):
        if choices[i] == choices[best]:
            humanizer.append(i)
    return humanizer[int(random.triangular(0, len(humanizer)))]

def minimaxLoop(drop_slot, letter, humanLetter, depth):
    # Try to insert letter to stack
    dropLetter(drop_slot, letter)  

    if detectWin() != " ": 
        returnable = detectWin()
        # If win condition, ignore the last letter
        pickLetter(drop_slot) 
        return returnable
    else:  
        # Last step
        if depth == 1:  
            pickLetter(drop_slot)
            return " "
        # If not last step, search other layer
        else: 
            h = letter
            letter = humanLetter
            humanLetter = h
            choices = [" ", " ", " ", " ", " ", " ", " "]
            for x in range(7):
                if checkOpen(x) == 1:
                    choices[x] = minimaxLoop(x, letter, humanLetter, depth-1) 
                else:
                    choices[x] = " " 

            for i in range(7):
                if choices[i] == letter: 
                    pickLetter(drop_slot)
                    return letter

            for i in range(7):
                if choices[i] == " ": 
                    pickLetter(drop_slot)
                    return " "

            pickLetter(drop_slot)
            return humanLetter 
