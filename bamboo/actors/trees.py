import math
import random

import pyglet
from pyglet.gl import *

from base import Actor

from bamboo.geom import Vec2


class Climbable(object):
	def __init__(self):
		self.actors = []

	def is_climbable(self):
		return True

	def add_actor(self, a):
		a.climbing = self
		a.climbing_height = self.height_for_y(a.y)
		self.actors.append(a)

	def remove_actor(self, a):
		a.climbing = None
		self.actors.remove(a)

	def climb_up(self, a):
		a.climbing_height = min(self.height - 2, a.climbing_height + 10.0 / self.PIECE_HEIGHT)

	def climb_down(self, a):
		a.climbing_height = max(0, a.climbing_height - 10.0 / self.PIECE_HEIGHT)

	def height_for_y(self, y):
		raise NotImplementedError("Climbable objects must implement .height_for_y()")

	def distance_from(self, x, y):
		raise NotImplementedError("Climbable objects must implement .distance_from()")


class BambooTree(Actor, Climbable):
	height = 20

	PIECE_HEIGHT = 64
	RADIUS = 12.5
	TEX_PERIOD = 1
	THINNING = 0.98		# trees get thinner as you go up, by this ratio per segment

	def __init__(self, x=60, height=20, angle=0):
		Climbable.__init__(self)
		self.height = height
		self.x = x
		self.y = 0
		self.base_angle = angle
		self.wobble_angle = 0
		self.wind_phase = 0
		self.create_sprites()

	def on_spawn(self):
		self.wind_phase = 0.1 * self.x

	def distance_from(self, x, y):
		"""Estimate the distance from x, y to this tree. This only works for small wobbly angles."""
		da = self.wobble_angle / self.height

		pos = Vec2(self.x, self.y)
		step = Vec2(0, self.PIECE_HEIGHT).rotate(self.base_angle)
		radius = Vec2(self.RADIUS, 0).rotate(self.base_angle)

		if pos.y > y:
			return (Vec2(x, y) - pos).mag()

		for i in range(self.height + 1):
			if pos.y > y:
				return abs(pos.x - x)
			pos += step
			step.rotate(da)	
		
		return (Vec2(x, y) - pos).mag()

	def height_for_y(self, y):
		"""Estimate the height in this tree for a coordinate of y. This only works for small wobble angles."""
		da = self.wobble_angle / self.height

		pos = Vec2(self.x, self.y)
		step = Vec2(0, self.PIECE_HEIGHT).rotate(self.base_angle)
		radius = Vec2(self.RADIUS, 0).rotate(self.base_angle)

		for i in range(self.height + 1):
			if step.y <= 0:
				raise ValueError("Tree does not reach a height of %f." % y)
			next = pos + step
			if next.y >= y:
				return i + float(y - pos.y) / step.y
			pos += step
			step.rotate(da)	
		raise ValueError("Tree does not reach a height of %f." % y)

	@classmethod
	def on_class_load(cls):
		cls.load_texture('piece', 'bamboo-piece.png', anchor_x='center')
		cls.load_texture('leaf1', 'bamboo-leaf1.png', anchor_x='right')
		cls.load_texture('leaf2', 'bamboo-leaf2.png', anchor_x='right')

	def get_parent_group(self):
		return None

	def create_sprites(self):
		self.load_resources()
		self.batch = pyglet.graphics.Batch()
		self.foliage = {}

		tex = self.textures['piece']
		vertices = []
		tex_coords = []

		h = 0
		r = self.RADIUS
		for i in range(self.height + 1):
			vertices += [-self.RADIUS, h, self.RADIUS, h]
			r = r * self.THINNING
			tex_coords += [tex.tex_coords[0], (i + 1) * self.TEX_PERIOD, tex.tex_coords[3], (i + 1) * self.TEX_PERIOD]
			h += self.PIECE_HEIGHT

		parent_group = self.get_parent_group()
		group = pyglet.sprite.SpriteGroup(self.textures['piece'], GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, parent=parent_group)
		self.vertex_list = self.batch.add((self.height + 1) * 2, GL_QUAD_STRIP, group, ('v2f', vertices), ('t2f', tex_coords))
	
		for i in range(self.height):
			prob = self.height - i
			if random.random() * prob < 1:
				l = random.choice(['leaf1', 'leaf2'])
				self.foliage.setdefault(i, []).append((-1, pyglet.sprite.Sprite(self.textures[l], x=self.x, y=self.PIECE_HEIGHT * i + self.y, batch=self.batch, group=parent_group)))
			if random.random() * prob < 1:
				l = random.choice(['leaf1', 'leaf2'])
				self.foliage.setdefault(i, []).append((01, pyglet.sprite.Sprite(self.textures[l].get_transform(flip_x=True), x=self.x, y=self.PIECE_HEIGHT * i + self.y, batch=self.batch, group=parent_group)))

	def set_trunk_vertex(self, i, v):
		x, y = v
		self.vertex_list.vertices[i * 2] = x
		self.vertex_list.vertices[i * 2 + 1] = y

	def compute_wobble(self):
		"""Generator for the vertex list. Iterate to give a sequence of Vec2 objects"""
		da = self.wobble_angle / self.height

		pos = Vec2(self.x, self.y)
		step = Vec2(0, self.PIECE_HEIGHT).rotate(self.base_angle)
		radius = Vec2(self.RADIUS, 0).rotate(self.base_angle)

		actor_segments = {}
		for a in self.actors:
			h = int(a.climbing_height)
			actor_segments.setdefault(h, []).append(a)

		for i in range(self.height + 1):
			self.set_trunk_vertex(2 * i, pos - radius)
			self.set_trunk_vertex(2 * i + 1, pos + radius)
			for side, f in self.foliage.get(i, []):
				p = pos + side * radius
				f.x = p.x
				f.y = p.y
				f.rotation = -radius.angle_in_degrees()

			for a in actor_segments.get(i, []):
				h = a.climbing_height - i
				apos = pos + h * step
				a.x, a.y = apos
				a.rotation = -radius.angle_in_degrees()

			pos += step
			step = step.rotate(da)
			radius = radius.rotate(da) * self.THINNING

	def update(self):
		self.wind_phase += 1.0 / self.height
		self.wobble_angle = 0.4 * math.sin(self.wind_phase) + 0.2 * math.sin(self.wind_phase * 0.21) 
		self.compute_wobble()

	def draw(self):
		self.batch.draw()



class BackgroundGroup(pyglet.graphics.Group):
	def __init__(self, depth=0.5, parent=None):
		super(BackgroundGroup, self).__init__(parent)
		self.depth = depth
	
	def set_state(self):
		d = self.depth
		glColor3f(d, d, d)

	def unset_state(self):
		glColor3f(1, 1, 1)
		

class BackgroundBambooTree(BambooTree):
	RADIUS = 8
	
	PIECE_HEIGHT = 128
	TEX_PERIOD = 2

	def __init__(self, *args, **kwargs):
		self.shadow = random.random() * 0.7
		super(BackgroundBambooTree, self).__init__(*args, **kwargs)	

	def is_climbable(self):
		return False

	@classmethod
	def on_class_load(cls):
		cls.load_texture('piece', 'bamboo-piece-blurred.png', anchor_x='center')
		cls.load_texture('leaf1', 'bamboo-leaf1.png', anchor_x='right')
		cls.load_texture('leaf2', 'bamboo-leaf2.png', anchor_x='right')

	def on_spawn(self):
		self.RADIUS = random.random() ** 0.5 * 10 + 2
		self.wobble_angle = random.random() * 1 - 0.5
		self.compute_wobble()

	def get_parent_group(self):
		return BackgroundGroup(self.shadow)

	def update(self):
		pass
