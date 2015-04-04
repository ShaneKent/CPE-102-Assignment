import pygame
import worldmodel
import entities
import point

MOUSE_HOVER_ALPHA = 120
MOUSE_HOVER_EMPTY_COLOR = (0, 255, 0)
MOUSE_HOVER_OCC_COLOR = (255, 0, 0)

class WorldView:
   def __init__(self, view_cols, view_rows, screen, world, tile_width,
      tile_height, mouse_img=None):
      self.viewport = pygame.Rect(0, 0, view_cols, view_rows)
      self.screen = screen
      self.mouse_pt = point.Point(0, 0)
      self.world = world
      self.tile_width = tile_width
      self.tile_height = tile_height
      self.num_rows = world.num_rows
      self.num_cols = world.num_cols
      self.mouse_img = mouse_img


def viewport_to_world(viewport, pt):
   return point.Point(pt.x + viewport.left, pt.y + viewport.top)


def world_to_viewport(viewport, pt):
   return point.Point(pt.x - viewport.left, pt.y - viewport.top)


def clamp(v, low, high):
   return min(high, max(v, low))


def create_shifted_viewport(viewport, delta, num_rows, num_cols):
   new_x = clamp(viewport.left + delta[0], 0, num_cols - viewport.width)
   new_y = clamp(viewport.top + delta[1], 0, num_rows - viewport.height)

   return pygame.Rect(new_x, new_y, viewport.width, viewport.height)


def draw_background(view):
   for y in range(0, view.viewport.height):
      for x in range(0, view.viewport.width):
         w_pt = viewport_to_world(view.viewport, point.Point(x, y))
         img = worldmodel.get_background_image(view.world, w_pt)
         view.screen.blit(img, (x * view.tile_width, y * view.tile_height))


def draw_entities(view):
   for entity in view.world.entities:
      if view.viewport.collidepoint(entity.position.x, entity.position.y):
         v_pt = world_to_viewport(view.viewport, entity.position)
         view.screen.blit(entity.get_image(),
            (v_pt.x * view.tile_width, v_pt.y * view.tile_height))


def draw_viewport(view):
   draw_background(view)
   draw_entities(view)


def update_view(view, view_delta=(0,0), mouse_img=None):
   view.viewport = create_shifted_viewport(view.viewport, view_delta,
      view.num_rows, view.num_cols)
   view.mouse_img = mouse_img
   draw_viewport(view)
   pygame.display.update()
   mouse_move(view, view.mouse_pt)


def update_view_tiles(view, tiles):
   rects = []
   for tile in tiles:
      if view.viewport.collidepoint(tile.x, tile.y):
         v_pt = world_to_viewport(view.viewport, tile)
         img = get_tile_image(view, v_pt)
         rects.append(update_tile(view, v_pt, img))
         if view.mouse_pt.x == v_pt.x and view.mouse_pt.y == v_pt.y:
            rects.append(update_mouse_cursor(view))

   pygame.display.update(rects)


def update_tile(view, view_tile_pt, surface):
   abs_x = view_tile_pt.x * view.tile_width
   abs_y = view_tile_pt.y * view.tile_height

   view.screen.blit(surface, (abs_x, abs_y))

   return pygame.Rect(abs_x, abs_y, view.tile_width, view.tile_height)


def get_tile_image(view, view_tile_pt):
   pt = viewport_to_world(view.viewport, view_tile_pt)
   bgnd = worldmodel.get_background_image(view.world, pt)
   occupant = worldmodel.get_tile_occupant(view.world, pt)
   if occupant:
      img = pygame.Surface((view.tile_width, view.tile_height))
      img.blit(bgnd, (0, 0))
      img.blit(occupant.get_image(), (0,0))
      return img
   else:
      return bgnd


def create_mouse_surface(view, occupied):
   surface = pygame.Surface((view.tile_width, view.tile_height))
   surface.set_alpha(MOUSE_HOVER_ALPHA)
   color = MOUSE_HOVER_EMPTY_COLOR
   if occupied:
      color = MOUSE_HOVER_OCC_COLOR
   surface.fill(color)
   if view.mouse_img:
      surface.blit(view.mouse_img, (0, 0))

   return surface


def update_mouse_cursor(view):
   return update_tile(view, view.mouse_pt,
      create_mouse_surface(view,
         worldmodel.is_occupied(view.world,
            viewport_to_world(view.viewport, view.mouse_pt))))


def mouse_move(view, new_mouse_pt):
   rects = []

   rects.append(update_tile(view, view.mouse_pt,
      get_tile_image(view, view.mouse_pt)))

   if view.viewport.collidepoint(new_mouse_pt.x + view.viewport.left,
      new_mouse_pt.y + view.viewport.top):
      view.mouse_pt = new_mouse_pt

   rects.append(update_mouse_cursor(view))

   pygame.display.update(rects)

