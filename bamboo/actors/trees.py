import random

import pyglet
from pyglet.gl import *

from base import Actor


class BambooTree(Actor):
	height = 20

	PIECE_HEIGHT = 61

	def __init__(self, x=60, height=20):
		self.height = height
		self.x = x
		self.y = 0
		self.create_sprites()

	resources_loaded = False

	@classmethod
	def on_class_load(cls):
		cls.load_texture('piece', 'bamboo-piece.png', anchor_x='center')
		cls.load_texture('leaf1', 'bamboo-leaf1.png')
		cls.load_texture('leaf2', 'bamboo-leaf2.png')

	def create_sprites(self):
		self.load_resources()
		self.batch = pyglet.graphics.Batch()
		self.pieces = []

		for i in range(self.height):
			if i > 7:
				if random.randint(0, 3) == 0:
					l = random.choice(['leaf1', 'leaf2'])
					self.pieces.append(pyglet.sprite.Sprite(self.textures[l], x=self.x + 23, y=self.PIECE_HEIGHT * i + self.y, batch=self.batch))
			self.pieces.append(pyglet.sprite.Sprite(self.textures['piece'], x=self.x, y=self.PIECE_HEIGHT * i + self.y, batch=self.batch))

	def draw(self):
		glPushMatrix(GL_MODELVIEW)
		glTranslatef(self.x, self.y, 0)
		self.batch.draw()
		glPopMatrix(GL_MODELVIEW)

