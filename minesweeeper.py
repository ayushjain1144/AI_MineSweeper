from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random

class Minesweeper(QWidget):

    def __init__(self, row, col):

        """Options for the game: name, row, column, number_mines"""
        self.OPTIONS = [
            ("8 X 8", 8, 8, 10),
            ("16 X 16", 16, 16, 40),
            ("30 X 16", 30, 16, 99),
            ("Custom", row, col, num_mines)

    ]

    def start_option(self, option):
        """Defines the start option from the Option list"""

        self.level_name, self.row, self.col, self.num_mines = self.OPTIONS[option]

        self.setWindowTitle(f"AI Minesweeper ----- {self.level_name}")
        self.mines.setText(f"{self.num_mines}")
        self.clear_map()
        self.init_map()
        self.reset_map()

    def init_map(self):


        for r in range(self.row):
            for c in range(self.col):
                box = Pos(r, c)
                self.grid.addWidget(box, r, c)

                box.clicked.connect(self.trigger_start)
                box.revealed.connect(self.on_reveal)
                box.expandable.connect(self.expand_reveal)

        QTimer.singleshot(0, lamda: self.resize(1, 1))

    def reset_map(self):
        """Resets everything to inital state"""

        self.reset_position()
        self.add_mines()
        self.reset_number()
        self.update_timer()

    def reset_position(self):
        """Clears the position of mines"""

        for r in range(self.row):
            for c in range(self.col):
                box = self.grid.itemAtPosition(r, c).widget()
                box.reset()

    def add_mines(self):

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
