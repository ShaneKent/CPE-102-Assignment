import builder_controller
import entities
import image_store
import pygame
import random
import save_load
import worldmodel
import worldview

IMAGE_LIST_FILE_NAME = 'imagelist'
WORLD_FILE = 'gaia.sav'

WORLD_WIDTH_SCALE = 2
WORLD_HEIGHT_SCALE = 2

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILE_WIDTH = 32
TILE_HEIGHT = 32


def create_default_background(img):
   return entities.Background(image_store.DEFAULT_IMAGE_NAME, img)


def main():
   random.seed()
   pygame.init()
   screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
   i_store = image_store.load_images(IMAGE_LIST_FILE_NAME,
      TILE_WIDTH, TILE_HEIGHT)

   num_cols = SCREEN_WIDTH // TILE_WIDTH * WORLD_WIDTH_SCALE
   num_rows = SCREEN_HEIGHT // TILE_HEIGHT * WORLD_HEIGHT_SCALE

   default_background = create_default_background(
      image_store.get_images(i_store, image_store.DEFAULT_IMAGE_NAME))

   world = worldmodel.WorldModel(num_rows, num_cols, default_background)
   view = worldview.WorldView(SCREEN_WIDTH // TILE_WIDTH,
      SCREEN_HEIGHT // TILE_HEIGHT, screen, world, TILE_WIDTH, TILE_HEIGHT)

   worldview.update_view(view)

   builder_controller.activity_loop(view, world, i_store)


if __name__ == '__main__':
   main()
