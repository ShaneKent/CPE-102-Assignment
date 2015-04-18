import point
import actions

class Entity:
   def __init__(self, name, imgs):
      self.name = name
      self.imgs = imgs
      self.current_img = 0

   def get_name(self):
      return self.name

   def get_images(self):
      return self.imgs

   def get_image(self):
      return self.imgs[self.current_img]

   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def entity_string(self):
      return 'unknown'


/////////

class GridItem(Entity):
   def __init__(self, name, imgs, position):
      super(GridItem, self).__init__(name, imgs)
      self.position = position

   def set_position(self, point):
      self.position = point

   def get_position(self):
      return self.position

/////////

class Occupant(GridItem):
   def __init__(self, name, imgs, position):
      super(Occupant, self).__init__(name, imgs, position)
      self.pending_actions = []
    
   def remove_pending_action(self, action):
      if hasattr(self, "pending_actions"):
         self.pending_actions.remove(action)

   def add_pending_action(self, action):
      if hasattr(self, "pending_actions"):
         self.pending_actions.append(action)

   def get_pending_actions(self):
      if hasattr(self, "pending_actions"):
         return self.pending_actions
      else:
         return []

   def clear_pending_actions(self):
      if hasattr(self, "pending_actions"):
         self.pending_actions = []


///////////////

class Miner(Occupant):
   def __init__(self, name, imgs, position, rate, resource_limit, animation_rate):
      super(Miner, self).__init__(name, imgs, position)
      self.rate = rate
      self.resource_limit = resource_limit
      self.animation_rate = animation_rate
      self.resource_count = 0
      
   def get_rate(self):
      return self.rate
      
   def set_resource_count(self, n):
      self.resource_count = n

   def get_resource_count(self):
      return self.resource_count
 
   def get_resource_limit(self):
      return self.resource_limit
      
   def get_animation_rate(self):
      return self.animation_rate



///////////////


class Background(Entity):
   def __init__(self, name, imgs):
      super(Background, self).__init__(name, imgs)
   
////////


class MinerNotFull(Miner):
   def __init__(self, name, resource_limit, position, rate, imgs,
      animation_rate):
      super(MinerNotFull, self).__init__(name, imgs, position, rate, resource_limit, animation_rate)
      
   def entity_string(self):
      return ' '.join(['miner', self.name, str(self.position.x),
         str(self.position.y), str(self.resource_limit),
         str(self.rate), str(self.animation_rate)])
         
   def miner_to_ore(self, world, ore):
      entity_pt = self.get_position()
      if not ore:
         return ([entity_pt], False)
      ore_pt = ore.get_position()
      if entity_pt.adjacent(ore_pt):
         self.set_resource_count(1 + self.get_resource_count())
         actions.remove_entity(world, ore)
         return ([ore_pt], True)
      else:
         new_pt = world.next_position(entity_pt, ore_pt)
         return (world.move_entity(self, new_pt), False)
                  
   def create_miner_action(self, world, i_store):
      def action(current_ticks):
         self.remove_pending_action(action)

         entity_pt = self.get_position()
         ore = world.find_nearest(entity_pt, Ore)
         (tiles, found) = self.miner_to_ore(world, ore)

         new_entity = self
         if found:
            new_entity = actions.try_transform_miner(world, self,
               self.try_transform_miner)

         actions.schedule_action(world, new_entity,
            new_entity.create_miner_action(world, i_store),
            current_ticks + new_entity.get_rate())
         return tiles
      return action


   def try_transform_miner(self, world):
      if self.resource_count < self.resource_limit:
         return self
      else:
         new_entity = MinerFull(
            self.get_name(), self.get_resource_limit(),
            self.get_position(), self.get_rate(),
            self.get_images(), self.get_animation_rate())
         return new_entity
      
   def schedule_miner(self, world, ticks, i_store):
      actions.schedule_action(world, self, self.create_miner_action(world, i_store),
         ticks + self.get_rate())
      actions.schedule_animation(world, self)

/////////
   
class MinerFull(Miner):
   def __init__(self, name, resource_limit, position, rate, imgs,
      animation_rate):
      super(MinerFull, self).__init__(name, imgs, position, rate, resource_limit, animation_rate)
      self.resource_count = resource_limit

   def create_miner_action(self, world, i_store):
      def action(current_ticks):
         self.remove_pending_action(action)

         entity_pt = self.get_position()
         smith = world.find_nearest(entity_pt, Blacksmith)
         (tiles, found) = self.miner_to_smith(world, smith)

         new_entity = self
         if found:
            new_entity = actions.try_transform_miner(world, self,
               self.try_transform_miner)

         actions.schedule_action(world, new_entity,
            new_entity.create_miner_action(world, i_store),
            current_ticks + new_entity.get_rate())
         return tiles
      return action

   def miner_to_smith(self, world, smith):
      entity_pt = self.get_position()
      if not smith:
         return ([entity_pt], False)
      smith_pt = smith.get_position()
      if entity_pt.adjacent(smith_pt):
         smith.set_resource_count(smith.get_resource_count() + self.get_resource_count())
         self.set_resource_count(0)
         return ([], True)
      else:
         new_pt = world.next_position(entity_pt, smith_pt)
         return (world.move_entity(self, new_pt), False)
            
   def try_transform_miner(self, world):
      new_entity = MinerNotFull(
         self.get_name(), self.get_resource_limit(),
         self.get_position(), self.get_rate(),
         self.get_images(), self.get_animation_rate())

      return new_entity

///////////

      
class Vein(Occupant):
   def __init__(self, name, rate, position, imgs, resource_distance=1):
      super(Vein, self).__init__(name, imgs, position)
      self.rate = rate
      self.resource_distance = resource_distance

   def get_rate(self):
      return self.rate
      
   def get_resource_distance(self):
      return self.resource_distance

   def entity_string(self):
      return ' '.join(['vein', self.name, str(self.position.x),
         str(self.position.y), str(self.rate),
         str(self.resource_distance)])
         
   def create_vein_action(self, world, i_store):
      def action(current_ticks):
         self.remove_pending_action(action)

         open_pt = world.find_open_around(self.get_position(), self.get_resource_distance())
         if open_pt:
            ore = actions.create_ore(world,
               "ore - " + self.get_name() + " - " + str(current_ticks),
               open_pt, current_ticks, i_store)
            world.add_entity(ore)
            tiles = [open_pt]
         else:
            tiles = []

         actions.schedule_action(world, self,
            self.create_vein_action(world, i_store),
            current_ticks + self.get_rate())
         return tiles
      return action

   def schedule_vein(self, world, ticks, i_store):
      actions.schedule_action(world, self, self.create_vein_action(world, i_store),
         ticks + self.get_rate())
 
/////////////
  
class Ore(Occupant):
   def __init__(self, name, position, imgs, rate=5000):
      super(Ore, self).__init__(name, imgs, position)
      self.rate = rate
      
   def get_rate(self):
      return self.rate
   
   def entity_string(self):
      return ' '.join(['ore', self.name, str(self.position.x),
         str(self.position.y), str(self.rate)])
         
   def create_ore_transform_action(self, world, i_store):
      def action(current_ticks):
         self.remove_pending_action(action)
         blob = actions.create_blob(world, self.get_name() + " -- blob",
            self.get_position(),
            self.get_rate() // actions.BLOB_RATE_SCALE,
            current_ticks, i_store)

         actions.remove_entity(world, self)
         world.add_entity(blob)

         return [blob.get_position()]
      return action
      
   def schedule_ore(self, world, ticks, i_store):
      actions.schedule_action(world, self,
         self.create_ore_transform_action(world, i_store),
         ticks + self.get_rate())

///////////


class Blacksmith(Occupant):
   def __init__(self, name, position, imgs, resource_limit, rate,
      resource_distance=1):
      super(Blacksmith, self).__init__(name, imgs, position)
      self.resource_limit = resource_limit
      self.resource_count = 0
      self.rate = rate
      self.resource_distance = resource_distance
      
   def get_rate(self):
      return self.rate
      
   def set_resource_count(self, n):
      self.resource_count = n
   
   def get_resource_count(self):
      return self.resource_count
      
   def get_resource_limit(self):
      return self.resource_limit
      
   def get_resource_distance(self):
      return self.resource_distance

   def entity_string(self):
      return ' '.join(['blacksmith', self.name, str(self.position.x),
         str(self.position.y), str(self.resource_limit),
         str(self.rate), str(self.resource_distance)])


///////////////


class Obstacle(GridItem):
   def __init__(self, name, position, imgs):
      super(Obstacle, self).__init__(name, imgs, position)

   def entity_string(self):
      return ' '.join(['obstacle', self.name, str(self.position.x),
         str(self.position.y)])
         
////////////////



class OreBlob(Occupant):
   def __init__(self, name, position, rate, imgs, animation_rate):
      super(OreBlob, self).__init__(name, imgs, position)
      self.rate = rate
      self.animation_rate = animation_rate
      
   def get_rate(self):
      return self.rate
      
   def get_animation_rate(self):
      return self.animation_rate
      
   def blob_to_vein(self, world, vein):
      entity_pt = self.get_position()
      if not vein:
         return ([entity_pt], False)
      vein_pt = vein.get_position()
      if entity_pt.adjacent(vein_pt):
         actions.remove_entity(world, vein)
         return ([vein_pt], True)
      else:
         new_pt = world.blob_next_position(entity_pt, vein_pt)
         old_entity = world.get_tile_occupant(new_pt)
         if isinstance(old_entity, Ore):
            actions.remove_entity(world, old_entity)
         return (world.move_entity(self, new_pt), False)


   def create_ore_blob_action(self, world, i_store):
      def action(current_ticks):
         self.remove_pending_action(action)

         entity_pt = self.get_position()
         vein = world.find_nearest(entity_pt, Vein)
         (tiles, found) = self.blob_to_vein(world, vein)

         next_time = current_ticks + self.get_rate()
         if found:
            quake = actions.create_quake(world, tiles[0], current_ticks, i_store)
            world.add_entity(quake)
            next_time = current_ticks + self.get_rate() * 2

         actions.schedule_action(world, self,
            self.create_ore_blob_action(world, i_store),
            next_time)

         return tiles
      return action

   def schedule_blob(self, world, ticks, i_store):
      actions.schedule_action(world, self, self.create_ore_blob_action(world, i_store),
         ticks + self.get_rate())
      actions.schedule_animation(world, self)
      

/////////////////

class Quake(Occupant):
   def __init__(self, name, position, imgs, animation_rate):
      super(Quake, self).__init__(name, imgs, position)
      self.animation_rate = animation_rate
      
   def get_animation_rate(self):
      return self.animation_rate

   def create_death_action(self, world):
      def action(current_ticks):
         self.remove_pending_action(action)
         pt = self.get_position()
         actions.remove_entity(world, self)
         return [pt]
      return action
   
   def schedule_quake(self, world, ticks):
      actions.schedule_animation(world, self, actions.QUAKE_STEPS) 
      actions.schedule_action(world, self, self.create_death_action(world),
         ticks + actions.QUAKE_DURATION)

