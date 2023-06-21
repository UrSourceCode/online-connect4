class Board(object):
    # Matrix for store letter
    positions = []
    for x in range(7):
        positions.append([" " for y in range(6)])

    # Print board
    def showBoard(self):
        for y in range(6):
            print("|", end = '')
            for x in range(7):
                print("[" + self.positions[x][5 - y] + "]", end = '')
            print("|")
        print("| 1  2  3  4  5  6  7 |")

    # Drop letter to fill stack
    def dropLetter(self, insert, letter):
        for i in range(6):
            if self.positions[insert][i] == " ":
                self.positions[insert][i] = letter
                return

    # Check matrix stack
    def checkOpen(self, slot):
        if not 0 <= slot <= 6:
            return 0
        if self.positions[slot][5] == " ":
            return 1
        else:
            return 0

    # Getter and setter
    def getArray(self):
        new_array = []
        for x in range(7):
            new_array.append([" " for n in range(6)])

        for x in range(7):
            for y in range(6):
                new_array[x][y] = self.positions[x][y]

        return new_array

    def setArray(self, new_array):
        for x in range(7):
            for y in range(6):
                self.positions[x][y] = new_array[x][y]

    # Detect win condition (4 connect)
    def detectWin(self):
        # Vertical
        for x in range(7):
            for y in range(3):
                if self.positions[x][y] != " " and self.positions[x][y] == self.positions[x][y + 1] == self.positions[x][y + 2] == self.positions[x][y + 3]:
                    return self.positions[x][y]
        # Horizontal
        for x in range(4):
            for y in range(6):
                if self.positions[x][y] != " " and self.positions[x][y] == self.positions[x + 1][y] == self.positions[x + 2][y] == self.positions[x + 3][y]:
                    return self.positions[x][y]
        # Diagonal
        for x in range(4):
            for y in range(3):
                if self.positions[x][y] != " " and self.positions[x][y] == self.positions[x + 1][y + 1] == self.positions[x + 2][y + 2] == self.positions[x + 3][y + 3]:
                    return self.positions[x][y]

        for x in range(3, 7):
            for y in range(3):
                if self.positions[x][y] != " " and self.positions[x][y] == self.positions[x-1][y+1] == self.positions[x - 2][y + 2] == self.positions[x - 3][y + 3]:
                    return self.positions[x][y]
        return " "
