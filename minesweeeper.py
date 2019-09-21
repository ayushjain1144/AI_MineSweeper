from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random

class Tile(QWidget):

    expandable = pyqtSignal(int, int)
    revealed = pyqtSignal(object)
    clicked = pyqtSignal()

    def __init__(self, x , y):

        super().__init__()


        self.setFixedSize(QSize(25, 25))
        self.x = x
        self.y = y
        self.initialize()

    def initialize(self):
        """Contains the states of the mines"""

        self.is_mine = False
        self.number = 0
        self.is_revealed = False
        self.is_flagged = False

        self.update()

class Minesweeper(QWidget):

    def __init__(self, row, col, num_mines):

        """Options for the game: name, row, column, number_mines"""
        self.OPTIONS = [
            ("8 X 8", 8, 8, 10),
            ("16 X 16", 16, 16, 40),
            ("30 X 16", 30, 16, 99),
            ("Custom", row, col, num_mines)
            ]
        self.row = row
        self.col = col
        self.num_mines = num_mines

    def start_option(self, option):
        """Defines the start option from the Option list"""

        self.level_name, self.row, self.col, self.num_mines = self.OPTIONS[option]

        self.setWindowTitle(f"AI Minesweeper ----- {self.level_name}")
        self.mines.setText(f"{self.num_mines}")
        self.clear_map()
        self.init_map()
        self.reset_map()

    def init_map(self):
        """Added boxes on GUI"""

        for r in range(self.row):
            for c in range(self.col):
                box = Tile(r, c)
                self.grid.addWidget(box, r, c)

                box.clicked.connect(self.trigger_start)
                box.revealed.connect(self.on_reveal)
                box.expandable.connect(self.expand_reveal)

        QTimer.singleshot(0, lamda: self.resize(1, 1))

    def reset_map(self):
        """Resets everything to inital state"""

        self.reset_position()
        self.add_mines()
        self.reset_adjacency()
        self.update_timer()

    def reset_position(self):
        """Clears the position of mines"""

        for r in range(self.row):
            for c in range(self.col):
                box = self.grid.itemAtPosition(r, c).widget()
                box.reset()

    def add_mines(self):
        """Returns the positions of the mines as a list"""
        mine_locations = []

        while len(mine_locations) < self.num_mines:

            r, c = random.randint(0, self.row - 1), random.randint(0, self.col - 1)
            # Sanity check if we are not repeating the mines

            if (r, c) not in mine_locations:

                box = self.grid.itemAtPosition(r, c).widget()
                w.is_mine = True
                mine_locations.append((r, c))
        self.end_game_condition = (self.row * self.col) - (self.num_mines + 1)

        return mine_locations


    def calculate_number(self, x, y):
        """Returns mines surrounding the x, y tile"""

        sum = 0

        if x - 1 >= 0:
            sum = sum + self.grid.itemAtPosition(x - 1, y).is_mine

            if y - 1 >= 0:
                sum = sum + self.grid.itemAtPosition(x - 1, y - 1).is_mine

            if y + 1 < self.row:
                sum = sum + self.grid.itemAtPosition(x - 1, y + 1).is_mine


        if x + 1 < self.col:
            sum = sum + self.grid.itemAtPosition(x + 1, y).is_mine

            if y - 1 >= 0:
                sum = sum + self.grid.itemAtPosition(x + 1, y - 1).is_mine

            if y + 1 < self.row:
                sum = sum + self.grid.itemAtPosition(x + 1, y + 1).is_mine

        if y - 1 >= 0:

            sum = sum + self.grid.itemAtPosition(x, y - 1).is_mine

        if y + 1 < self.row:

            sum = sum + self.grid.itemAtPosition(x, y + 1).is_mine

        return sum

    def reset_adjacency(self):
    """Calculates adjacency of every tile and store it in Tile"""

        for r in range(self.row):
            for c in range(self.col):
                tile = self.grid.itemAtPosition(r, c).widget()
                tile.number = self.calculate_number(r, c)

    def left_click(self):
    """Emulates the functionality of left click in real Minesweeper"""

        self.revealed.emit(self)
        if self.number == 0:
            self.expandable.emit(self.x  self.y)
        self.clicked.emit()


    def paintEvent(self, event):

        pane = QPainter(self)
        pane.setRenderHint(QPainter.Antialiasing)

        tile = event.rect()
