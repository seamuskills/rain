# this will be a level editor
import pygame

screenSize = [1080, 720 + 40] #giving myself a little room to make potential ui?
sc = pygame.display.set_mode(screenSize, flags=pygame.DOUBLEBUF)
c = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()