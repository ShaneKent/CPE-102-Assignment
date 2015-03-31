class OrderedList:
   def __init__(self):
      self.list = []


   def insert(self, item, ord):
      size = len(self.list)
      idx = 0
      while (idx < size and self.list[idx].ord < ord):
         idx += 1

      self.list[idx:idx] = [ListItem(item, ord)]


   def remove(self, item):
      size = len(self.list)
      idx = 0
      while (idx < size and self.list[idx].item != item):
         idx += 1

      if idx < size:
         self.list[idx:idx+1] = []


   def head(self):
      return self.list[0] if self.list else None


   def pop(self):
      if self.list:
         return self.list.pop(0)


class ListItem:
   def __init__(self, item, ord):
      self.item = item
      self.ord = ord


   def __eq__(a, b):
      return a.item == b.item and a.ord == b.ord



