import entities
from worldmodel import *
from pygame import *
from math import *
from random import *
from point import *
from image_store import *

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


 
# LEAVE THESE FUNCTIONS HERE

#This is used by too many functions in this file.
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

#Ties both of the miner classes together.
def try_transform_miner(world, entity, transform):
   new_entity = transform(world)
   if entity != new_entity:
      clear_pending_actions(world, entity)
      world.remove_entity_at(entity.get_position())
      world.add_entity(new_entity)
      schedule_animation(world, new_entity)

   return new_entity

#Connected to too many different functions in many different functions.
def remove_entity(world, entity):
   for action in entity.get_pending_actions():
      world.unschedule_action(action)
   entity.clear_pending_actions()
   world.remove_entity(entity)



#Used to create a blob, wouldn't be in the Blob class.
def create_blob(world, name, pt, rate, ticks, i_store):
   blob = entities.OreBlob(name, pt, rate,
      get_images(i_store, 'blob'),
      randint(BLOB_ANIMATION_MIN, BLOB_ANIMATION_MAX)
      * BLOB_ANIMATION_RATE_SCALE)
   blob.schedule_blob(world, ticks, i_store)
   return blob

#Used to create a ore, wouldn't be in the Ore class.
def create_ore(world, name, pt, ticks, i_store):
   ore = entities.Ore(name, pt, get_images(i_store, 'ore'),
      randint(ORE_CORRUPT_MIN, ORE_CORRUPT_MAX))
   ore.schedule_ore(world, ticks, i_store)

   return ore
   
#Used to create a quake, wouldn't be in the Quake class.
def create_quake(world, pt, ticks, i_store):
   quake = entities.Quake("quake", pt,
      get_images(i_store, 'quake'), QUAKE_ANIMATION_RATE)
   quake.schedule_quake(world, ticks)
   return quake

#Used to create a vein, wouldn't be in the Vein class.
def create_vein(world, name, pt, ticks, i_store):
   vein = entities.Vein("vein" + name,
      randint(VEIN_RATE_MIN, VEIN_RATE_MAX),
      pt, get_images(i_store, 'vein'))
   return vein
      
      
      
#Higher level function used for nearly all classes in Entity
def schedule_action(world, entity, action, time):
   entity.add_pending_action(action)
   world.schedule_action(action, time)

#Higher level function used for nearly all classes in Entity
def schedule_animation(world, entity, repeat_count=0):
   schedule_action(world, entity,
      create_animation_action(world, entity, repeat_count),
      entity.get_animation_rate())
      
#Higher level function used for nearly all classes in Entity
def clear_pending_actions(world, entity):
   for action in entity.get_pending_actions():
      world.unschedule_action(action)
   entity.clear_pending_actions()