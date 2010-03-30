import math

import pyglet
from pyglet.gl import *

from bamboo.geom import Vec2


class Terrain(object):
	def __init__(self, outline):
		"""Create the terrain from a list of (at least 2) Vec2s outline"""
		self.outline = outline
		self.create_batch()
		self.wind_phase = 0

	resources_loaded = False

	def height_at(self, x):
		last = None
		for i, v in enumerate(self.outline):
			if x < v.x:
				if last is None:
					return v.x
				frac = float(x - last.x) / float(v.x - last.x)
				return frac * v.y + (1 - frac) * last.y
			last = v
		else:
			return last.y

	@classmethod
	def load_resources(cls):
		if cls.resources_loaded:
			return
		cls.earth = pyglet.resource.texture('earth.png')
		cls.grass = pyglet.resource.texture('grass.png')

	def create_batch(self):
		self.load_resources()
		layer1 = pyglet.graphics.OrderedGroup(1)
		layer2 = pyglet.graphics.OrderedGroup(2)
		earthgroup = pyglet.graphics.TextureGroup(self.earth, parent=layer1)
		grassgroup = pyglet.sprite.SpriteGroup(self.grass, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, parent=layer2)
		
		batch = pyglet.graphics.Batch()

		earth_vertices = []
		earth_texcoords = []
		grass_vertices = []
		grass_texcoords = []

		for v in self.outline:
			earth_vertices += [v.x, 0, v.x, v.y]
			earth_texcoords += [v.x / 256.0, 1 - v.y / 256.0, v.x / 256.0, 1]

			# TODO: split grass at regular intervals for wind effect
			grass_vertices += [v.x, v.y - 5, v.x, v.y + self.grass.height - 5]
			grass_texcoords += [v.x / 128.0, self.grass.tex_coords[1], v.x / 128.0, self.grass.tex_coords[7]]
		
		batch.add(len(earth_vertices) / 2, GL_QUAD_STRIP, earthgroup, ('v2f', earth_vertices), ('t2f', earth_texcoords))
		self.grass_list = batch.add(len(grass_vertices) / 2, GL_QUAD_STRIP, grassgroup, ('v2f', grass_vertices), ('t2f', grass_texcoords))
		
		self.batch = batch

	def update(self):
		"""Update the grass animation"""
		self.wind_phase += 0.08
		for i, v in enumerate(self.outline):
			dx = 4 * math.sin(self.wind_phase + v.x / 128.0 * 0.5) + 3 * math.sin(self.wind_phase * 0.375 + v.x / 128.0 * 0.5)
			self.grass_list.vertices[i * 4] = v.x + dx * -0.2
			self.grass_list.vertices[i * 4 + 2] = v.x + dx

	def draw(self):
		self.batch.draw()

