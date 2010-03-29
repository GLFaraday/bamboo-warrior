import math

import pyglet
from pyglet.gl import *


class Terrain(object):
	def __init__(self, width=800, heightmap=[100,100,165,180,120,140]):
		self.width = width
		self.unit_width = width / (len(heightmap) - 1)
		self.heightmap = heightmap
		self.create_batch()

		self.wind_phase = 0

	resources_loaded = False

	def height_at(self, x):
		segment = x // self.unit_width
		if segment < 0:
			return self.heightmap[0]
		if segment >= (len(self.heightmap) - 1):
			return self.heightmap[-1]
		frac = float(x % self.unit_width) / self.unit_width
		y1, y2 = self.heightmap[segment:segment + 2]
		return frac * y2 + (1 - frac) * y1

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

		for i, h in enumerate(self.heightmap):
			x = self.unit_width * i
			earth_vertices += [x, 0, x, h]
			earth_texcoords += [x / 256.0, 1 - h / 256.0, x / 256.0, 1]

			grass_vertices += [x, h - 5, x, h + self.grass.height - 5]
			grass_texcoords += [x / 128.0, self.grass.tex_coords[1], x / 128.0, self.grass.tex_coords[7]]
		
		batch.add(len(earth_vertices) / 2, GL_QUAD_STRIP, earthgroup, ('v2i', earth_vertices), ('t2f', earth_texcoords))
		self.grass_list = batch.add(len(grass_vertices) / 2, GL_QUAD_STRIP, grassgroup, ('v2f', grass_vertices), ('t2f', grass_texcoords))
		
		self.batch = batch

	def update(self):
		"""Update the grass animation"""
		self.wind_phase += 0.08
		for i in range(len(self.heightmap)):
			base_x = i * self.unit_width
			dx = 4 * math.sin(self.wind_phase + base_x / 128.0 * 0.5) + 3 * math.sin(self.wind_phase * 0.375 + base_x / 128.0 * 0.5)
			self.grass_list.vertices[i * 4] = base_x + dx * -0.2
			self.grass_list.vertices[i * 4 + 2] = base_x + dx

	def draw(self):
		self.batch.draw()

