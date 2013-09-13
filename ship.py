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

	plane_max = 1.5
	plane_min = 0.5
	acceleration_default = 0.2
	max_speed = 2

	images = []

	def __init__(self, node):
		pygame.sprite.DirtySprite.__init__(self)
		self.start_node = node
		self.state = Ship.orbiting
		self.image_init = self.images[0]
		self.image = self.image_init
		self.add(self.container)
		self.add(sector.visible_sprites)
		self.rect = self.image.get_rect(center = hashi_play.vectorAdd(hashi_play.grid_offset, hashi_play.cellCenter((node.y,node.x))))
		self.plane = self.plane_max
		self.timeout = 22
		self.momentum = self.max_speed
		self.direction = random.randint(1,360)
		self.frame = self.timeout/2
		self.acceleration = self.acceleration_default

	def update(self):
		max_speed = self.max_speed
		plane_max = self.plane_max
		plane_min = self.plane_min

		if self.state == Ship.orbiting:
			speed = self.momentum + self.acceleration
			if self.acceleration > 0:
				self.momentum = min(speed, max_speed)
			else:
				self.momentum = max(speed, -max_speed)

			self.rect.move_ip(*(deg_to_offset(self.direction,self.momentum)))
			
			if self.momentum == -max_speed or self.momentum == max_speed:
				self.frame += 1
			if self.frame == self.timeout:
				self.frame = 0
				self.acceleration *= -1

		X = (2.*max_speed*plane_max)/(plane_max - plane_min) - max_speed
		Y = (2.*max_speed)/(plane_max - plane_min)


		self.plane = (self.momentum + X)/Y
		self.image, self.rect = hashi.rotozoom_center(self.image_init, self.rect, 0, self.plane);
		#print self.plane

	def getLayer():
		if (self.plane >= (self.plane_max + self.plane_min)/2):
			return 1
		else:
			return 2


