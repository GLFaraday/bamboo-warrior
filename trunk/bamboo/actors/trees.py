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
		a.climbing_height = self.height_for_y(a.pos.y)
		self.actors.append(a)

	def remove_actor(self, a):
		a.climbing = None
		self.actors.remove(a)

	def climb_up(self, a, dist=10.0):
		a.climbing_height = min(self.height - 2, a.climbing_height + float(dist) / self.PIECE_HEIGHT)

	def climb_down(self, a, dist=10.0):
		a.climbing_height = max(0, a.climbing_height - float(dist) / self.PIECE_HEIGHT)
		if a.climbing_height == 0:
			self.remove_actor(a)

	def height_for_y(self, y):
		raise NotImplementedError("Climbable objects must implement .height_for_y()")

	def distance_from(self, pos):
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
		self.pos = Vec2(x, 0)
		self.base_angle = angle
		self.wobble_angle = 0
		self.wind_phase = 0
		self.create_sprites()

	def on_spawn(self):
		self.wind_phase = 0.1 * self.pos.x

	def distance_from(self, p):
		"""Estimate the distance from x, y to this tree. This only works for small wobbly angles."""
		da = self.wobble_angle / self.height

		pos = self.pos
		step = Vec2(0, self.PIECE_HEIGHT).rotate(self.base_angle)
		radius = Vec2(self.RADIUS, 0).rotate(self.base_angle)

		if pos.y > p.y:
			return (p - pos).mag()

		for i in range(self.height + 1):
			if pos.y > p.y:
				return abs(pos.x - p.x)
			pos += step
			step.rotate(da)	
		
		return (p - pos).mag()

	def height_for_y(self, y):
		"""Estimate the height in this tree for a coordinate of y. This only works for small wobble angles."""
		da = self.wobble_angle / self.height

		pos = self.pos
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
		cls.load_directional_sprite('leaf1', 'bamboo-leaf1.png', anchor_x='right')
		cls.load_directional_sprite('leaf2', 'bamboo-leaf2.png', anchor_x='right')
		cls.load_sprite('top', 'bamboo-top.png', anchor_x=77, anchor_y=3)

	def get_parent_group(self, parent=None):
		return parent

	def create_sprites(self, batch=None, parent=None):
		self.load_resources()
		if batch:
			self.batch = batch
		else:
			self.batch = pyglet.graphics.Batch()
		self.foliage = {}

		tex = self.textures['piece']
		vertices = []
		tex_coords = []

		da = self.wobble_angle / self.height
		pos = self.pos
		step = Vec2(0, self.PIECE_HEIGHT).rotate(self.base_angle)
		radius = Vec2(self.RADIUS, 0).rotate(self.base_angle)

		for i in range(self.height + 1):
			vertices += list(pos - radius)
			vertices += list(pos + radius)
			radius *= self.THINNING
			tex_coords += [tex.tex_coords[0], (i + 1) * self.TEX_PERIOD, tex.tex_coords[3], (i + 1) * self.TEX_PERIOD]
			pos += step
			step = step.rotate(da)
			radius = radius.rotate(da) * self.THINNING

		parent_group = self.get_parent_group(parent)
		group = pyglet.sprite.SpriteGroup(self.textures['piece'], GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, parent=parent_group)
		self.vertex_list = self.batch.add((self.height + 1) * 2, GL_QUAD_STRIP, group, ('v2f', vertices), ('t2f', tex_coords))
	
		for i in range(self.height):
			prob = self.height - i
			if random.random() * prob < 1:
				l = random.choice(['leaf1-l', 'leaf2-l'])
				self.foliage.setdefault(i, []).append((1, pyglet.sprite.Sprite(self.graphics[l], x=self.pos.x, y=self.PIECE_HEIGHT * i + self.pos.y, batch=self.batch, group=parent_group)))
			if random.random() * prob < 1:
				l = random.choice(['leaf1-r', 'leaf2-r'])
				self.foliage.setdefault(i, []).append((-1, pyglet.sprite.Sprite(self.graphics[l], x=self.pos.x, y=self.PIECE_HEIGHT * i + self.pos.y, batch=self.batch, group=parent_group)))
		self.foliage.setdefault(self.height, []).append((0, pyglet.sprite.Sprite(self.graphics['top'], batch=self.batch, group=parent_group)))

	def set_trunk_vertex(self, i, v):
		x, y = v
		self.vertex_list.vertices[i * 2] = x
		self.vertex_list.vertices[i * 2 + 1] = y

	def compute_wobble(self):
		"""Generator for the vertex list. Iterate to give a sequence of Vec2 objects"""
		da = self.wobble_angle / self.height

		pos = self.pos
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
				a.v = apos - a.pos
				a.pos = apos
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

	def __eq__(self, ano):
		return self.__class__ == ano.__class__ and self.depth == ano.depth
		

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
		cls.load_directional_sprite('leaf1', 'bamboo-leaf1.png', anchor_x='right')
		cls.load_directional_sprite('leaf2', 'bamboo-leaf2.png', anchor_x='right')
		cls.load_sprite('top', 'bamboo-top.png', anchor_x=77, anchor_y=3)

	def on_spawn(self):
		self.RADIUS = random.random() ** 0.5 * 10 + 2
		self.wobble_angle = random.random() * 1 - 0.5
		self.compute_wobble()

	def get_parent_group(self, parent=None):
		return BackgroundGroup(self.shadow, parent=parent)

	def update(self):
		pass