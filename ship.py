import pygame, sector, random, hashi_play
from math import cos, sin, radians, ceil
import hashi

#TODO: orbit algo : Make a circle function on a 2D plane then transform the result into orbit around 3D.


def deg_to_offset(deg, offset):
    x = cos(radians(deg)) * offset
    y = sin(radians(deg)) * offset
    return (x, y)


class Ship(pygame.sprite.DirtySprite):
	travelling 		= 0
	orbiting 		= 1
	orbit_to_travel = 2
	travel_to_orbit = 3	

	images = []

	speed = 10
	radius = 1
	plane_max = 1.5
	plane_min = 0.5

	def __init__(self, node):
		self.groups = self.container, sector.visible_sprites # assign groups BEFORE calling pygame.sprite.Sprite.__init__
		pygame.sprite.DirtySprite.__init__(self,  self.groups) #call parent class. NEVER FORGET !
		
		self.start_node = node
		self.state = Ship.orbiting
		self.image_init = self.images[0]
		self.image = self.image_init
		#self.add(self.container)
		#self.add(sector.visible_sprites)
		self.gravity_center = hashi_play.vectorAdd(hashi_play.grid_offset, hashi_play.cellCenter((node.y,node.x)))
		self.rect = self.image.get_rect(center = self.gravity_center)
		self.direction = random.randint(0,359)
		self.theta = 0

		
	def update(self):
		if self.state == Ship.orbiting:
			self.theta = (self.theta + self.speed)%360
			depth = self.radius * cos(radians(self.theta))

			sector.visible_sprites.change_layer(self,-7)
			coeff = hashi_play.cell_size/2
			position = coeff*self.radius * sin(radians(self.theta))

			xr = cos(radians(self.direction))*(position) + self.gravity_center[0]
			yr = sin(radians(self.direction))*(position) + self.gravity_center[1]
			self.rect.centerx = xr
			self.rect.centery = yr
			
			scale = (self.plane_max-self.plane_min)*(depth + self.radius)/(self.radius*2) + self.plane_min
			if scale < 1:
				sector.visible_sprites.change_layer(self,-1)
			else:
				sector.visible_sprites.change_layer(self,1)
			self.image, self.rect = hashi.rotozoom_center(self.image_init, self.rect, 0, scale);


