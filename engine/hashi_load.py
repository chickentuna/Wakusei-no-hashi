import random, os.path

#import basic pygame modules
import pygame
from pygame.locals import *
from hashi_play import main_dir

#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


if main_dir[-4:] == '.exe':
    main_dir = main_dir[:main_dir.rfind('\\')]


def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)

    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert_alpha()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs

def load_sequence(file, num, ext):
    files = []

    for i in range(num):
        files += [file+str(i)+ext]
    return load_images(*files)