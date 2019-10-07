# AI_MineSweeper

# Problem Statement
Consider the following minesweeper problem. A rectangular grid of
squares is a war field with a number of mines which may explode if clicked. The mines are
not visible to the intelligent agent walking over the area. The agent has a radar based device which
detects the number of mines in the vicinity of the square. A square has maximum 8 neighbors in its
horizontal, vertical and diagonal directions which may contain one or more mines.

The agent is said to be in a state represented by a n-valued tuple. The mines are not dynamic and remain at the same place throughout the search in a run. Once clicked in a square that does not have any mine, the neighboring safe area opens up with the boundary squares. The open area does not have any mine in it. The area that opens up as safe zone is a convex region
bounded by the nearest mines in horizontal and vertical directions. The area is not convex if it has a bend. Each move refers to a click at any one remaining square outside the open area followed by further expansion of the open area. A wrong click at hidden mine may cause an explosion, therefore, the walking agent has to take intelligent decisions based on the number of mines obtained for squares at the border of the open area.

# ALgorithm Used

I designed two heurestic functions which calculate the worth of the next possible moves and used hill climbing approach to decide upon the next steps.

# Run

python minesweeper.py

# Dependencies

- Python3.7
- PyQt5
