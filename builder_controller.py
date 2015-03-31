import entities
import image_store
import keys
import mouse_buttons
import point
import pygame
import random
import save_load
import worldview
import worldmodel

WORLD_FILE_NAME = 'gaia.sav'

BACKGROUND_TAGS = ['grass', 'rocks']

TIMER_FREQUENCY = 100

MINER_LIMIT = 2
MINER_RATE_MIN = 600
MINER_RATE_MAX = 1000
MINER_ANIMATION_RATE = 100
VEIN_RATE_MIN = 8000
VEIN_RATE_MAX = 17000
ORE_RATE_MIN = 20000
ORE_RATE_MAX = 30000
SMITH_LIMIT_MIN = 10
SMITH_LIMIT_MAX = 15
SMITH_RATE_MIN = 2000
SMITH_RATE_MAX = 4000


def mouse_to_tile(pos, tile_width, tile_height):
   return point.Point(pos[0] // tile_width, pos[1] // tile_height)


def save_world(world, filename):
   with open(filename, 'w') as file:
      save_load.save_world(world, file)


def load_world(world, i_store, filename):
   with open(filename, 'r') as file:
      save_load.load_world(world, i_store, file)


def on_keydown(event, world, entity_select, i_store):
   x_delta = 0
   y_delta = 0
   if event.key == pygame.K_UP: y_delta -= 1
   if event.key == pygame.K_DOWN: y_delta += 1
   if event.key == pygame.K_LEFT: x_delta -= 1
   if event.key == pygame.K_RIGHT: x_delta += 1
   elif event.key in keys.ENTITY_KEYS:
      entity_select = keys.ENTITY_KEYS[event.key]
   elif event.key == keys.SAVE_KEY: save_world(world, WORLD_FILE_NAME)
   elif event.key == keys.LOAD_KEY: load_world(world, i_store, WORLD_FILE_NAME)

   return ((x_delta, y_delta), entity_select)


def handle_mouse_motion(view, event):
   mouse_pt = mouse_to_tile(event.pos, view.tile_width, view.tile_height)
   worldview.mouse_move(view, mouse_pt)


def handle_keydown(view, event, i_store, world, entity_select):
   (view_delta, entity_select) = on_keydown(event, world,
      entity_select, i_store)
   worldview.update_view(view, view_delta,
      image_store.get_images(i_store, entity_select)[0])

   return entity_select


def create_new_entity(pt, entity_select, i_store):
   name = entity_select + '_' + str(pt.x) + '_' + str(pt.y)
   images = image_store.get_images(i_store, entity_select)
   if entity_select == 'obstacle':
      return entities.Obstacle(name, pt, images)
   elif entity_select == 'miner':
      return entities.MinerNotFull(name, MINER_LIMIT, pt,
         random.randint(MINER_RATE_MIN, MINER_RATE_MAX),
         images, MINER_ANIMATION_RATE)
   elif entity_select == 'vein':
      return entities.Vein(name,
         random.randint(VEIN_RATE_MIN, VEIN_RATE_MAX), pt, images)
   elif entity_select == 'ore':
      return entities.Ore(name, pt, images,
         random.randint(ORE_RATE_MIN, ORE_RATE_MAX))
   elif entity_select == 'blacksmith':
      return entities.Blacksmith(name, pt, images,
         random.randint(SMITH_LIMIT_MIN, SMITH_LIMIT_MAX),
         random.randint(SMITH_RATE_MIN, SMITH_RATE_MAX))
   else:
      return None


def is_background_tile(entity_select):
   return entity_select in BACKGROUND_TAGS


def handle_mouse_button(view, world, event, entity_select, i_store):
   mouse_pt = mouse_to_tile(event.pos, view.tile_width, view.tile_height)
   tile_view_pt = worldview.viewport_to_world(view.viewport, mouse_pt)
   if event.button == mouse_buttons.LEFT and entity_select:
      if is_background_tile(entity_select):
         worldmodel.set_background(world, tile_view_pt,
            entities.Background(entity_select,
               image_store.get_images(i_store, entity_select)))
         return [tile_view_pt]
      else:
         new_entity = create_new_entity(tile_view_pt, entity_select, i_store)
         if new_entity:
            worldmodel.remove_entity_at(world, tile_view_pt)
            worldmodel.add_entity(world, new_entity)
            return [tile_view_pt]
   elif event.button == mouse_buttons.RIGHT:
      worldmodel.remove_entity_at(world, tile_view_pt)
      return [tile_view_pt]

   return []


def activity_loop(view, world, i_store):
   pygame.key.set_repeat(keys.KEY_DELAY, keys.KEY_INTERVAL)

   entity_select = None
   while 1:
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            return
         elif event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(view, event)
         elif event.type == pygame.MOUSEBUTTONDOWN:
            tiles = handle_mouse_button(view, world, event, entity_select,
               i_store)
            worldview.update_view_tiles(view, tiles)
         elif event.type == pygame.KEYDOWN:
            entity_select = handle_keydown(view, event, i_store, world,
               entity_select)

