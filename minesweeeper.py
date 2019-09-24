from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random
import sys
import time



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
        self.is_clicked = False

        self.update()

    def set_flag(self):
        """Sets flag on discovered mines"""

        self.is_flagged = True
        self.reveal()



    def reveal(self):
        """Reveal the tile"""

        self.is_revealed = True
        self.update()
        self.revealed.emit(self)

    def undo_reveal(self):
        """Undo Reveal of tile"""

        self.is_revealed = False
        self.update()
        self.revealed.emit(self)


    def left_click(self):
        """Emulates the functionality of left click in real Minesweeper"""

        self.revealed.emit(self)

        if self.number == 0:
            self.expandable.emit(self.row,  self.col)
        self.clicked.emit()


    def paintEvent(self, event):

        pane = QPainter(self)
        pane.setRenderHint(QPainter.Antialiasing)

        object = event.rect()

        #Conditions if the square is is_revealed

        if self.is_revealed:

            if not self.is_clicked:
                pane.fillRect(object, QBrush(Qt.green))
                pen = QPen(Qt.green)
            else:
                pane.fillRect(object, QBrush(Qt.blue))
                pen = QPen(Qt.blue)
            pen.setWidth(1)
            pane.setPen(pen)
            pane.drawRect(object)

            if self.is_mine and not self.is_flagged:
                pane.drawPixmap(object, QPixmap("bomb.png"))

            elif self.is_flagged:
                pane.drawPixmap(object, QPixmap("flag.png"))
                pane.setOpacity(0.3)
                pane.drawPixmap(object, QPixmap("bomb.png"))

            elif self.number > 0:

                pen = QPen(Qt.red)
                pane.setPen(pen)
                font = pane.font()
                font.setBold(True)
                pane.setFont(font)

                pane.drawText(object, Qt.AlignHCenter | Qt.AlignVCenter, str(self.number))

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


        self.row = row
        self.col = col
        self.num_mines = num_mines
        self.is_started = False

        self.setWindowTitle(f"AI Minesweeper : {self.row} X {self.col}")

        window = QWidget()
        layout = QHBoxLayout()

        self.mines = QLabel()
        self.mines.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.next_button = QPushButton()
        self.next_button.setFixedSize(QSize(50, 50))
        self.next_button.setStyleSheet('QPushButton {background-color: #000000; color: red;}')
        self.next_button.setText('Next')

        self.next_button.pressed.connect(self.take_step)

        self.mines.setText(f"{self.num_mines}")

        font = self.mines.font()
        font.setPointSize(20)
        font.setWeight(65)
        self.mines.setFont(font)
        self.mines.setFont(font)



        self.button = QPushButton()
        self.button.setFixedSize(QSize(50, 50))
        self.button.setStyleSheet('QPushButton {background-color: #000000; color: red;}')
        self.button.setText('Start')

        self.button.pressed.connect(self.start_option)

        self.mines_label = QLabel()
        self.mines_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mines_label.setText("Mines: ")



        layout.addWidget(self.mines_label)
        layout.addWidget(self.mines)
        layout.addWidget(self.button)
        layout.addWidget(self.next_button)


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






    def start_option(self):
        """Changes Flag"""

        if self.is_started == False:
            self.is_started = True
            print("Your Game has Started")

            r, c = random.randint(0, self.row - 1), random.randint(0, self.col - 1)

            self.grid.itemAtPosition(r, c).widget().is_clicked = True
            list = self.open_area(r, c)


            for w in list:

                w.reveal()



    def take_step(self):
        """Executes a move"""

        print("Flagging the sure mines in this state")
        self.flag_definite_bomb()


        print("Computing for Next Best Move")

        tile_heurestic_list = []
        list_states = self.get_next_step_list()

        for tile_coords in list_states:
            tile = self.grid.itemAtPosition(tile_coords[0], tile_coords[1]).widget()
            list = self.nextState(tile_coords)
            h_value = self.heurestic()
            h_value_tie_break = self.num_open_tiles()
            tile_heurestic_list.append((tile_coords, h_value, h_value_tie_break))

            print(f"The heurestic value for tile at {tile_coords} is {h_value}")

            for w in list:
                w.undo_reveal()

        self.hill_climbing(tile_heurestic_list)




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
                print(tile.number)


    def return_surrounding(self, x, y):
        """Returns mines surrounding the x, y tile"""

        list = []

        if x - 1 >= 0:
            list.append((x - 1, y))

            if y - 1 >= 0:
                list.append((x - 1, y - 1))

            if y + 1 < self.row:
                list.append((x - 1, y + 1))


        if x + 1 < self.col:
            list.append((x + 1, y))

            if y - 1 >= 0:
                list.append((x + 1, y - 1))

            if y + 1 < self.row:
                list.append((x + 1, y + 1))

        if y - 1 >= 0:

            list.append((x, y - 1))

        if y + 1 < self.row:

            list.append((x, y + 1))

        return list



    def num_open_tiles(self):
        """Returns number of open spaces - used for tie-breaking"""

        open_tiles = 0
        for r in range(self.row):
            for c in range(self.col):
                tile = self.grid.itemAtPosition(r, c).widget()
                if tile.is_revealed or tile.is_flagged:
                    open_tiles = open_tiles + 1
        return open_tiles

    def count_bombs(self, list):
        """Returns the number of Bombs in a list"""

        sum = 0
        for t in list:

            tile = self.grid.itemAtPosition(t[0], t[1]).widget()
            if tile.is_flagged:
                sum = sum + 1

        return sum

    def info_closed(self, list):
        """Returns the number and list of closed tiles"""

        sum = 0
        closed_list = []
        for t in list:

            tile = self.grid.itemAtPosition(t[0], t[1]).widget()
            if (not tile.is_revealed) and (not tile.is_flagged):
                sum = sum + 1
                closed_list.append(tile)

        return sum, closed_list

    def get_revealed_tiles(self):
        """Returns the revealed tiles list"""

        list = []
        for r in range(self.row):
            for c in range(self.col):
                tile = self.grid.itemAtPosition(r, c).widget()
                if tile.is_revealed:
                    list.append(tile)
        return list

    def flag_definite_bomb(self):
        """Based on revealed digits, flag the definite mine positions"""

        count = 0
        revealed = self.get_revealed_tiles()
        for tile in revealed:

            #get position of the tile
            if tile.number > 0:
                idx = self.grid.indexOf(tile)
                location = self.grid.getItemPosition(idx)
                row, col = location[:2]

                list = self.return_surrounding(row, col)

                num_surrounding_bombs = self.count_bombs(list)

                num_close_tiles, list_closed_tiles = self.info_closed(list)

                variability = tile.number - num_surrounding_bombs
                print(f"{variability}, {tile.number}, {num_close_tiles}, {row}, {col}")

                if variability == num_close_tiles:
                    for tile in list_closed_tiles:
                        print(f"{row}, {col}")
                        tile.set_flag()

        return count

    def heurestic(self):
        """Based on revealed digits, count the definite mine positions"""

        count = 0
        revealed = self.get_revealed_tiles()
        for tile in revealed:

            #get position of the tile
            idx = self.grid.indexOf(tile)
            location = self.grid.getItemPosition(idx)
            row, col = location[:2]
            list = self.return_surrounding(row, col)

            num_surrounding_bombs = self.count_bombs(list)

            num_close_tiles, list_closed_tiles = self.info_closed(list)

            variability = tile.number - num_surrounding_bombs

            if variability == num_close_tiles:
                count = count + len(list_closed_tiles)

        return count

    def get_next_step_list(self):
        """Returns possible steps it can take"""

        list = []

        for r in range(self.row):
            for c in range(self.col):
                tile = self.grid.itemAtPosition(r, c).widget()
                if not tile.is_revealed:
                    list.append((r, c))

        return list



    def open_area(self, x, y):
        """Opens the area when clicked on a tile"""

        open_queue =  [(x, y)]
        reveal_queue = []
        flag = True

        while flag:
            flag = False
            list = open_queue
            open_queue = []

            for x, y in list:
                positions = self.return_surrounding(x, y)
                for w1 in positions:
                    w = self.grid.itemAtPosition(w1[0], w1[1]).widget()

                    if not w.is_mine and w not in reveal_queue:
                        reveal_queue.append(w)
                        if w.number == 0:
                            open_queue.append((w.x, w.y))
                            flag = True
        return reveal_queue



    def nextState(self, tile_coords):
        """Generates next state"""
        #tile is the tile we would click

        r = tile_coords[0]
        c = tile_coords[1]

        initial_open = self.get_revealed_tiles()
        new_open_list = self.open_area(r, c)

        new_change_list = list(set(new_open_list) - set(initial_open))

        for w in new_change_list:

            w.reveal()

        return new_change_list


    def heurestic_2(self):
        """Calculates heurestic for the present board condition by summing the numbers on the tile"""

        sum = 0
        for r in range(self.row):
            for c in range(self.col):
                tile = self.grid.itemAtPosition(r, c).widget()
                if tile.is_revealed:
                    sum = sum + tile.number
        return sum

    def hill_climbing(self, list):
        """Takes the forward step, depending on list of heuristic and tile locations"""

        best_child_list = []
        #print(list)
        if len(list) == 0:
            print("Game Over")
            return
        best_hvalue = max(list, key=lambda i: i[1])[1]
        for item in list:
            if item[1] == best_hvalue:
                best_child_list.append(item)

        if len(best_child_list) != 1:

            print("Breaking the equal heurestic case")
            best_tie_break = max(best_child_list, key=lambda i: i[2])

            print(f"The maximum value for tie break is for {best_tie_break[0]} with tie-break value {best_tie_break[2]}")
            print("Opening the tile")
            r = best_tie_break[0][0]
            c = best_tie_break[0][1]
            self.grid.itemAtPosition(r, c).widget().is_clicked = True
            self.nextState(best_tie_break[0])
        else:
            r = ((best_child_list[0])[0])[0]
            c = ((best_child_list[0])[0])[1]
            self.grid.itemAtPosition(r, c).widget().is_clicked = True
            self.nextState((best_child_list[0])[0])



app = QApplication(sys.argv)
ex = Minesweeper(15, 15, 20)
sys.exit(app.exec_())
