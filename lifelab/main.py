import pygame
from math import cos, sin, tan
from critters import Critter, Kingdom
import cv2

class World:
    LIMIT = 50
    FPS = 30
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.critters = []
        self.window = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.bg = cv2.VideoCapture('water.mp4')
        success, img = self.bg.read()
        self.bgshape = img.shape[1::-1]

    def mkcritter(self):
        c = Critter(self)
        c.traits.randomize()
        c.calories = c.traits.calories
        c.breed_cooldown = c.traits.breed_cooldown
        c.place_randomly()
        return c

    def tick(self):
        self.clock.tick(self.FPS)
        success, img = self.bg.read()
        if not success:
            self.bg = cv2.VideoCapture('water.mp4')
            success, img = self.bg.read()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        self.window.fill( (0, 0, 255) )
        self.window.blit(pygame.image.frombuffer(img.tobytes(), self.bgshape, "BGR"), (0, 0))

        for critter in self.critters:
            critter.tick()

        for critter in self.critters:
            critter.draw()

        pygame.display.flip()
        return True

def gradientRect( window, left_colour, right_colour, target_rect ):
    """ Draw a horizontal-gradient filled rectangle covering <target_rect> """
    colour_rect = pygame.Surface( ( 2, 2 ) )                                   # tiny! 2x2 bitmap
    pygame.draw.line( colour_rect, left_colour,  ( 0,0 ), ( 0,1 ) )            # left colour line
    pygame.draw.line( colour_rect, right_colour, ( 1,0 ), ( 1,1 ) )            # right colour line
    colour_rect = pygame.transform.smoothscale( colour_rect, ( target_rect.width, target_rect.height ) )  # stretch!
    window.blit( colour_rect, target_rect )                                    # paint it


def main():
    world = World(800, 600)
    for i in range(15):
        world.critters.append(world.mkcritter())

    while True:
        if not world.tick():
            return

if __name__ == "__main__":
    main()
