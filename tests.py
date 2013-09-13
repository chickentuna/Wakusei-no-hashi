from hashi_load import *
import sys

class Bubble(pygame.sprite.DirtySprite):
    animcycle = 6
    images = []

    def __init__(self,x,y):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = (x,y))
        self.subSprites = 2
        self.frame = 0
        self.add(Bubble.container)
    def update(self):
        self.frame+=1
        self.image = self.images[self.frame//self.animcycle%self.subSprites]
        self.dirty = 2
        self.visible = 0


SCREENRECT = Rect(0, 0, 640, 480)

# Initialize pygame
pygame.init()

# Set the display mode
winstyle = 0  # |FULLSCREEN
bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
background = pygame.Surface(SCREENRECT.size)
#Load images, assign to sprite classes
#(do this before the classes are used, after screen setup)
Bubble.images = load_images('happy1.png','happy2.png')

clock = pygame.time.Clock()

all = pygame.sprite.RenderUpdates()
Bubble.container = all

#get input
cont = True
bub = Bubble(20,20)
while cont:
   for event in pygame.event.get():
       if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
               cont = False
   keystate = pygame.key.get_pressed()

   # clear/erase the last drawn sprites
   all.clear(screen, background)

   #update all the sprites
   all.update()
    #draw the scene
   dirty = all.draw(screen)
   pygame.display.update(dirty)

   #cap the framerate
   clock.tick(30)