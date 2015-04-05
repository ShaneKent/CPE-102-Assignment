# define occupancy value
EMPTY = 0
GATHERER = 1
GENERATOR = 2
RESOURCE = 3

class Grid:
   def __init__(self, width, height, occupancy_value):
      self.width = width
      self.height = height
      self.cells = []
   
      # initialize grid to all specified occupancy value
      for row in range(0, self.height):
         self.cells.append([])
         for col in range(0, self.width):
            self.cells[row].append(occupancy_value)

   def set_cell(self, point, value):
      self.cells[point.y][point.x] = value


   def get_cell(self, point):
      return self.cells[point.y][point.x]

