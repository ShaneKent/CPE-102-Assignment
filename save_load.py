import actions
import entities
import image_store
import point
import worldmodel

PROPERTY_KEY = 0

BGND_KEY = 'background'
BGND_NUM_PROPERTIES = 4
BGND_NAME = 1
BGND_COL = 2
BGND_ROW = 3

MINER_KEY = 'miner'
MINER_NUM_PROPERTIES = 7
MINER_NAME = 1
MINER_LIMIT = 4
MINER_COL = 2
MINER_ROW = 3
MINER_RATE = 5
MINER_ANIMATION_RATE = 6

OBSTACLE_KEY = 'obstacle'
OBSTACLE_NUM_PROPERTIES = 4
OBSTACLE_NAME = 1
OBSTACLE_COL = 2
OBSTACLE_ROW = 3

ORE_KEY = 'ore'
ORE_NUM_PROPERTIES = 5
ORE_NAME = 1
ORE_COL = 2
ORE_ROW = 3
ORE_RATE = 4

SMITH_KEY = 'blacksmith'
SMITH_NUM_PROPERTIES = 7
SMITH_NAME = 1
SMITH_COL = 2
SMITH_ROW = 3
SMITH_LIMIT = 4
SMITH_RATE = 5
SMITH_REACH = 6

VEIN_KEY = 'vein'
VEIN_NUM_PROPERTIES = 6
VEIN_NAME = 1
VEIN_RATE = 4
VEIN_COL = 2
VEIN_ROW = 3
VEIN_REACH = 5


def save_world(world, file):
   save_entities(world, file)
   save_background(world, file)

def save_entities(world, file):
   for entity in world.get_entities():
      file.write(entity.entity_string() + '\n')


def save_background(world, file):
   for row in range(0, world.num_rows):
      for col in range(0, world.num_cols):
         file.write('background ' +
            entities.get_name(
               world.get_background(point.Point(col, row))) +
            ' ' + str(col) + ' ' + str(row) + '\n')


def load_world(world, images, file, run=False):
   for line in file:
      properties = line.split()
      if properties:
         if properties[PROPERTY_KEY] == BGND_KEY:
            add_background(world, properties, images)
         else:
            add_entity(world, properties, images, run)


def add_background(world, properties, i_store):
   if len(properties) >= BGND_NUM_PROPERTIES:
      pt = point.Point(int(properties[BGND_COL]), int(properties[BGND_ROW]))
      name = properties[BGND_NAME]
      world.set_background(pt,
         entities.Background(name, image_store.get_images(i_store, name)))


def add_entity(world, properties, i_store, run):
   new_entity = create_from_properties(properties, i_store)
   if new_entity:
      world.add_entity(new_entity)
      if run:
         schedule_entity(world, new_entity, i_store)


def create_from_properties(properties, i_store):
   key = properties[PROPERTY_KEY]
   if properties:
      if key == MINER_KEY:
         return create_miner(properties, i_store)
      elif key == VEIN_KEY:
         return create_vein(properties, i_store)
      elif key == ORE_KEY:
         return create_ore(properties, i_store)
      elif key == SMITH_KEY:
         return create_blacksmith(properties, i_store)
      elif key == OBSTACLE_KEY:
         return create_obstacle(properties, i_store)
   return None


def create_miner(properties, i_store):
   if len(properties) == MINER_NUM_PROPERTIES:
      miner = entities.MinerNotFull(properties[MINER_NAME],
         int(properties[MINER_LIMIT]),
         point.Point(int(properties[MINER_COL]), int(properties[MINER_ROW])),
         int(properties[MINER_RATE]),
         image_store.get_images(i_store, properties[PROPERTY_KEY]),
         int(properties[MINER_ANIMATION_RATE]))
      return miner
   else:
      return None


def create_vein(properties, i_store):
   if len(properties) == VEIN_NUM_PROPERTIES:
      vein = entities.Vein(properties[VEIN_NAME], int(properties[VEIN_RATE]),
         point.Point(int(properties[VEIN_COL]), int(properties[VEIN_ROW])),
         image_store.get_images(i_store, properties[PROPERTY_KEY]),
         int(properties[VEIN_REACH]))
      return vein
   else:
      return None


def create_ore(properties, i_store):
   if len(properties) == ORE_NUM_PROPERTIES:
      ore = entities.Ore(properties[ORE_NAME],
         point.Point(int(properties[ORE_COL]), int(properties[ORE_ROW])),
         image_store.get_images(i_store, properties[PROPERTY_KEY]),
         int(properties[ORE_RATE]))
      return ore
   else:
      return None


def create_blacksmith(properties, i_store):
   if len(properties) == SMITH_NUM_PROPERTIES:
      return entities.Blacksmith(properties[SMITH_NAME],
         point.Point(int(properties[SMITH_COL]), int(properties[SMITH_ROW])),
         image_store.get_images(i_store, properties[PROPERTY_KEY]),
         int(properties[SMITH_LIMIT]), int(properties[SMITH_RATE]),
         int(properties[SMITH_REACH]))
      return smith
   else:
      return None


def create_obstacle(properties, i_store):
   if len(properties) == OBSTACLE_NUM_PROPERTIES:
      return entities.Obstacle(properties[OBSTACLE_NAME],
         point.Point(int(properties[OBSTACLE_COL]), int(properties[OBSTACLE_ROW])),
         image_store.get_images(i_store, properties[PROPERTY_KEY]))
   else:
      return None


def schedule_entity(world, entity, i_store):
   if isinstance(entity, entities.MinerNotFull):
      actions.schedule_miner(world, entity, 0, i_store)
   elif isinstance(entity, entities.Vein):
      actions.schedule_vein(world, entity, 0, i_store)
   elif isinstance(entity, entities.Ore):
      actions.schedule_ore(world, entity, 0, i_store)
