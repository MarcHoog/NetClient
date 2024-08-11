import pygame
from pygame.locals import RESIZABLE, VIDEORESIZE
import sys
import logging
from logger import setup_logger

# Initialize Pygame
setup_logger()
pygame.init()

# Screen dimensions
GRAY = (200, 200, 200)
FONT = pygame.font.Font('./src/client/content/fonts/Maplestory Bold.ttf', 20)

pygame.display.set_caption("Pygame Chat Client")


class ResizableTextBox:
    
    def __init__(self, x, y, height, width):
        self.height = height
        self.width = width
        self.rect = pygame.rect.Rect(x, y, self.width, self.height)
 
        self.x = x
        self.y = y
        self.color = (255, 255, 255)
        self.border_color = (0, 0, 0)
        self.border_width = 3
        
        self.text = ''
        
        
    def draw(self, display):
        pygame.draw.rect(display, self.color, self.rect)
        pygame.draw.rect(display, self.border_color, self.rect, self.border_width)
        
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Creating an Square lol")
        
        # what we show
        self.screen = pygame.display.set_mode((1280, 960), RESIZABLE)

        # what we render on
        self.display = pygame.Surface((1280, 960))
        self.test = ResizableTextBox(40, 40, 40, 1200)
        self.clock = pygame.time.Clock()
        
    def run(self):
        
        while True:
            self.display.fill((14, 219, 248))
            self.test.draw(self.display)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quiting the Game.")
                    pygame.quit()
                    sys.exit()
                elif event.type == VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)
                    
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)
            
Game().run()

