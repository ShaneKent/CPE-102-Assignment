class Point:
   def __init__(self, x, y):
      self.x = x
      self.y = y

   def distance_sq(self, p2):
      return (self.x - p2.x)**2 + (self.y - p2.y)**2
      
   def adjacent(self, pt2):
      return ((self.x == pt2.x and abs(self.y - pt2.y) == 1) or 
         (self.y == pt2.y and abs(self.x - pt2.x) == 1))

def sign(x):
   if x < 0:
      return -1
   elif x > 0:
      return 1
   else:
      return 0