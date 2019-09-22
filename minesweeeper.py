from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random
import sys
import time

revealed = []

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

    def set_flag(self):
        """Sets flag on discovered mines"""

        self.revealed.emit(self)
        revealed.emit()
        self.clicked.emit()


    def left_click(self):
        """Emulates the functionality of left click in real Minesweeper"""

        self.revealed.emit(self)
        revealed.append(self)
        if self.number == 0:
            self.expandable.emit(self.row,  self.col)
        self.clicked.emit()


    def paintEvent(self, event):

        pane = QPainter(self)
        pane.setRenderHint(QPainter.Antialiasing)

        object = event.rect()

        #Conditions if the square is is_revealed

        if self.is_revealed:

            if self.is_mine:
                pane.drawPixmap(object, QPixmap("bomb.png"))

            elif self.number > 0:
                pen = QPen();
                pen.setColor("red")
                font = pane.font()
                font.setBold(True)
                pane.setFont(font)

                pane.drawText(rect, Qt.AlignHCenter | Qt.AlignVCenter, str(self.number))

        else:

            pane.fillRect(object, QBrush(Qt.lightGray))
            pen = QPen(Qt.gray)
            pen.setWidth(1)
            pane.setPen(pen)
            pane.drawRect(object)

            if self.is_mine:
                pane.setOpacity(0.3)
                pane.drawPixmap(object, QPixmap("bomb.png"))


class Minesweeper(QMainWindow):

    def __init__(self, row, col, num_mines):
        super().__init__()

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

        window = QWidget()
        layout = QHBoxLayout()

        self.mines = QLabel()
        self.mines.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.mines.setText(f"{self.num_mines}")
        self.clock.setText("000")
        font = self.mines.font()
        font.setPointSize(20)
        font.setWeight(65)
        self.mines.setFont(font)
        self.mines.setFont(font)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.button = QPushButton()
        self.button.setFixedSize(QSize(30, 30))
        self.button.setStyleSheet('QPushButton {background-color: #000000; color: red;}')
        self.button.setText('Start Game')

        #self.button.pressed.connect(self.button_pressed)

        self.mines_label = QLabel()
        self.mines_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mines_label.setText("Mines: ")

        self.timer_label = QLabel()
        self.timer_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mines_label.setText("Timer: ")

        layout.addWidget(self.mines_label)
        layout.addWidget(self.mines)
        layout.addWidget(self.button)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.clock)

        vert_layout = QVBoxLayout()
        vert_layout.addLayout(layout)

        self.grid = QGridLayout()
        self.grid.setSpacing(5)

        vert_layout.addLayout(self.grid)
        window.setLayout(vert_layout)
        self.setCentralWidget(window)

        self.init_map()
        self.reset_map()

        self.show()






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

                #box.clicked.connect(self.trigger_start)
                #box.revealed.connect(self.on_reveal)
                #box.expandable.connect(self.expand_reveal)

        #QTimer.singleshot(0, lambda: self.resize(1, 1))

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
                box.initialize()

    def add_mines(self):
        """Returns the positions of the mines as a list"""
        mine_locations = []

        while len(mine_locations) < self.num_mines:

            r, c = random.randint(0, self.row - 1), random.randint(0, self.col - 1)
            # Sanity check if we are not repeating the mines

            if (r, c) not in mine_locations:

                box = self.grid.itemAtPosition(r, c).widget()
                box.is_mine = True
                mine_locations.append((r, c))
        self.end_game_condition = (self.row * self.col) - (self.num_mines + 1)

        return mine_locations


    def calculate_number(self, x, y):
        """Returns mines surrounding the x, y tile"""

        sum = 0

        if x - 1 >= 0:
            sum = sum + self.grid.itemAtPosition(x - 1, y).widget().is_mine

            if y - 1 >= 0:
                sum = sum + self.grid.itemAtPosition(x - 1, y - 1).widget().is_mine

            if y + 1 < self.row:
                sum = sum + self.grid.itemAtPosition(x - 1, y + 1).widget().is_mine


        if x + 1 < self.col:
            sum = sum + self.grid.itemAtPosition(x + 1, y).widget().is_mine

            if y - 1 >= 0:
                sum = sum + self.grid.itemAtPosition(x + 1, y - 1).widget().is_mine

            if y + 1 < self.row:
                sum = sum + self.grid.itemAtPosition(x + 1, y + 1).widget().is_mine

        if y - 1 >= 0:

            sum = sum + self.grid.itemAtPosition(x, y - 1).widget().is_mine

        if y + 1 < self.row:

            sum = sum + self.grid.itemAtPosition(x, y + 1).widget().is_mine

        return sum



    def reset_adjacency(self):
        """Calculates adjacency of every tile and store it in Tile"""
        for r in range(self.row):
            for c in range(self.col):
                tile = self.grid.itemAtPosition(r, c).widget()
                tile.number = self.calculate_number(r, c)

    def update_timer(self):

        t = int(time.time())
        self.clock.setText(f"{t}")

    def return_surrounding(self, x, y):
        """Returns mines surrounding the x, y tile"""

        list = []

        if x - 1 >= 0:
            list.append(self.grid.itemAtPosition(x - 1, y).widget())

            if y - 1 >= 0:
                list.append(self.grid.itemAtPosition(x - 1, y - 1).widget())

            if y + 1 < self.row:
                list.append(self.grid.itemAtPosition(x - 1, y + 1).widget())


        if x + 1 < self.col:
            list.append(self.grid.itemAtPosition(x + 1, y).widget())

            if y - 1 >= 0:
                list.append(self.grid.itemAtPosition(x + 1, y - 1).widget())

            if y + 1 < self.row:
                list.append(self.grid.itemAtPosition(x + 1, y + 1).widget())

        if y - 1 >= 0:

            list.append(self.grid.itemAtPosition(x, y - 1).widget())

        if y + 1 < self.row:

            list.append(self.grid.itemAtPosition(x, y + 1).widget())

        return list



    def num_open_tiles(self):
        """Returns number of open spaces - used for tie-breaking"""

        open_tiles = 0
        for r in range(self.row):
            for c in range(self.col):
                tile = self.grid.itemAtPosition(r, c).widget()
                if tile.is_revealed:
                    open_tiles = open_tiles + tile.is_revealed
        return open_tiles

    def count_bombs(list):
        """Returns the number of Bombs in a list"""

        sum = 0
        for tile in list:
            sum = sum + tile.is_mine

        return count_bombs

    def info_closed(list):
        """Returns the number and list of closed tiles"""

        sum = 0
        list = []
        for tile in list:
            if not tile.is_revealed:
                sum = sum + 1
                list.append(tile)

        return sum, list

    def flag_definite_bomb(self):
        """Based on revealed digits, flags the definite mine positions"""

        for tile in revealed:

            #get position of the tile
            idx = self.grid.indexOf(tile)
            location = self.layout.getItemPosition(idx)
            row, col = location[:2]
            list = self.return_surrounding(row, col)

            num_surrounding_bombs = count_bombs(list)

            num_close_tiles, list_closed_tiles = info_closed(list)

            variability = tile.number - num_surrounding_bombs

            if variability == num_close_tiles:
                for tile_closed in list_closed_tiles:
                    tile_closed.set_flag()







    def heurestic_2(self):
        """Calculates heurestic for the present board condition"""
        """Heurestic is sum of digits in the present region"""

        num_mines = 0

        return num_mines


app = QApplication(sys.argv)
ex = Minesweeper(8, 8, 4)
sys.exit(app.exec_())
