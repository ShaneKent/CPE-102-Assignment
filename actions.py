import entities
import worldmodel
import pygame
import math
import random
import point
import image_store

BLOB_RATE_SCALE = 4
BLOB_ANIMATION_RATE_SCALE = 50
BLOB_ANIMATION_MIN = 1
BLOB_ANIMATION_MAX = 3

ORE_CORRUPT_MIN = 20000
ORE_CORRUPT_MAX = 30000

QUAKE_STEPS = 10
QUAKE_DURATION = 1100
QUAKE_ANIMATION_RATE = 100

VEIN_SPAWN_DELAY = 500
VEIN_RATE_MIN = 8000
VEIN_RATE_MAX = 17000

def sign(x):
   if x < 0:
      return -1
   elif x > 0:
      return 1
   else:
      return 0

def next_position(world, entity_pt, dest_pt):
   horiz = sign(dest_pt.x - entity_pt.x)
   new_pt = point.Point(entity_pt.x + horiz, entity_pt.y)

   if horiz == 0 or world.is_occupied(new_pt):
      vert = sign(dest_pt.y - entity_pt.y)
      new_pt = point.Point(entity_pt.x, entity_pt.y + vert)

      if vert == 0 or world.is_occupied(new_pt):
         new_pt = point.Point(entity_pt.x, entity_pt.y)

   return new_pt

def blob_next_position(world, entity_pt, dest_pt):
   horiz = sign(dest_pt.x - entity_pt.x)
   new_pt = point.Point(entity_pt.x + horiz, entity_pt.y)

   if horiz == 0 or (world.is_occupied(new_pt) and
      not isinstance(world.get_tile_occupant(new_pt),
      entities.Ore)):
      vert = sign(dest_pt.y - entity_pt.y)
      new_pt = point.Point(entity_pt.x, entity_pt.y + vert)

      if vert == 0 or (world.is_occupied(new_pt) and
         not isinstance(world.get_tile_occupant(new_pt),
         entities.Ore)):
         new_pt = point.Point(entity_pt.x, entity_pt.y)

   return new_pt

def miner_to_ore(world, entity, ore):
   entity_pt = entity.get_position()
   if not ore:
      return ([entity_pt], False)
   ore_pt = ore.get_position()
   if entity_pt.adjacent(ore_pt):
      entity.set_resource_count(1 + entity.get_resource_count())
      remove_entity(world, ore)
      return ([ore_pt], True)
   else:
      new_pt = next_position(world, entity_pt, ore_pt)
      return (world.move_entity(entity, new_pt), False)


def miner_to_smith(world, entity, smith):
   entity_pt = entity.get_position()
   if not smith:
      return ([entity_pt], False)
   smith_pt = smith.get_position()
   if entity_pt.adjacent(smith_pt):
      smith.set_resource_count(smith.get_resource_count() + entity.get_resource_count())
      entity.set_resource_count(0)
      return ([], True)
   else:
      new_pt = next_position(world, entity_pt, smith_pt)
      return (world.move_entity(entity, new_pt), False)


def create_miner_not_full_action(world, entity, i_store):
   def action(current_ticks):
      entity.remove_pending_action(action)

      entity_pt = entity.get_position()
      ore = world.find_nearest(entity_pt, entities.Ore)
      (tiles, found) = miner_to_ore(world, entity, ore)

      new_entity = entity
      if found:
         new_entity = try_transform_miner(world, entity,
            try_transform_miner_not_full)

      schedule_action(world, new_entity,
         create_miner_action(world, new_entity, i_store),
         current_ticks + new_entity.get_rate())
      return tiles
   return action


def create_miner_full_action(world, entity, i_store):
   def action(current_ticks):
      entity.remove_pending_action(action)

      entity_pt = entity.get_position()
      smith = world.find_nearest(entity_pt, entities.Blacksmith)
      (tiles, found) = miner_to_smith(world, entity, smith)

      new_entity = entity
      if found:
         new_entity = try_transform_miner(world, entity,
            try_transform_miner_full)

      schedule_action(world, new_entity,
         create_miner_action(world, new_entity, i_store),
         current_ticks + new_entity.get_rate())
      return tiles
   return action


def blob_to_vein(world, entity, vein):
   entity_pt = entity.get_position()
   if not vein:
      return ([entity_pt], False)
   vein_pt = vein.get_position()
   if entity_pt.adjacent(vein_pt):
      remove_entity(world, vein)
      return ([vein_pt], True)
   else:
      new_pt = blob_next_position(world, entity_pt, vein_pt)
      old_entity = world.get_tile_occupant(new_pt)
      if isinstance(old_entity, entities.Ore):
         remove_entity(world, old_entity)
      return (world.move_entity(entity, new_pt), False)


def create_ore_blob_action(world, entity, i_store):
   def action(current_ticks):
      entity.remove_pending_action(action)

      entity_pt = entity.get_position()
      vein = world.find_nearest(entity_pt, entities.Vein)
      (tiles, found) = blob_to_vein(world, entity, vein)

      next_time = current_ticks + entity.get_rate()
      if found:
         quake = create_quake(world, tiles[0], current_ticks, i_store)
         world.add_entity(quake)
         next_time = current_ticks + entity.get_rate() * 2

      schedule_action(world, entity,
         create_ore_blob_action(world, entity, i_store),
         next_time)

      return tiles
   return action


def find_open_around(world, pt, distance):
   for dy in range(-distance, distance + 1):
      for dx in range(-distance, distance + 1):
         new_pt = point.Point(pt.x + dx, pt.y + dy)

         if (world.within_bounds(new_pt) and
            (not world.is_occupied(new_pt))):
            return new_pt

   return None


def create_vein_action(world, entity, i_store):
   def action(current_ticks):
      entity.remove_pending_action(action)

      open_pt = find_open_around(world, entity.get_position(),
         entity.get_resource_distance())
      if open_pt:
         ore = create_ore(world,
            "ore - " + entity.get_name() + " - " + str(current_ticks),
            open_pt, current_ticks, i_store)
         world.add_entity(ore)
         tiles = [open_pt]
      else:
         tiles = []

      schedule_action(world, entity,
         create_vein_action(world, entity, i_store),
         current_ticks + entity.get_rate())
      return tiles
   return action


def try_transform_miner_full(world, entity):
   new_entity = entities.MinerNotFull(
      entity.get_name(), entity.get_resource_limit(),
      entity.get_position(), entity.get_rate(),
      entity.get_images(), entity.get_animation_rate())

   return new_entity


def try_transform_miner_not_full(world, entity):
   if entity.resource_count < entity.resource_limit:
      return entity
   else:
      new_entity = entities.MinerFull(
         entity.get_name(), entity.get_resource_limit(),
         entity.get_position(), entity.get_rate(),
         entity.get_images(), entity.get_animation_rate())
      return new_entity


def try_transform_miner(world, entity, transform):
   new_entity = transform(world, entity)
   if entity != new_entity:
      clear_pending_actions(world, entity)
      world.remove_entity_at(entity.get_position())
      world.add_entity(new_entity)
      schedule_animation(world, new_entity)

   return new_entity


def create_miner_action(world, entity, image_store):
   if isinstance(entity, entities.MinerNotFull):
      return create_miner_not_full_action(world, entity, image_store)
   else:
      return create_miner_full_action(world, entity, image_store)


def create_animation_action(world, entity, repeat_count):
   def action(current_ticks):
      entity.remove_pending_action(action)

      entity.next_image()

      if repeat_count != 1:
         schedule_action(world, entity,
            create_animation_action(world, entity, max(repeat_count - 1, 0)),
            current_ticks + entity.get_animation_rate())

      return [entity.get_position()]
   return action


def create_entity_death_action(world, entity):
   def action(current_ticks):
      entity.remove_pending_action(action)
      pt = entity.get_position()
      remove_entity(world, entity)
      return [pt]
   return action


def create_ore_transform_action(world, entity, i_store):
   def action(current_ticks):
      entity.remove_pending_action(action)
      blob = create_blob(world, entity.get_name() + " -- blob",
         entity.get_position(),
         entity.get_rate() // BLOB_RATE_SCALE,
         current_ticks, i_store)

      remove_entity(world, entity)
      world.add_entity(blob)

      return [blob.get_position()]
   return action


def remove_entity(world, entity):
   for action in entity.get_pending_actions():
      world.unschedule_action(action)
   entity.clear_pending_actions()
   world.remove_entity(entity)


def create_blob(world, name, pt, rate, ticks, i_store):
   blob = entities.OreBlob(name, pt, rate,
      image_store.get_images(i_store, 'blob'),
      random.randint(BLOB_ANIMATION_MIN, BLOB_ANIMATION_MAX)
      * BLOB_ANIMATION_RATE_SCALE)
   schedule_blob(world, blob, ticks, i_store)
   return blob


def schedule_blob(world, blob, ticks, i_store):
   schedule_action(world, blob, create_ore_blob_action(world, blob, i_store),
      ticks + blob.get_rate())
   schedule_animation(world, blob)


def schedule_miner(world, miner, ticks, i_store):
   schedule_action(world, miner, create_miner_action(world, miner, i_store),
      ticks + miner.get_rate())
   schedule_animation(world, miner)


def create_ore(world, name, pt, ticks, i_store):
   ore = entities.Ore(name, pt, image_store.get_images(i_store, 'ore'),
      random.randint(ORE_CORRUPT_MIN, ORE_CORRUPT_MAX))
   schedule_ore(world, ore, ticks, i_store)

   return ore


def schedule_ore(world, ore, ticks, i_store):
   schedule_action(world, ore,
      create_ore_transform_action(world, ore, i_store),
      ticks + ore.get_rate())


def create_quake(world, pt, ticks, i_store):
   quake = entities.Quake("quake", pt,
      image_store.get_images(i_store, 'quake'), QUAKE_ANIMATION_RATE)
   schedule_quake(world, quake, ticks)
   return quake


def schedule_quake(world, quake, ticks):
   schedule_animation(world, quake, QUAKE_STEPS) 
   schedule_action(world, quake, create_entity_death_action(world, quake),
      ticks + QUAKE_DURATION)


def create_vein(world, name, pt, ticks, i_store):
   vein = entities.Vein("vein" + name,
      random.randint(VEIN_RATE_MIN, VEIN_RATE_MAX),
      pt, image_store.get_images(i_store, 'vein'))
   return vein


def schedule_vein(world, vein, ticks, i_store):
   schedule_action(world, vein, create_vein_action(world, vein, i_store),
      ticks + vein.get_rate())


def schedule_action(world, entity, action, time):
   entity.add_pending_action(action)
   world.schedule_action(action, time)


def schedule_animation(world, entity, repeat_count=0):
   schedule_action(world, entity,
      create_animation_action(world, entity, repeat_count),
      entity.get_animation_rate())


def clear_pending_actions(world, entity):
   for action in entity.get_pending_actions():
      world.unschedule_action(action)
   entity.clear_pending_actions()
