import pygame
import worldview
import worldmodel
import point

KEY_DELAY = 400
KEY_INTERVAL = 100

TIMER_FREQUENCY = 100

def on_keydown(event):
   x_delta = 0
   y_delta = 0
   if event.key == pygame.K_UP: y_delta -= 1
   if event.key == pygame.K_DOWN: y_delta += 1
   if event.key == pygame.K_LEFT: x_delta -= 1
   if event.key == pygame.K_RIGHT: x_delta += 1

   return (x_delta, y_delta)


def mouse_to_tile(pos, tile_width, tile_height):
   return point.Point(pos[0] // tile_width, pos[1] // tile_height)


def handle_timer_event(world, view):
   rects = worldmodel.update_on_time(world, pygame.time.get_ticks())
   worldview.update_view_tiles(view, rects)


def handle_mouse_motion(view, event):
   mouse_pt = mouse_to_tile(event.pos, view.tile_width, view.tile_height)
   worldview.mouse_move(view, mouse_pt)


def handle_keydown(view, event):
   view_delta = on_keydown(event)
   worldview.update_view(view, view_delta)


def activity_loop(view, world):
   pygame.key.set_repeat(KEY_DELAY, KEY_INTERVAL)
   pygame.time.set_timer(pygame.USEREVENT, TIMER_FREQUENCY)

   while 1:
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            return
         elif event.type == pygame.USEREVENT:
            handle_timer_event(world, view)
         elif event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(view, event)
         elif event.type == pygame.KEYDOWN:
            handle_keydown(view, event)

